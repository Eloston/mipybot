from . import template

class handler(template.handler):
    def __init__(self, *args):
        self.NAME = "Open Window"
        self.HEADER = 0x64

    def receive(self, roboclass):
        roboclass.PACKETS.POINTER.read('byte')
        roboclass.PACKETS.POINTER.read('byte')
        roboclass.PACKETS.POINTER.read('string')
        roboclass.PACKETS.POINTER.read('byte')

        return roboclass.PACKETS.POINTER.getposition()
