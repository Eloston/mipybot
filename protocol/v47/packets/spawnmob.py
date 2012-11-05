from . import template

class handler(template.handler):
    def __init__(self, *args):
        self.NAME = "Spawn Mob"
        self.HEADER = 0x18

    def receive(self, roboclass):
        roboclass.PACKETS.POINTER.read('int')
        roboclass.PACKETS.POINTER.read('byte')
        roboclass.PACKETS.POINTER.read('int')
        roboclass.PACKETS.POINTER.read('int')
        roboclass.PACKETS.POINTER.read('int')
        roboclass.PACKETS.POINTER.read('byte')
        roboclass.PACKETS.POINTER.read('byte')
        roboclass.PACKETS.POINTER.read('byte')
        roboclass.PACKETS.POINTER.read('short')
        roboclass.PACKETS.POINTER.read('short')
        roboclass.PACKETS.POINTER.read('short')
        roboclass.PACKETS.POINTER.read('entitymetadata')

        return roboclass.PACKETS.POINTER.getposition()
