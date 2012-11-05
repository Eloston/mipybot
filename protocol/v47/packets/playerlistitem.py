from . import template

class handler(template.handler):
    def __init__(self, *args):
        self.NAME = "Player List Item"
        self.HEADER = 0xC9

    def receive(self, roboclass):
        roboclass.PACKETS.POINTER.read('string')
        roboclass.PACKETS.POINTER.read('bool')
        roboclass.PACKETS.POINTER.read('short')

        return roboclass.PACKETS.POINTER.getposition()
