from . import template

class handler(template.handler):
    def __init__(self, *args):
        self.NAME = "Update Window Property"
        self.HEADER = 0x69

    def receive(self, roboclass):
        roboclass.PACKETS.POINTER.read(5)
        return roboclass.PACKETS.POINTER.getposition()
        return 5
