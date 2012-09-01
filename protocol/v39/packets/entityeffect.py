from . import template

class handler(template.handler):
    def __init__(self, *args):
        self.NAME = "Entity Effect"
        self.HEADER = 0x29

    def getlength(self, roboclass, data):
        return 8
