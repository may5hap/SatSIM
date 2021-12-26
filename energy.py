# -*- coding=utf-8 -*-
"""
@author: Hao Wang
"""
import math

Power_Type = {0: "External", 1: "Battery", 2: "Energy Harvesting"}


class EnergyHarvester:
    SOLAR_PANEL_AREA = 0.2 # m^2
    RADIATION = 1353        # Watts/(m^2)
    ETA = 0.19              # the efficiency solar ----> electricity
    ALPHA = math.pi/3               # the angle between the normal of the Solar Panel and sunlight


    def __init__(self):
        pass

    def harvest(self, time):
        return self.SOLAR_PANEL_AREA * self.RADIATION * self.ETA * math.cos(self.ALPHA) * time



class EnergyModel(object):
    P_TX = 10           # Watts
    P_RX = 7           # Watts

    E_INIT = 300000     # Joules
    E_MIN = 3000        # Joules  to operate

    # # idle discharge rate
    # P_IDLE = 100        # Watts
    #
    # Rx_RATE = 1e7       # the receive rate, a constant

    RTable_LOOKUP = 0.00001   # 0.00001 J/b

    P_0 = 20

    def __init__(self, power_type=2):
        self.power_type = power_type
        self.energy = self.E_INIT
        self.energy_consumption = 0
        self.havester = EnergyHarvester()

    def __repr__(self):
        return "<Power Type=%s, Energy=%d J>" % (Power_Type[self.power_type], self.energy)

    def reset(self):
        self.energy = self.E_INIT
        self.energy_consumption = 0

    def decrease_device_energy(self, time=1):
        energy_dec = self.P_0 * time
        self.energy -= energy_dec
        self.energy_consumption += energy_dec
        return energy_dec

    def decrease_tx_energy(self, tx_time):
        # energy consumption = Tx power * Tx time
        energy_dec = self.P_TX * tx_time
        if self.power_type != 0:
            self.energy -= energy_dec
        self.energy_consumption += energy_dec
        return energy_dec

    def decrease_rx_energy(self, rx_time):
        # energy consumption = Rx power * Rx time
        energy_dec = self.P_RX * rx_time
        if self.power_type != 0:
            self.energy -= energy_dec
        self.energy_consumption += energy_dec
        return energy_dec, rx_time

    def decrease_rtable_lookup(self, packet_size):
        energy_dec = packet_size * self.RTable_LOOKUP
        self.energy -= energy_dec
        self.energy_consumption += energy_dec
        return energy_dec

    def increase_energy(self, charging_time=1):
        if self.power_type == 2:  # Energy harvesting only
            self.energy += self.havester.harvest(charging_time)
            self.energy = min(self.energy, self.E_INIT)
        return self.energy

    def have_energy(self):
        if self.energy > self.E_MIN:
            return True
        return False

    @property
    def powerType(self):
        return self.power_type

    @powerType.setter
    def powerType(self, power_type):
        self.power_type = power_type
