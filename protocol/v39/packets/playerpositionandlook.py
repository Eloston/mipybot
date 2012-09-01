from . import template

class handler(template.handler):
    def __init__(self, *args):
        self.NAME = "Player Position & Look"
        self.HEADER = 0x0D

    def send(self, roboclass):
        x = roboclass.CONVERTER.makedouble(roboclass.CHARACTER.POSITION['x'])

        y = roboclass.CONVERTER.makedouble(roboclass.CHARACTER.POSITION['y'])

        stance = roboclass.CONVERTER.makedouble(roboclass.CHARACTER.POSITION['stance'])

        z = roboclass.CONVERTER.makedouble(roboclass.CHARACTER.POSITION['z'])

        yaw = roboclass.CONVERTER.makefloat(roboclass.CHARACTER.POSITION['yaw'])

        pitch = roboclass.CONVERTER.makefloat(roboclass.CHARACTER.POSITION['pitch'])

        onground = roboclass.CONVERTER.makebool(roboclass.CHARACTER.POSITION['onground'])

        return x + y + stance + z + yaw + pitch + onground

    def receive(self, roboclass, data):
        Position = 0
        positiondict = dict()

        positiondict['x'] = roboclass.CONVERTER.getdouble(data, Position)
        Position += roboclass.CONVERTER.DOUBLE_LENGTH

        positiondict['stance'] = roboclass.CONVERTER.getdouble(data, Position)
        Position += roboclass.CONVERTER.DOUBLE_LENGTH

        positiondict['y'] = roboclass.CONVERTER.getdouble(data, Position)
        Position += roboclass.CONVERTER.DOUBLE_LENGTH

        positiondict['z'] = roboclass.CONVERTER.getdouble(data, Position)
        Position += roboclass.CONVERTER.DOUBLE_LENGTH

        positiondict['yaw'] = roboclass.CONVERTER.getfloat(data, Position)
        Position += roboclass.CONVERTER.FLOAT_LENGTH

        positiondict['pitch'] = roboclass.CONVERTER.getfloat(data, Position)
        Position += roboclass.CONVERTER.FLOAT_LENGTH

        positiondict['onground'] = roboclass.CONVERTER.getbool(data, Position)
        Position += roboclass.CONVERTER.BYTE_LENGTH

        roboclass.CHARACTER.updateposition(positiondict)

        print("Position Dictionary:", positiondict)

        roboclass.PACKETS.send(0x0D)

    def getlength(self, roboclass, data):
        return roboclass.CONVERTER.DOUBLE_LENGTH*4 + roboclass.CONVERTER.FLOAT_LENGTH*2 + roboclass.CONVERTER.BYTE_LENGTH
