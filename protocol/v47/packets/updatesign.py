from . import template

class handler(template.handler):
    def __init__(self, *args):
        self.NAME = "Update Sign"
        self.HEADER = 0x82

    def receive(self, roboclass):
        roboclass.PACKETS.POINTER.read('int')
        roboclass.PACKETS.POINTER.read('short')
        roboclass.PACKETS.POINTER.read('int')
        roboclass.PACKETS.POINTER.read('string')
        roboclass.PACKETS.POINTER.read('string')
        roboclass.PACKETS.POINTER.read('string')
        roboclass.PACKETS.POINTER.read('string')

        return roboclass.PACKETS.POINTER.getposition()
