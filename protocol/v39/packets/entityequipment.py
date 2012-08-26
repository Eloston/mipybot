from . import template

class handler(template.handler):
    def __init__(self, *args):
        self.NAME = "Entity Equipment"
        self.HEADER = 0x05

    def getlength(self, roboclass, data):
        return 10
