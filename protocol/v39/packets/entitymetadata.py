from . import template

class handler(template.handler):
    def __init__(self, *args):
        self.NAME = "Entity Metadata"
        self.HEADER = 0x28

    def receive(self, roboclass):
        roboclass.PACKETS.POINTER.read('int')
        roboclass.PACKETS.POINTER.read('entitymetadata')

        return roboclass.PACKETS.POINTER.getposition()
