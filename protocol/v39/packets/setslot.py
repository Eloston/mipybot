from . import template

class handler(template.handler):
    def __init__(self, *args):
        self.NAME = "Set Slot"
        self.HEADER = 0x67

    def getlength(self, roboclass, data):
        Length = roboclass.CONVERTER.BYTE_LENGTH + roboclass.CONVERTER.SHORT_LENGTH
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
