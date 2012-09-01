from . import template

class handler(template.handler):
    def __init__(self, *args):
        self.NAME = "Player List Item"
        self.HEADER = 0xC9

    def getlength(self, roboclass, data):
        Length = roboclass.CONVERTER.getstringdata(data)['length']
        Length += roboclass.CONVERTER.SHORT_LENGTH*2 + roboclass.CONVERTER.BYTE_LENGTH
        return Length
