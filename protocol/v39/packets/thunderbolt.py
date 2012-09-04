from . import template

class handler(template.handler):
    def __init__(self, *args):
        self.NAME = "Thunderbolt"
        self.HEADER = 0x47

    def receive(self, roboclass):
        return 17
