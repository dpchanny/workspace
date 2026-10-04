class Solution:
    def smallerNumbersThanCurrent(self, nums):
        size = len(nums)
        counts = []
        for i in range(size):
            count = 0
            for j in range(size):
                if i == j:
                    continue
                if nums[i] > nums[j]:
                    count += 1
            counts.append(count)
        return counts
