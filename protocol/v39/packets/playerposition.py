from . import template

class handler(template.handler):
    def __init__(self, *args):
        self.NAME = "Player Position"
        self.HEADER = 0x0B

    def send(self, roboclass):
        x = roboclass.CONVERTER.makedouble(roboclass.CHARACTER.POSITION['x'])

        y = roboclass.CONVERTER.makedouble(roboclass.CHARACTER.POSITION['y'])

        stance = roboclass.CONVERTER.makedouble(roboclass.CHARACTER.POSITION['stance'])

        z = roboclass.CONVERTER.makedouble(roboclass.CHARACTER.POSITION['z'])

        onground = roboclass.CONVERTER.makebool(roboclass.CHARACTER.POSITION['onground'])

        return x + y + stance + z + onground
