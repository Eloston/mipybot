from . import template

class handler(template.handler):
    def __init__(self, *args):
        self.NAME = "Update Sign"
        self.HEADER = 0x82

    def getlength(self, roboclass, data):
        Length = roboclass.CONVERTER.INTEGER_LENGTH*2 + roboclass.CONVERTER.SHORT_LENGTH
        # Repeat 4 times below to cover all 4 lines
        Length += roboclass.CONVERTER.getstringdata(data, Length)['length'] + roboclass.CONVERTER.SHORT_LENGTH
        Length += roboclass.CONVERTER.getstringdata(data, Length)['length'] + roboclass.CONVERTER.SHORT_LENGTH
        Length += roboclass.CONVERTER.getstringdata(data, Length)['length'] + roboclass.CONVERTER.SHORT_LENGTH
        Length += roboclass.CONVERTER.getstringdata(data, Length)['length'] + roboclass.CONVERTER.SHORT_LENGTH
        return Length
