from . import template

class handler(template.handler):
    def __init__(self, *args):
        self.NAME = "Spawn Dropped Item"
        self.HEADER = 0x15

    def getlength(self, roboclass, data):
        return roboclass.CONVERTER.INTEGER_LENGTH*4 + roboclass.CONVERTER.SHORT_LENGTH*2 + roboclass.CONVERTER.BYTE_LENGTH*4
