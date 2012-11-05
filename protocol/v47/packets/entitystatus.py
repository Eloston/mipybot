from . import template

class handler(template.handler):
    def __init__(self, *args):
        self.NAME = "Entity Status"
        self.HEADER = 0x26

    def receive(self, roboclass):
        roboclass.PACKETS.POINTER.read(5)
        return roboclass.PACKETS.POINTER.getposition()
