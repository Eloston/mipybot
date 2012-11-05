from . import template

class handler(template.handler):
    def __init__(self, *args):
        self.NAME = "Named Sound Effect"
        self.HEADER = 0x3E

    def receive(self, roboclass):
        roboclass.PACKETS.POINTER.read('string')
        roboclass.PACKETS.POINTER.read('int')
        roboclass.PACKETS.POINTER.read('int')
        roboclass.PACKETS.POINTER.read('int')
        roboclass.PACKETS.POINTER.read('float')
        roboclass.PACKETS.POINTER.read('byte')

        return roboclass.PACKETS.POINTER.getposition()
