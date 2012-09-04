from . import template

class handler(template.handler):
    def __init__(self, *args):
        self.NAME = "Explosion"
        self.HEADER = 0x3C

    def receive(self, roboclass):
        roboclass.PACKETS.POINTER.read('double')
        roboclass.PACKETS.POINTER.read('double')
        roboclass.PACKETS.POINTER.read('double')
        roboclass.PACKETS.POINTER.read('float')
        recordcount = roboclass.PACKETS.POINTER.read('int')
        roboclass.PACKETS.POINTER.read(recordcount*3)
        roboclass.PACKETS.POINTER.read('float')
        roboclass.PACKETS.POINTER.read('float')
        roboclass.PACKETS.POINTER.read('float')
        return roboclass.PACKETS.POINTER.getposition()
