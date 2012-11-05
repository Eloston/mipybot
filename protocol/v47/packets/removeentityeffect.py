from . import template

class handler(template.handler):
    def __init__(self, *args):
        self.NAME = "Remove Entity Effect"
        self.HEADER = 0x2A

    def receive(self, roboclass):
        roboclass.PACKETS.POINTER.read(5)
        return roboclass.PACKETS.POINTER.getposition()
