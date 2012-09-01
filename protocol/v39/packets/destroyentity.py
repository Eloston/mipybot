from . import template

class handler(template.handler):
    def __init__(self, *args):
        self.NAME = "Destroy Entity"
        self.HEADER = 0x1D

    def getlength(self, roboclass, data):
        entitycount = roboclass.CONVERTER.getbyte(data)
        return roboclass.CONVERTER.BYTE_LENGTH + roboclass.CONVERTER.INTEGER_LENGTH*entitycount
