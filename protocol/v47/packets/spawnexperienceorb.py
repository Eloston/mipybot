from . import template

class handler(template.handler):
    def __init__(self, *args):
        self.NAME = "Spawn Experience Orb"
        self.HEADER = 0x1A

    def receive(self, roboclass):
        roboclass.PACKETS.POINTER.read(18)
        return roboclass.PACKETS.POINTER.getposition()
