from . import template

class handler(template.handler):
    def __init__(self, *args):
        self.NAME = "Entity Look and Relative Move"
        self.HEADER = 0x21

    def receive(self, roboclass):
        roboclass.PACKETS.POINTER.read(9)
        return roboclass.PACKETS.POINTER.getposition()
