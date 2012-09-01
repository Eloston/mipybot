from . import template

class handler(template.handler):
    def __init__(self, *args):
        self.NAME = "Map Chunk Bulk"
        self.HEADER = 0x38

    def getlength(self, roboclass, data):
        chunkcount = roboclass.CONVERTER.getshort(data)
        Length = roboclass.CONVERTER.SHORT_LENGTH
        chunkdatasize = roboclass.CONVERTER.getinteger(data, Length)
        Length += roboclass.CONVERTER.INTEGER_LENGTH + chunkdatasize
        Length += 12*chunkcount
        return Length
