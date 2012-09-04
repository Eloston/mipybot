from . import template

class handler(template.handler):
    def __init__(self, *args):
        self.NAME = "Entity Head Look"
        self.HEADER = 0x23

    def receive(self, roboclass):
        return 5
