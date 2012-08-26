from . import template

class handler(template.handler):
    def __init__(self, *args):
        self.NAME = "Time Update"
        self.HEADER = 0x04

    def receive(self, roboclass, data):
        roboclass.CHARACTER.TIME = roboclass.CONVERTER.getlong(data)

    def getlength(self, roboclass, data):
        return roboclass.CONVERTER.LONG_LENGTH
