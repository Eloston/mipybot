from . import template

class handler(template.handler):
    def __init__(self, *args):
        self.NAME = "Attach Entity"
        self.HEADER = 0x27

    def receive(self, roboclass):
        return 8
