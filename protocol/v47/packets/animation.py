from . import template

class handler(template.handler):
    def __init__(self, *args):
        self.NAME = "Animation"
        self.HEADER = 0x12

    def receive(self, roboclass):
        roboclass.PACKETS.POINTER.read(roboclass.CONVERTER.INTEGER_LENGTH + roboclass.CONVERTER.BYTE_LENGTH)
        return roboclass.PACKETS.POINTER.getposition()
