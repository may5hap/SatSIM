# -*- coding: utf-8 -*-
"""
@author: Hao Wang
@file:   log.py
"""
import datetime

"""
主要用来实现日志功能，查看仿真过程
"""
logdir = '/home/eini001/EventDriven/Distributed/SatSim/logs/'


class Log:
    def __init__(self):
        self.logdir = logdir
        self.file = str(datetime.datetime.now())
        self.logfile = self.logdir + self.file + '.txt'
        with open(self.logfile, 'a') as f:
            f.write('The start time' + '\t' + 'The none id' + '\t' + 'The action' + '\t' + 'The packet id' + '\n')

    def info(self, event):
        with open(self.logfile, 'a') as f:
            f.write(
                str(event.startTime) + '\t' + event.node.name + '\t' + event.what + '\t' + str(event.packet.id) + '\n')
