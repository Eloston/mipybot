from . import template

class handler(template.handler):
    def __init__(self, *args):
        self.NAME = "Player Look"
        self.HEADER = 0x0C

    def send(self, roboclass):
        yaw = roboclass.CONVERTER.makefloat(roboclass.CHARACTER.POSITION['yaw'])

        pitch = roboclass.CONVERTER.makefloat(roboclass.CHARACTER.POSITION['pitch'])

        onground = roboclass.CONVERTER.makebool(roboclass.CHARACTER.POSITION['onground'])

        return yaw + pitch + onground
