from . import template

class handler(template.handler):
    def __init__(self, *args):
        self.NAME = "Sound/Particle Effect"
        self.HEADER = 0x3D

    def getlength(self, roboclass, data):
        return 17
