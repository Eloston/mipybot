from . import template

class handler(template.handler):
    def __init__(self, *args):
        self.NAME = "Time Update"
        self.HEADER = 0x04

    def receive(self, roboclass):
        roboclass.CHARACTER.TIME = roboclass.PACKETS.POINTER.read('long')
        return roboclass.PACKETS.POINTER.getposition()
