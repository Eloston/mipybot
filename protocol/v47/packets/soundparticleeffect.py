from . import template

class handler(template.handler):
    def __init__(self, *args):
        self.NAME = "Sound or Particle Effect"
        self.HEADER = 0x3D

    def receive(self, roboclass):
        roboclass.PACKETS.POINTER.read(19)
        return roboclass.PACKETS.POINTER.getposition()
