from . import template

class handler(template.handler):
    def __init__(self, *args):
        self.NAME = "Entity Look"
        self.HEADER = 0x20

    def receive(self, roboclass):
        roboclass.PACKETS.POINTER.read(6)
        return roboclass.PACKETS.POINTER.getposition()
