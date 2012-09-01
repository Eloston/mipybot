from . import template

class handler(template.handler):
    def __init__(self, *args):
        self.NAME = "Explosion"
        self.HEADER = 0x3C

    def getlength(self, roboclass, data):
        Length = roboclass.CONVERTER.DOUBLE_LENGTH*3 + roboclass.CONVERTER.FLOAT_LENGTH
        recordcount = roboclass.CONVERTER.getinteger(data, Length)
        Length += roboclass.CONVERTER.INTEGER_LENGTH + recordcount*3 + roboclass.CONVERTER.FLOAT_LENGTH*3
        return Length
