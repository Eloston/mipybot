from . import template

class handler(template.handler):
    def __init__(self, *args):
        self.NAME = "Multi Block Change"
        self.HEADER = 0x34

    def receive(self, roboclass):
        roboclass.PACKETS.POINTER.read('int')
        roboclass.PACKETS.POINTER.read('int')
        roboclass.PACKETS.POINTER.read('short')
        roboclass.PACKETS.POINTER.read('integerdata')
        return roboclass.PACKETS.POINTER.getposition()
