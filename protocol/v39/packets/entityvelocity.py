from . import template

class handler(template.handler):
    def __init__(self, *args):
        self.NAME = "Entity Velocity"
        self.HEADER = 0x1C

    def getlength(self, roboclass, data):
        return 10
