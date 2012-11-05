from . import template

class handler(template.handler):
    def __init__(self, *args):
        self.NAME = "Chunk Data"
        self.HEADER = 0x33

    def receive(self, roboclass):
        roboclass.PACKETS.POINTER.read('int')
        roboclass.PACKETS.POINTER.read('int')
        roboclass.PACKETS.POINTER.read('short')
        roboclass.PACKETS.POINTER.read('short')
        roboclass.PACKETS.POINTER.read('byte')
        roboclass.PACKETS.POINTER.read('integerdata')
        return roboclass.PACKETS.POINTER.getposition()
