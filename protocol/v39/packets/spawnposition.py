from . import template

class handler(template.handler):
    def __init__(self, *args):
        self.NAME = "Spawn Position"
        self.HEADER = 0x06

    def receive(self, roboclass, data):
        Position = 0
        X = roboclass.CONVERTER.getinteger(data, Position)
        Position += roboclass.CONVERTER.INTEGER_LENGTH
        Y = roboclass.CONVERTER.getinteger(data, Position)
        Position += roboclass.CONVERTER.INTEGER_LENGTH
        Z = roboclass.CONVERTER.getinteger(data, Position)
        positiondict = dict()
        positiondict['x'] = X
        positiondict['y'] = Y
        positiondict['z'] = Z
        roboclass.CHARACTER.updateposition(positiondict)
        print("Spawn position:\nX:", X, "\nY:", Y, "\nZ:", Z)

    def getlength(self, roboclass, data):
        return roboclass.CONVERTER.INTEGER_LENGTH*3
