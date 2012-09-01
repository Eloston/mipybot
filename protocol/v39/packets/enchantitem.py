from . import template

class handler(template.handler):
    def __init__(self, *args):
        self.NAME = "Enchant Item"
        self.HEADER = 0x6C

    def getlength(self, roboclass, data):
        return 2
