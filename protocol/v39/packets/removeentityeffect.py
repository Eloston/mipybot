from . import template

class handler(template.handler):
    def __init__(self, *args):
        self.NAME = "Remove Entity Effect"
        self.HEADER = 0x2A

    def receive(self, roboclass):
        return 5
