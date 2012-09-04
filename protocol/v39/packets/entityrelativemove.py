from . import template

class handler(template.handler):
    def __init__(self, *args):
        self.NAME = "Entity Relative Move"
        self.HEADER = 0x1F

    def receive(self, roboclass):
        return 7
