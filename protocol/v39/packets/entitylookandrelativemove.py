from . import template

class handler(template.handler):
    def __init__(self, *args):
        self.NAME = "Entity Look and Relative Move"
        self.HEADER = 0x21

    def receive(self, roboclass):
        return 9
