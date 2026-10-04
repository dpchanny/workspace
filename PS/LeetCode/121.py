class Solution:
    def maxProfit(self, prices):
        max_profit = 0
        a = 0
        b = 0
        for i in range(len(prices)):
            if prices[i] < prices[a]:
                profit = prices[b] - prices[a]
                max_profit = max(max_profit, profit)
                a = i
                b = i
            if prices[i] > prices[b]:
                b = i
        profit = prices[b] - prices[a]
        max_profit = max(max_profit, profit)
        return max_profit
