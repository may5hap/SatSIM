# -*- coding: utf-8 -*-
"""
@author: Hao Wang
@file:   event.py
"""
r"""
事件驱动的卫星网络仿真
事件可以定义为：
    1、某个节点的发包
    2、某个节点的收包
    3、某个节点的丢包
    4、查路由信息
"""
from datetime import datetime, timedelta


def MakeEvent(node, startTime, what, packet, duration):
    event = Event(node, startTime, what, packet, duration)
    return event


class Event:
    def __init__(self, node, startTime, what, packet, duration):
        """
        初始化，必须给定事件的开始时间、持续时间，以及必须的其他信息，比如某个节点，发包还是收包等
        :param startTime: 开始时间
        :param duration: 持续时间
        :param extraInfo: 必要的额外信息
        """
        self.node = node
        self.startTime = startTime
        self.what = what
        self.packet = packet
        self.duration = duration
        self.endTime = self.startTime + self.duration

    def handle(self):
        """
        处理事件
        :return:
        """
        if self.what == 'send':
            nexthop = self.node.router.look_up(self.packet)
            if not self.node.net.has_edge(self.node.name, nexthop):
                # print('暂时没有到下一跳的链路')
                self.packet.time += timedelta(seconds=1)
                self.packet.delay += 1.0
                # print('the start time and the packet time:', self.startTime, self.packet.time)
                return MakeEvent(self.node, self.packet.time, 'send', self.packet, timedelta(seconds=0))
            txtime, proptime = self.node.send(self, nexthop)
            return MakeEvent(self.node.net.nodes[nexthop]['n'], self.packet.time,
                             'receive', self.packet, timedelta(seconds=txtime))
        elif self.what == 'receive':
            self.node.receive(self)
            return MakeEvent(self.node, self.packet.time, 'lookup', self.packet, timedelta(seconds=0.001))
        elif self.what == 'lookup':
            self.node.lookup(self)
            if self.packet.drop == 1:
                return None
            elif self.packet.arrive == 1:
                return None
            else:
                return MakeEvent(self.node, self.packet.time, 'send', self.packet, timedelta(seconds=0))

    def __lt__(self, other):
        r"""
        主要定义在队列中的优先级（开始时间越小，优先级越高，如果开始时间相同，则比较结束时间）
        :param other: 其他的事件
        :return:
        """
        return self.startTime < other.startTime or self.endTime < other.endTime
