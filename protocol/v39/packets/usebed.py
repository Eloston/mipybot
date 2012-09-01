from . import template

class handler(template.handler):
    def __init__(self, *args):
        self.NAME = "Use Bed"
        self.HEADER = 0x11

    def getlength(self, roboclass, data):
        return roboclass.CONVERTER.INTEGER_LENGTH + roboclass.CONVERTER.BYTE_LENGTH + roboclass.CONVERTER.INTEGER_LENGTH + roboclass.CONVERTER.BYTE_LENGTH + roboclass.CONVERTER.INTEGER_LENGTH
