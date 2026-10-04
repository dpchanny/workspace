"""Print an image as terminal ASCII art.

Examples:
    python ascii_art.py photo.jpg
    python ascii_art.py photo.jpg --fit height --chars "@%#*+=-:. "
    python ascii_art.py photo.jpg --width 100 --fit width
"""

from __future__ import annotations

import argparse
import shutil
import sys
import time
from pathlib import Path

from PIL import Image, ImageOps

DEFAULT_CHARS = "@%#*+=-:. "


def terminal_size() -> tuple[int, int]:
    """Return usable terminal columns and rows, with conservative fallbacks."""
    size = shutil.get_terminal_size(fallback=(80, 24))
    return max(1, size.columns), max(1, size.lines)


def fit_dimensions(
    image: Image.Image, columns: int, rows: int, mode: str
) -> tuple[int, int]:
    """Calculate output dimensions while compensating for tall terminal cells."""
    source_width, source_height = image.size
    aspect = source_width / source_height

    # A terminal character is normally about twice as tall as it is wide.
    cell_aspect = 0.5
    if mode == "width":
        width = columns
        height = max(1, round(width / aspect * cell_aspect))
    elif mode == "height":
        height = rows
        width = max(1, round(height * aspect / cell_aspect))
    else:  # auto: use whichever dimension reaches its boundary first.
        width_from_columns = columns
        height_from_columns = max(1, round(width_from_columns / aspect * cell_aspect))
        height_from_rows = rows
        width_from_rows = max(1, round(height_from_rows * aspect / cell_aspect))
        if height_from_columns <= rows:
            width, height = width_from_columns, height_from_columns
        else:
            width, height = width_from_rows, height_from_rows

    return max(1, width), max(1, height)


def render(image: Image.Image, width: int, height: int, chars: str) -> str:
    """Resize and convert an image into luminance-based ASCII characters."""
    gray = ImageOps.grayscale(image).resize((width, height), Image.Resampling.LANCZOS)
    palette = chars
    last_index = len(palette) - 1
    pixels = list(gray.getdata())
    return "\n".join(
        "".join(
            palette[pixel * last_index // 255]
            for pixel in pixels[offset : offset + width]
        )
        for offset in range(0, width * height, width)
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Render an image as terminal ASCII art."
    )
    parser.add_argument("image", type=Path, help="path to the input image")
    parser.add_argument(
        "--fit",
        choices=("auto", "width", "height"),
        default="auto",
        help="fit to terminal width, height, or whichever is reached first (default: auto)",
    )
    parser.add_argument(
        "--chars", default=DEFAULT_CHARS, help="characters from dark to light"
    )
    parser.add_argument("--width", type=int, help="override terminal width in columns")
    parser.add_argument("--height", type=int, help="override terminal height in rows")
    parser.add_argument(
        "--watch",
        action="store_true",
        help="re-render when the terminal is resized (press Ctrl-C to stop)",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if not args.chars:
        raise SystemExit("--chars must contain at least one character")
    if not args.image.is_file():
        raise SystemExit(f"image not found: {args.image}")

    try:
        # Apply EXIF orientation before converting to RGB. Many phone cameras
        # store the rotation in metadata instead of rotating the pixel data.
        image = ImageOps.exif_transpose(Image.open(args.image)).convert("RGB")
    except Exception as exc:
        raise SystemExit(f"could not open image: {exc}") from exc

    try:
        previous_size = None
        while True:
            columns, rows = terminal_size()
            columns = args.width or columns
            rows = args.height or max(1, rows - 1)  # reserve one line for the prompt
            size = (columns, rows)
            if size != previous_size:
                output_width, output_height = fit_dimensions(
                    image, columns, rows, args.fit
                )
                art = render(image, output_width, output_height, args.chars)
                sys.stdout.write("\x1b[2J\x1b[H" if args.watch else "")
                sys.stdout.write(art + "\n")
                sys.stdout.flush()
                previous_size = size
            if not args.watch:
                break
            time.sleep(0.25)
    except KeyboardInterrupt:
        return 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
