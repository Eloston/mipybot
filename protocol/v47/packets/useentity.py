from . import template

class handler(template.handler):
    def __init__(self, *args):
        self.NAME = "Use Entity"
        self.HEADER = 0x07

    def receive(self, roboclass):
        roboclass.PACKETS.POINTER.read(9)
        return roboclass.PACKETS.POINTER.getposition()
