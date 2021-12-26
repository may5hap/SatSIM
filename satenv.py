# -*- coding: utf-8 -*-
"""
@author: Hao Wang
@file:   satenv.py
"""

import gym
from gym import spaces


class SatEnv(gym.Env):
    metadata = {
        'render.modes': ['human', 'rgb_array']
    }
    def __init__(self, satnet):
        super(SatEnv, self).__init__()
        self.satnet = satnet
