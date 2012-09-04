from . import template

class handler(template.handler):
    def __init__(self, *args):
        self.NAME = "Player Abilities"
        self.HEADER = 0xCA

    def receive(self, roboclass):
        return 3
