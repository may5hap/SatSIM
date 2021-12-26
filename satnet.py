# -*- coding: utf-8 -*-
"""
@author: Hao Wang
"""
import csv
import math
from networkx import DiGraph
import gym
import torch as th
from .node import Node
from .channel import Channel
import networkx as nx
from .packet import Packet
from datetime import datetime, timedelta
from .utils import check_edge_can_exist, find_src, find_dst
from .cbr import Cbr
import random
from .eventList import EventList
from .event import MakeEvent
from .log import Log

log = Log()
decision_interval = 10
tlefilepath = "/home/eini001/EventDriven/Distributed/SatSim/envs/iridium_tle_sorted.txt"
testLogDir = '/home/eini001/satenvsimTest/algorithms/TestResults/model4/seen/DGRL/'
test = None  # or "DGRL"

if test is not None:
    readout = 'min'
    testPacketLogPath = testLogDir + readout + f'/packet-{test}-{decision_interval}-' + readout + '.csv'
    # print(testPacketLogPath)
    # testPacketLogPath = testLogDir + test + '/' + f'packet-{test}-{decision_interval}.csv'
    with open(testPacketLogPath, 'a', newline="") as f:
        headers = ['PacketId', 'Delay', 'EnergyCon', 'Drop']
        writer = csv.writer(f)
        writer.writerow(headers)


