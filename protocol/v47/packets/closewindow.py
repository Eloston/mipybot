from . import template

class handler(template.handler):
    def __init__(self, *args):
        self.NAME = "Close Window"
        self.HEADER = 0x65

    def receive(self, roboclass):
        roboclass.PACKETS.POINTER.read(1)
        return roboclass.PACKETS.POINTER.getposition()
