r'''
    base class for generating packages
'''


class Packet:
    size = 12000
    cid = 1

    def __init__(self, s_node, d_node, generateTime):
        super(Packet, self).__init__()
        self.s_node = s_node
        self.d_node = d_node
        self.cur_node = s_node
        self.drop = 0
        self.arrive = 0
        self.delay = 0
        self.ttl = 16
        self.time = generateTime
        self.econ = 0
        self.id = self.__class__.cid
        self.__class__.cid += 1

    def is_expire(self):
        return self.ttl <= 0

    def __lt__(self, other):
        r"""
        主要定义在队列中的优先级（开始时间越小，优先级越高，如果开始时间相同，则比较结束时间）
        :param other: 其他的事件
        :return:
        """
        return self.time <= other.time
