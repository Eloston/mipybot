from . import template

class handler(template.handler):
    def __init__(self, *args):
        self.NAME = "Use Entity"
        self.HEADER = 0x07
