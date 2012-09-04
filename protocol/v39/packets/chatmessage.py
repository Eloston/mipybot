from . import template

class handler(template.handler):
    def __init__(self, *args):
        self.NAME = "Chat Message"
        self.HEADER = 0x03

    def receive(self, roboclass):
        print("Message:", roboclass.PACKETS.POINTER.read('string'))
        return roboclass.PACKETS.POINTER.getposition()
