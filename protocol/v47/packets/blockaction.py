from . import template

class handler(template.handler):
    def __init__(self, *args):
        self.NAME = "Block Action"
        self.HEADER = 0x36

    def receive(self, roboclass):
        roboclass.PACKETS.POINTER.read(14)
        return roboclass.PACKETS.POINTER.getposition()