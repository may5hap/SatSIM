# -*- coding: utf-8 -*-
"""
@author: Hao Wang
@file:   mobility.py
"""

from skyfield.api import Loader, EarthSatellite, wgs84
from skyfield_data import get_skyfield_data_path


load = Loader(get_skyfield_data_path())
planets = load('de421.bsp')
ts = load.timescale(builtin=False)


class MobilityModel:
    def __init__(self):
        self.pos = [1, 2, 3]        # 节点的位置，是一个三位坐标，比如[1,2,3]
        self.lat = 0                # 节点的纬度
        self.long = 0
        self.in_sunlit = 1          # 是否有太阳照射以吸收能量

    def cal_pos(self, node, t=(2021, 5, 7, 12, 0, 0)):
        sat = EarthSatellite(node.tle[0], node.tle[1], node.name, ts)
        t1 = ts.utc(t[0], t[1], t[2], t[3], t[4], t[5])
        geocentric = sat.at(t1)
        self.pos = geocentric.position.m
        subpoint = wgs84.subpoint(geocentric)
        self.lat = subpoint.latitude.degrees
        self.long = subpoint.longitude.degrees
        self.in_sunlit = 1 if sat.at(t1).is_sunlit(planets) else 0

    def reset(self):
        self.pos = [1, 2, 3]
        self.lat = 0
        self.long = 0
        self.in_sunlit = 1
