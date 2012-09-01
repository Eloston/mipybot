from . import template

class handler(template.handler):
    def __init__(self, *args):
        self.NAME = "Block Change"
        self.HEADER = 0x35

    def getlength(self, roboclass, data):
        return 12
