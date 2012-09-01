from . import template

class handler(template.handler):
    def __init__(self, *args):
        self.NAME = "Close Window"
        self.HEADER = 0x65

    def getlength(self, roboclass, data):
        return 1
