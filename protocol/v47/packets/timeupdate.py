from . import template

class handler(template.handler):
    def __init__(self, *args):
        self.NAME = "Time Update"
        self.HEADER = 0x04

    def receive(self, roboclass):
        roboclass.CHARACTER.TIMEAGE = roboclass.PACKETS.POINTER.read('long')
        roboclass.CHARACTER.TIMEDAY = roboclass.PACKETS.POINTER.read('long')
        return roboclass.PACKETS.POINTER.getposition()
