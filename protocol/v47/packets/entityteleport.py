from . import template

class handler(template.handler):
    def __init__(self, *args):
        self.NAME = "Entity Teleport"
        self.HEADER = 0x22

    def receive(self, roboclass):
        roboclass.PACKETS.POINTER.read(18)
        return roboclass.PACKETS.POINTER.getposition()
