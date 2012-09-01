from . import template

class handler(template.handler):
    def __init__(self, *args):
        self.NAME = "Spawn Object/Vehicle"
        self.HEADER = 0x17

    def getlength(self, roboclass, data):
        Length = roboclass.CONVERTER.INTEGER_LENGTH*4 + roboclass.CONVERTER.BYTE_LENGTH
        objectdata = roboclass.CONVERTER.getinteger(data, Length)
        Length += roboclass.CONVERTER.INTEGER_LENGTH
        if objectdata > 0:
            Length += roboclass.CONVERTER.SHORT_LENGTH*3
        return Length
