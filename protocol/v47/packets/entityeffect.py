from . import template

class handler(template.handler):
    def __init__(self, *args):
        self.NAME = "Entity Effect"
        self.HEADER = 0x29

    def receive(self, roboclass):
        roboclass.PACKETS.POINTER.read(8)
        return roboclass.PACKETS.POINTER.getposition()
