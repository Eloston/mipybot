from . import template

class handler(template.handler):
    def __init__(self, *args):
        self.NAME = "Set Slot"
        self.HEADER = 0x67

    def receive(self, roboclass):
        roboclass.PACKETS.POINTER.read('byte')
        roboclass.PACKETS.POINTER.read('short')
        roboclass.PACKETS.POINTER.read('slot')
        return roboclass.PACKETS.POINTER.getposition()
