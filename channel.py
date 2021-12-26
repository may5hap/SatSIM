r'''
    written by Hao Wang in 6.1.2021
    a channel is a edge that connects two satellite nodes
    1、 source node and destination node
        src_node
        dst_node
    2、 bandwidth and frequency
        the bandwidth that can be used, im Hz
        the carrier frequency, in Hz
        the wave_length, in m
        the rate, in bps
    3、 length
        the length of channel of the distance of src_node and destination node
    4、 noise
        the noise power that signal suffer from
    5、 type
        which type is the channel, intra-plane or inter-plane
'''

import math
from .antenna import Antenna

a = 1.38e-23
light_speed = 3e8  # in m/s


class Channel:
    polar_lat = 80                              # 极区的最低纬度
    P_TX = 10
    bandwidth = 40e5                            # 信道带宽
    carrier_frequency = 23e9                    # 载波频率，ka波段

    def __init__(self, type, src_node, dst_node):
        super(Channel, self).__init__()
        ############### 1、 source node and destination node
        self.src_node = src_node
        self.dst_node = dst_node

        ############### 2、 length
        self.length = 0

        ############### 3、 bandwidth and frequency
        self.wave_length = light_speed / self.carrier_frequency
        self.rate = 0

        ############### 4、 noise
        ############### noise power can be calculated as: N = taB, t is the temperature, a is constant, B is the bandwidth
        ############### here we use t = 300K, B is the same as the channel bandwidth
        self.noise_power = 1000 * a * self.bandwidth

        ############### 5、 type
        self.type = type  # 2 for inter-plane ISL and 1 for intra-plane ISL

        self.cal_length()
        # print(self.length)
        self.cal_rate()

    ############# think about what we need to get from channel
    ############# 1、 the propagation delay
    ############# 2、 the transmission delay

    def cal_prop_delay(self):
        ############### the propagation delay can be calculated as: prop_delay = self.length / light_speed
        prop_delay = self.length / light_speed
        return prop_delay

    def cal_length(self):
        self.length = math.sqrt(sum([pow(self.src_node.mobile.pos[0] - self.dst_node.mobile.pos[0], 2),
                                     pow(self.src_node.mobile.pos[1] - self.dst_node.mobile.pos[1], 2),
                                     pow(self.src_node.mobile.pos[2] - self.dst_node.mobile.pos[2], 2)]))
        return self.length

    def cal_trans_delay(self, package):
        ############### the transmission delay is related to the rate and package size: trand_delay = size / rate
        self.cal_rate()
        trans_delay = package.size / self.rate
        return trans_delay

    def cal_rate(self):
        ############### the rate is related to the bandwidth and SNR
        # print(f'链路长度：{self.length}')
        loss = pow(4 * math.pi * self.length / self.wave_length, 2)
        P_r = self.P_TX * Antenna.GT * Antenna.GR / loss
        # print(f'接收功率：{P_r}')
        self.noise_power = 1000 * a * self.bandwidth
        SNR = P_r / self.noise_power
        self.rate = self.bandwidth * math.log2(1 + SNR)         # in bps
        return self.rate

    def update(self):
        self.cal_length()
        self.cal_rate()
