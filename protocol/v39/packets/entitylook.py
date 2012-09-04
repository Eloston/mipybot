from . import template

class handler(template.handler):
    def __init__(self, *args):
        self.NAME = "Entity Look"
        self.HEADER = 0x20

    def receive(self, roboclass):
        return 6
