from . import template

class handler(template.handler):
    def __init__(self, *args):
        self.NAME = "Entity Equipment"
        self.HEADER = 0x05

    def receive(self, roboclass):
        roboclass.PACKETS.POINTER.read('int')
        roboclass.PACKETS.POINTER.read('short')
        roboclass.PACKETS.POINTER.read('slot')

        return roboclass.PACKETS.POINTER.getposition()
