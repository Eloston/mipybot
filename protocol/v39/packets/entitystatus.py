from . import template

class handler(template.handler):
    def __init__(self, *args):
        self.NAME = "Entity Status"
        self.HEADER = 0x26

    def receive(self, roboclass):
        return 5
