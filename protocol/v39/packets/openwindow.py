from . import template

class handler(template.handler):
    def __init__(self, *args):
        self.NAME = "Open Window"
        self.HEADER = 0x64

    def getlength(self, roboclass, data):
        Length = roboclass.CONVERTER.BYTE_LENGTH*2
        Length += roboclass.CONVERTER.getstringdata(data, Length)['length'] + roboclass.CONVERTER.SHORT_LENGTH
        Length += roboclass.CONVERTER.BYTE_LENGTH
        return Length
