r'''
    this class defines a basic router and it's look-up function
'''
import random


class Router():
    def __init__(self):
        super(Router, self).__init__()
        self.routing_table = {}

    def look_up(self, package):
        if package.d_node in self.routing_table.keys():
            return self.routing_table[package.d_node]
        else:
            return None

    def update_(self, path):
        pass


