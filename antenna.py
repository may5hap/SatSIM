r'''
Antenna. Every antenna has the following parts:
        D: the diameter in m
        Gt/Gr: the gain of transmitter/receiver antenna
'''

import math

light_speed = 3e8                 # in m/s


class Antenna:
    FREQUENCY = 23E9
    D = 0.5
    ETA = 0.65
    WAVE_LENGTH = light_speed / FREQUENCY
    GT = 4 * math.pi * pow(D, 2) / pow(WAVE_LENGTH, 2)  # antenna gain of transmitter
    GR = pow(math.pi * D / WAVE_LENGTH, 2) * ETA  # antenna gain of receiver

    def __init__(self):
        super(Antenna, self).__init__()
        pass
