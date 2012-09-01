from . import template

class handler(template.handler):
    def __init__(self, *args):
        self.NAME = "Block Action"
        self.HEADER = 0x36

    def getlength(self, roboclass, data):
        return 14
