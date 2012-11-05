from . import template

class handler(template.handler):
    def __init__(self, *args):
        self.NAME = "Spawn Position"
        self.HEADER = 0x06

    def receive(self, roboclass):
        X = roboclass.PACKETS.POINTER.read('int')
        Y = roboclass.PACKETS.POINTER.read('int')
        Z = roboclass.PACKETS.POINTER.read('int')

        positiondict = dict()
        positiondict['x'] = X
        positiondict['y'] = Y
        positiondict['z'] = Z
        roboclass.CHARACTER.updateposition(positiondict)
        print("Spawn position:\nX:", X, "\nY:", Y, "\nZ:", Z)

        return roboclass.PACKETS.POINTER.getposition()
