from . import template

class handler(template.handler):
    def __init__(self, *args):
        self.NAME = "Collect Item"
        self.HEADER = 0x16

    def getlength(self, roboclass, data):
        return roboclass.CONVERTER.INTEGER_LENGTH*2
