from . import template

class handler(template.handler):
    def __init__(self, *args):
        self.NAME = "Collect Item"
        self.HEADER = 0x16

    def receive(self, roboclass):
        roboclass.PACKETS.POINTER.read('int')
        roboclass.PACKETS.POINTER.read('int')
        return roboclass.PACKETS.POINTER.getposition()
