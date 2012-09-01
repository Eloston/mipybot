from . import template

class handler(template.handler):
    def __init__(self, *args):
        self.NAME = "Set Window Items"
        self.HEADER = 0x68

    def getlength(self, roboclass, data):
        Length = roboclass.CONVERTER.BYTE_LENGTH
        count = roboclass.CONVERTER.getshort(data, Length)
        print("count", count)
        Length += roboclass.CONVERTER.SHORT_LENGTH
        # Reading the slot
        parsed = 1 # Because when we enter the while loop, it would've already parsed one
        while parsed <= count:
            slotid = roboclass.CONVERTER.getshort(data, Length)
            Length += roboclass.CONVERTER.SHORT_LENGTH
            if slotid <= 0:
                parsed += 1
                continue
            Length += roboclass.CONVERTER.BYTE_LENGTH
            slotdatalength = roboclass.CONVERTER.getshort(data, Length)
            Length += roboclass.CONVERTER.SHORT_LENGTH
            if slotdatalength <= 0:
                parsed += 1
                continue
            Length += slotdatalength
            parsed += 1
        return Length
