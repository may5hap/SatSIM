# -*- coding: utf-8 -*-
"""
@author: Hao Wang
@file:   node.py
"""
import random
from .rtable import Router
from .energy import EnergyModel
from .mobility import MobilityModel
from .utils import time2list
from datetime import datetime, timedelta


class Node:

    def __init__(self, net, name, tle, index):
        super(Node, self).__init__()
        self.net = net

        self.name = name
        self.tle = tle
        self.index = index

        self.mobile = MobilityModel()

        self.bmm = EnergyModel(power_type=2)

        self.router = Router()
        # self.netDevices = {}
        self.sending_queue = []
        self.receiving_queue = []

        self.localtime = datetime(2021, 5, 7, 12, 0, 0)

        # self.forwardingTime = 0
        self.mobile.cal_pos(self)

    def reset(self):
        self.localtime = datetime(2021, 5, 7, 12, 0, 0)
        self.mobile.reset()
        self.mobile.cal_pos(self)
        self.sending_queue.clear()
        self.receiving_queue.clear()
        self.bmm.reset()

    def update_time(self, netTime):
        self.localtime = max(self.localtime, netTime)

    def update(self, time):
        self.mobile.cal_pos(self, time2list(time))
        self.bmm.decrease_device_energy()
        if self.mobile.in_sunlit:
            self.bmm.increase_energy()

    def send(self, event, nexthop):
        channel = self.net.edges[self.name, nexthop]['e']
        txtime = event.packet.size / channel.cal_rate()
        propdelay = channel.cal_prop_delay()
        event.packet.time += timedelta(seconds=txtime + propdelay)
        event.packet.delay += (txtime + propdelay)
        self.bmm.decrease_tx_energy(txtime)
        # event.packet.cur_node = nexthop
        return txtime, propdelay

    def receive(self, event):
        event.packet.time += event.duration
        event.packet.delay += event.duration.total_seconds()
        self.bmm.decrease_rx_energy(event.duration.total_seconds())

    def lookup(self, event):
        nexthop = self.router.look_up(event.packet)
        self.bmm.decrease_rtable_lookup(event.packet.size)
        event.packet.time += event.duration
        event.packet.delay += event.duration.total_seconds()
        event.packet.ttl -= 1

        # 1、到终点了
        if event.packet.d_node == self.name:
            event.packet.arrive = 1
            # return None
        # 2、ttl小于等于0，丢包了
        elif event.packet.ttl <= 0:
            event.packet.drop = 1
            # return None
        # 3、放到发送队列，准备发到下一跳
        # self.sending_queue.put(packet)
        # return nexthop

    def init_routing_table(self, successors, out_degrees):
        out_degree = out_degrees[self.name]
        for i in range(66):
            self.router.routing_table[f"{i+1}"] = successors[random.randint(0, out_degree-1)]

    def update_routing_table(self, actions):
        for k, v in actions.items():
            self.router.routing_table[k] = v
