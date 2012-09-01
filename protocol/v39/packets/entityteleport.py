from . import template

class handler(template.handler):
    def __init__(self, *args):
        self.NAME = "Entity Teleport"
        self.HEADER = 0x22

    def getlength(self, roboclass, data):
        return 18
