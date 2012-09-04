from . import template

class handler(template.handler):
    def __init__(self, *args):
        self.NAME = "Spawn Object/Vehicle"
        self.HEADER = 0x17

    def receive(self, roboclass):
        roboclass.PACKETS.POINTER.read('int')
        roboclass.PACKETS.POINTER.read('byte')
        roboclass.PACKETS.POINTER.read('int')
        roboclass.PACKETS.POINTER.read('int')
        roboclass.PACKETS.POINTER.read('int')
        objectdata = roboclass.PACKETS.POINTER.read('int')
        if objectdata > 0:
            roboclass.PACKETS.POINTER.read('short')
            roboclass.PACKETS.POINTER.read('short')
            roboclass.PACKETS.POINTER.read('short')
        return roboclass.PACKETS.POINTER.getposition()
