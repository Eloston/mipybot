from . import template

class handler(template.handler):
    def __init__(self, *args):
        self.NAME = "Spawn Painting"
        self.HEADER = 0x19

    def getlength(self, roboclass, data):
        Length = roboclass.CONVERTER.INTEGER_LENGTH
        Length += roboclass.CONVERTER.getstringdata(data, Length)['length']
        Length += roboclass.CONVERTER.SHORT_LENGTH
        Length += roboclass.CONVERTER.INTEGER_LENGTH*4
        return Length
