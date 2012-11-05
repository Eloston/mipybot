from . import template

class handler(template.handler):
    def __init__(self, *args):
        self.NAME = "Destroy Entity"
        self.HEADER = 0x1D

    def receive(self, roboclass):
        entitycount = roboclass.PACKETS.POINTER.read('byte')
        for iteration in list(range(entitycount)):
            roboclass.PACKETS.POINTER.read('int')
        return roboclass.PACKETS.POINTER.getposition()
