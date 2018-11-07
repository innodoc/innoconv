""" Demo for A module"""

from innoconv.modules import AbstractModule


class Demo(AbstractModule):
    """a Demo Module"""

    def __init__(self):
        super(Demo, self).__init__()
        self.events.extend([])
