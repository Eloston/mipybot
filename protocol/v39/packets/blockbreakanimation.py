from . import template

class handler(template.handler):
    def __init__(self, *args):
        self.NAME = "Block Break Animation"
        self.HEADER = 0x37

    def receive(self, roboclass):
        return 17
