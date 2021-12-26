# _*_ coding: utf-8 _*_
"""
@author: Hao Wang
"""

import heapq


class PriorityQueue:
    def __init__(self):
        self.queue = []
        heapq.heapify(self.queue)

    def get(self):
        return heapq.heappop(self.queue)

    def put(self, event):
        heapq.heappush(self.queue, (event.startTime, event))

    def empty(self):
        return len(self.queue) == 0