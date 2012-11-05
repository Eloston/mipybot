from . import template

class handler(template.handler):
    def __init__(self, *args):
        self.NAME = "Block Change"
        self.HEADER = 0x35

    def receive(self, roboclass):
        roboclass.PACKETS.POINTER.read(12)
        return roboclass.PACKETS.POINTER.getposition()
