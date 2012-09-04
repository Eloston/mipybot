from . import template

class handler(template.handler):
    def __init__(self, *args):
        self.NAME = "Entity Velocity"
        self.HEADER = 0x1C

    def receive(self, roboclass):
        return 10
