from . import template

class handler(template.handler):
    def __init__(self, *args):
        self.NAME = "Spawn Painting"
        self.HEADER = 0x19

    def receive(self, roboclass):
        roboclass.PACKETS.POINTER.read('int')
        roboclass.PACKETS.POINTER.read('string')
        roboclass.PACKETS.POINTER.read('int')
        roboclass.PACKETS.POINTER.read('int')
        roboclass.PACKETS.POINTER.read('int')
        roboclass.PACKETS.POINTER.read('int')

        return roboclass.PACKETS.POINTER.getposition()
