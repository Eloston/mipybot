from . import template

class handler(template.handler):
    def __init__(self, *args):
        self.NAME = "Creative Inventory Action"
        self.HEADER = 0x6B

    def receive(self, roboclass):
        roboclass.PACKETS.POINTER.read('short')
        roboclass.PACKETS.POINTER.read('slot')
        return roboclass.PACKETS.POINTER.getposition()
