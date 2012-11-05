from . import template

class handler(template.handler):
    def __init__(self, *args):
        self.NAME = "Entity Head Look"
        self.HEADER = 0x23

    def receive(self, roboclass):
        roboclass.PACKETS.POINTER.read(5)
        return roboclass.PACKETS.POINTER.getposition()
