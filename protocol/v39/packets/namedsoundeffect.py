from . import template

class handler(template.handler):
    def __init__(self, *args):
        self.NAME = "Named Sound Effect"
        self.HEADER = 0x3E

    def getlength(self, roboclass, data):
        Length = 0
        soundnamelength = roboclass.CONVERTER.getstringdata(data)['length']
        Length += roboclass.CONVERTER.SHORT_LENGTH + soundnamelength + roboclass.CONVERTER.INTEGER_LENGTH*3 + roboclass.CONVERTER.FLOAT_LENGTH + roboclass.CONVERTER.BYTE_LENGTH
        return Length
