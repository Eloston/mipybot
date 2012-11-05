from . import template

class handler(template.handler):
    def __init__(self, *args):
        self.NAME = "Map Chunk Bulk"
        self.HEADER = 0x38

    def receive(self, roboclass):
        chunkcount = roboclass.PACKETS.POINTER.read('short')

        roboclass.PACKETS.POINTER.read('integerdata')

        roboclass.PACKETS.POINTER.read(chunkcount*12)

        return roboclass.PACKETS.POINTER.getposition()
