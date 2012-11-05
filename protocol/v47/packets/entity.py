from . import template

class handler(template.handler):
    def __init__(self, *args):
        self.NAME = "Entity"
        self.HEADER = 0x1E

    def receive(self, roboclass):
        roboclass.PACKETS.POINTER.read(4)
        return roboclass.PACKETS.POINTER.getposition()
