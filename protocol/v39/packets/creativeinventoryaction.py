from . import template

class handler(template.handler):
    def __init__(self, *args):
        self.NAME = "Creative Inventory Action"
        self.HEADER = 0x6B

    def getlength(self, roboclass, data):
        Length = roboclass.CONVERTER.SHORT_LENGTH
        # Reading the slot
        slotid = roboclass.CONVERTER.getshort(data, Length)
        Length += roboclass.CONVERTER.SHORT_LENGTH
        if slotid == -1:
            return Length
        Length += roboclass.CONVERTER.BYTE_LENGTH
        slotdatalength = roboclass.CONVERTER.getshort(data, Length)
        Length += roboclass.CONVERTER.SHORT_LENGTH
        if slotdatalength == -1:
            return Length
        Length += slotdatalength
        return Length
