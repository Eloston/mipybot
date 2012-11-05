from . import template

class handler(template.handler):
    def __init__(self, *args):
        self.NAME = "Entity Velocity"
        self.HEADER = 0x1C

    def receive(self, roboclass):
        roboclass.PACKETS.POINTER.read(10)
        return roboclass.PACKETS.POINTER.getposition()
