from . import template

class handler(template.handler):
    def __init__(self, *args):
        self.NAME = "Entity Relative Move"
        self.HEADER = 0x1F

    def getlength(self, roboclass, data):
        return 7
