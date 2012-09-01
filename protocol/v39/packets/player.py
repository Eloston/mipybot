from . import template

class handler(template.handler):
    def __init__(self, *args):
        self.NAME = "Player"
        self.HEADER = 0x0A

    def send(self, roboclass):
        return roboclass.CONVERTER.makebool(roboclass.CHARACTER.POSITION['onground'])
