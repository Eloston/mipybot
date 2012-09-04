from . import template

class handler(template.handler):
    def __init__(self, *args):
        self.NAME = "Animation"
        self.HEADER = 0x12

    def receive(self, roboclass):
        return roboclass.CONVERTER.INTEGER_LENGTH + roboclass.CONVERTER.BYTE_LENGTH
