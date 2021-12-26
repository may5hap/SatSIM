# -*- coding: utf-8 -*-
"""
@author: Hao Wang
@file:   cbr.py
"""

from .packet import Packet


class Cbr:
    GENERATE_INTERVAL = 0.02            # in second

    def __init__(self):
        pass

    @staticmethod
    def generate_packet(src, dst, num=1, generateTime=0.0):
        assert num == 1
        return Packet(src, dst, generateTime)
