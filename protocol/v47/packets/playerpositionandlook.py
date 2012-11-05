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

    def receive(self, roboclass):
        positiondict = dict()

        positiondict['x'] = roboclass.PACKETS.POINTER.read('double')

        positiondict['stance'] = roboclass.PACKETS.POINTER.read('double')

        positiondict['y'] = roboclass.PACKETS.POINTER.read('double')

        positiondict['z'] = roboclass.PACKETS.POINTER.read('double')

        positiondict['yaw'] = roboclass.PACKETS.POINTER.read('float')

        positiondict['pitch'] = roboclass.PACKETS.POINTER.read('float')

        positiondict['onground'] = roboclass.PACKETS.POINTER.read('bool')

        roboclass.CHARACTER.updateposition(positiondict)

        print("Position Dictionary:", positiondict)

        roboclass.PACKETS.send(0x0D)

        return roboclass.PACKETS.POINTER.getposition()
