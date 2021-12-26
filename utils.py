# -*- coding=utf-8 -*-
"""
@author: Hao Wang
"""
import math

polar_lat = 80


def check_edge_can_exist(net, edge):
    if abs(net.nodes[edge[0]]['n'].mobile.lat) > polar_lat or abs(net.nodes[edge[1]]['n'].mobile.lat) > polar_lat:
        return False
    return True


def find_src(net, ground1):
    mindis = 1e10
    ret = None
    for node in net.nodes:
        dis = math.sqrt(pow(net.nodes[node]['n'].mobile.long-ground1[0], 2) +
                        pow(net.nodes[node]['n'].mobile.lat-ground1[1], 2))
        if dis < mindis:
            ret = node
            mindis = dis
    return ret


def find_dst(net, ground2):
    mindis = 1e10
    ret = None
    for node in net.nodes:
        dis = math.sqrt(pow(net.nodes[node]['n'].mobile.long-ground2[0], 2) +
                        pow(net.nodes[node]['n'].mobile.lat-ground2[1], 2))
        if dis < mindis:
            ret = node
            mindis = dis
    return ret


def time2list(time):
    l = []
    l.append(time.year)
    l.append(time.month)
    l.append(time.day)
    l.append(time.hour)
    l.append(time.minute)
    l.append(time.second)
    return l


class Info:
    def __init__(self):
        self.delay = 0
        self.energy_con = 0
        self.drop = 0
        self.nextHop = None
