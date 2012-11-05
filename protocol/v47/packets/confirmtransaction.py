from . import template

class handler(template.handler):
    def __init__(self, *args):
        self.NAME = "Confirm Transaction"
        self.HEADER = 0x6A

    def receive(self, roboclass):
        roboclass.PACKETS.POINTER.read(4)
        return roboclass.PACKETS.POINTER.getposition()
