from . import template

class handler(template.handler):
    def __init__(self, *args):
        self.NAME = "Chunk Data"
        self.HEADER = 0x33

    def getlength(self, roboclass, data):
        Length = roboclass.CONVERTER.INTEGER_LENGTH*2 + roboclass.CONVERTER.SHORT_LENGTH*2 + roboclass.CONVERTER.BYTE_LENGTH
        chunkdatasize = roboclass.CONVERTER.getintegerdata(data, Length)['length']
        Length += roboclass.CONVERTER.INTEGER_LENGTH + chunkdatasize
        return Length
