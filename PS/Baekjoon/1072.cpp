#include <iostream>

using namespace std;

long long int x, y, l, r, m, z;

int main(void) {
  cin >> x >> y;
  z = y * 100 / x;
  if (z + 1 > 99) {
    cout << -1;
    return 0;
  }
  l = 1;
  r = 1'000'000'001;
  while (l != r) {
    m = (l + r) / 2;
    if ((y + m) * 100 / (x + m) - z)
      r = m;
    else
      l = m + 1;
  }

  cout << l;
}