# -*- coding: utf-8 -*-
"""
@author: Hao Wang
@file:   eventList.py
"""
r"""
事件队列：
    事件队列主要用来保存事件，事情是按照开始执行的事件进行排序，i.e.,优先级队列
"""

from queue import PriorityQueue as PQ


class EventList:
    def __init__(self):
        self.Q = PQ()