class SatNet(DiGraph):
    start_time = (2021, 5, 7, 12, 0, 0)  # 仿真开始时间
    end_time = (2021, 5, 7, 13, 0, 0)  # 仿真结束时间
    source_node = None  # 数据源节点
    destination_node = None  # 数据目的节点
    packet_size = 12000  # 数据包平均长度1500字节
    bandwidth = 40e5  # 信道带宽
    carrier_frequency = 23e9  # 载波频率，ka波段
    num_satellite = 66  # 卫星数量
    no_seam_isl = 1  # 是否考虑跨平面ISL
    no_polar_isl = 1  # 是否考虑极区的跨平面ISL
    polar_lat = 80  # 极区的最低纬度
    decision_interval = decision_interval  # 路由决策周期
    packet_generation_interval = 0.02  # 数据包的生成间隔
    init_num_packet = random.randint(1, 10)  # 初始在源节点生成的包的个数
    ground1 = [115, 40]
    ground2 = [-50, -20]
    r"""
    Gym envs for satellite networks

    Observations (states) are: the networkx directed graph composed of the satellite nodes and the link edges
    Actions are: a routing decision

    Actions are made for each user-defined seconds (time-interval).
    Actions will be executed, i.e., forwarding some packets with the selected routing path

    Rewards are: the energy efficiency, delay and residual energy... It is based on your model
    """

    def __init__(self):
        DiGraph.__init__(self)
        self.time = datetime(self.start_time[0], self.start_time[1], self.start_time[2], self.start_time[3],
                             self.start_time[4], self.start_time[5])
        self.eventlist = EventList()

        self.init_net(tlefilepath)
        self.source_node = self.cal_src()
        self.destination_node = self.cal_dst()

    def init_net(self, tlefilepath):
        r"""

        :param tlefilepath: the file-path for TLE data
        :return: returns nothing, but to initialize the network environment
        """
        self.add_nodes(tlefilepath)
        self.add_edges()

    def add_nodes(self, tlefilepath):
        r"""
        this function is used to create the satellite nodes,
        generally the satellite nodes should not be created repeatedly
        :return: it returns nothings, but the satellite nodes will be created

        note that, the TLE data is stored at file 'iridiun_tle_sorted.txt', you should not change the information in it.
        if you want to expand the network scale, you can re-download the TLE data from https://celestrak.com

        we have defined the index of every satellite, such as [1,2] means the first plane and the second satellite
        """
        with open(tlefilepath, 'r') as f:
            for i in range(self.num_satellite):
                name = f.readline().strip()
                index = f.readline().strip()
                line1 = f.readline().strip()
                line2 = f.readline().strip()
                index = list(map(int, index.split(',')))
                node = Node(self, name, (line1, line2), index)
                DiGraph.add_node(self, name, n=node)

    def add_edges(self):
        for n1 in self.nodes:
            for n2 in self.nodes:
                if n1 != n2:
                    # add intra-plane isl
                    if self.nodes[n1]['n'].index[0] == self.nodes[n2]['n'].index[0]:
                        if abs(self.nodes[n1]['n'].index[1] - self.nodes[n2]['n'].index[1]) == 1 or \
                                abs(self.nodes[n1]['n'].index[1] - self.nodes[n2]['n'].index[1]) == 10:
                            channel1 = Channel(1, self.nodes[n1]['n'], self.nodes[n2]['n'])
                            DiGraph.add_edge(self, n1, n2, weight=1, e=channel1)
                    # add inter-plane isl
                    else:
                        # check the latitude
                        if abs(self.nodes[n1]['n'].mobile.lat) > self.polar_lat or abs(
                                self.nodes[n2]['n'].mobile.lat) > self.polar_lat:
                            continue
                        else:
                            if abs(self.nodes[n1]['n'].index[0] - self.nodes[n2]['n'].index[0]) == 1:
                                if self.nodes[n1]['n'].index[1] == self.nodes[n2]['n'].index[1]:
                                    channel1 = Channel(2, self.nodes[n1]['n'], self.nodes[n2]['n'])
                                    DiGraph.add_edge(self, n1, n2, weight=2, e=channel1)

    def cal_src(self):
        return find_src(self, self.ground1)

    def cal_dst(self):
        return find_dst(self, self.ground2)

    def step(self, actions=None, time=10):
        r"""
        :param action: the selected routing path
        :return: the next state after forwarding packets with the selected routing path
        """
        for node in self.nodes:
            self.nodes[node]['n'].update_routing_table(actions[node])
            # print(self.nodes[node]['n'].router.routing_table)
        reward = self.forwarding()
        # uncomment the following lines for constructing action space
        # self.time += timedelta(seconds=time)
        # self.update_per_second(self.time)
        return self#, reward, self.done, {}

    def init_traffic(self):
        """
        初始化流量，由于数据包和事件都是按事件的优先级处理，故把一开始的数据包发送时间设置的有一点点区别，不完全一致，
        否则从事件队列取事件和从发送队列取数据包会不一致
        :return:
        """
        for i in range(self.init_num_packet):
            packet = Cbr.generate_packet(self.source_node, self.destination_node, 1, self.time+timedelta(seconds=i/10000))
            self.eventlist.Q.put(
                MakeEvent(self.nodes[self.source_node]['n'], self.time+timedelta(seconds=i/10000), 'send', packet,
                          timedelta(seconds=0)))
        print(f'初始化流量，生成了{self.init_num_packet}个数据包')

    def generate_packet(self, generateTime, num=1):
        """
        在某个时间，源节点生成一个数据包到发送队列中，并将对应的发送事件插入事件队列中
        :param generateTime: 生成数据包的时间
        :param num: 生成数据包的数量，默认一个，暂不支持多个
        :return:
        """
        packet = Cbr.generate_packet(self.source_node, self.destination_node, num, generateTime)
        # self.nodes[self.source_node]['n'].sending_queue.append(packet)
        self.eventlist.Q.put(
            MakeEvent(self.nodes[self.source_node]['n'], generateTime, 'send', packet, timedelta(seconds=0)))

    def generate_timed_events(self):
        """
        这个函数用于提前生成好定时事件（每隔self.packet_generation_interval事件生成一个数据包），在转发前生成这些事件的优势是：
        有可能极端前况下，事件全部处理完了，但是还没到结束的事件，此时已经没有事件可以处理而出现死循环
        :return:
        """
        for i in range(1, int(self.decision_interval/self.packet_generation_interval) + 1):
            time = self.time + timedelta(seconds=i*self.packet_generation_interval)
            self.generate_packet(time)

    def forwarding(self):
        """
        转发self.decision_interval的过程，利用事件驱动，从事件队列中不停的取事件来执行，直到取出的事件开始执行时间超过了endtime
        :return:
        """
        endtime = self.time + timedelta(seconds=self.decision_interval)
        self.generate_timed_events()
        nextUpdateTime = self.time + timedelta(seconds=1)
        while not self.eventlist.Q.empty() and self.time < endtime:
            # print(self.time)
            event = self.eventlist.Q.get()
            if event.startTime < endtime:
                log.info(event)
                ret = event.handle()
                if ret is not None:
                    self.eventlist.Q.put(ret)
                    if event.what == 'receive' or event.what == 'lookup' or (event.what == 'send' and ret.what ==
                                                                             'receive'):
                        self.time = ret.startTime
                if ret is None:
                    self.time = event.packet.time
                # if not (ret is not None and event.what == 'send' and ret.what == 'send'):
                #     self.time = event.packet.time
                # self.update_nodes_time()
                if self.time >= nextUpdateTime:
                    self.update_per_second(nextUpdateTime)
                    nextUpdateTime += timedelta(seconds=1)
            else:
                self.eventlist.Q.put(event)
                break
        self.time = endtime
        self.update_per_second(self.time)
        self.source_node = self.cal_src()
        self.destination_node = self.cal_dst()

    def update_nodes_time(self):
        for node in self.nodes:
            self.nodes[node]['n'].update_time(self.time)

    # def reward_func(self):
    #     reward = 0
    #     a = len(self.packet_drop) / (len(self.packet_drop) + len(self.packetsArrived))
    #     penalty = -100
    #     w1, w2 = 1, 3
    #     x1, x2 = 0.1, 100
    #     for packet in self.packetsArrived:
    #         # print(f'消耗能量：{packet.econ},时延：{packet.time}')
    #         eff = x1 * packet.size / packet.econ - x2 * packet.time
    #         reward += w1 * eff
    #     if len(self.packetsArrived) != 0:
    #         reward /= len(self.packetsArrived)
    #     reward += w2 * a * penalty
    #     # print(f'{self.time}的上一个时刻奖励：{reward}')
    #     return reward

    def update_per_second(self, updateTime):
        # print(f'现在时间：{self.time}，更新网络拓扑（节点位置、连接情况等）')
        for node in self.nodes:
            self.nodes[node]['n'].update(updateTime)
        self.recalculate_edges()

    def reset(self):
        r"""
        used for resetting the environment, it will be called when a episode ends
        :return: returns the networkx graph of initial state
        """
        # self.done = 0
        self.time = datetime(self.start_time[0], self.start_time[1], self.start_time[2], self.start_time[3],
                             self.start_time[4], self.start_time[5])
        self.eventlist = EventList()
        for node in self.nodes:
            self.nodes[node]['n'].reset()
        self.recalculate_edges()
        self.source_node = self.cal_src()
        self.destination_node = self.cal_dst()
        for node in self.nodes:
            self.nodes[node]['n'].init_routing_table(list(self.successors(node)), self.out_degree)
        self.init_traffic()
        return self

    def recalculate_edges(self):
        for edge in list(self.edges):
            # print(edge[0], edge[1])
            if self.edges[edge]['e'].type == 1:
                self.edges[edge]['e'].update()
            if self.edges[edge]['e'].type == 2:
                if check_edge_can_exist(self, edge):
                    self.edges[edge]['e'].update()
                elif self.has_edge(edge[0], edge[1]):
                    # print('drop:', edge[0], edge[1])
                    self.remove_edge(edge[0], edge[1])
        for n1 in self.nodes:
            for n2 in self.nodes:
                if not self.has_edge(n1, n2) and abs(self.nodes[n1]['n'].mobile.lat) <= self.polar_lat and \
                        abs(self.nodes[n2]['n'].mobile.lat) <= self.polar_lat:
                    # add inter-plane isl
                    # check the latitude
                    if abs(self.nodes[n1]['n'].index[0] - self.nodes[n2]['n'].index[0]) == 1:
                        if self.nodes[n1]['n'].index[1] == self.nodes[n2]['n'].index[1]:
                            channel = Channel(2, self.nodes[n1]['n'], self.nodes[n2]['n'])
                            DiGraph.add_edge(self, n1, n2, weight=2, e=channel)

    def close(self):
        pass

    # in order to compare the performance of different algorithms, more functions are designed to record some information
    def writePacketCSV(self, packetCSV):
        with open(packetCSV, 'a', newline="") as f:
            writer = csv.writer(f)
            for packet in self.packetsArrived:
                writer.writerow([packet.id, packet.time, packet.econ, packet.drop])
            for packet in self.packet_drop:
                writer.writerow([packet.id, packet.time, packet.econ, packet.drop])
