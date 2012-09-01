from . import template

class handler(template.handler):
    def __init__(self, *args):
        self.NAME = "Spawn Named Entity"
        self.HEADER = 0x14

    def getlength(self, roboclass, data):
        Position = roboclass.CONVERTER.INTEGER_LENGTH
        Position += roboclass.CONVERTER.getstringdata(data, Position)['length'] + roboclass.CONVERTER.SHORT_LENGTH
        Position += roboclass.CONVERTER.INTEGER_LENGTH*3 + roboclass.CONVERTER.BYTE_LENGTH*2 + roboclass.CONVERTER.SHORT_LENGTH
        x = roboclass.CONVERTER.getbyte(data, Position, False)
        Position += roboclass.CONVERTER.BYTE_LENGTH
        while not x == 127:
            ty = x >> 5
            if ty == 0:
                Position += roboclass.CONVERTER.BYTE_LENGTH
            if ty == 1:
                Position += roboclass.CONVERTER.SHORT_LENGTH
            if ty == 2:
                Position += roboclass.CONVERTER.INTEGER_LENGTH
            if ty == 3:
                Position += roboclass.CONVERTER.FLOAT_LENGTH
            if ty == 4:
                print("DERRRRRPPPPPPPPPPPPPPPPPPPPPPP")
                Position += roboclass.CONVERTER.getstringdata(data, Position)['length']
                Position += roboclass.CONVERTER.SHORT_LENGTH
            if ty == 5:
                Position += roboclass.CONVERTER.SHORT_LENGTH*2 + roboclass.CONVERTER.BYTE_LENGTH
            if ty == 6:
                Position += roboclass.CONVERTER.INTEGER_LENGTH*3
            x = roboclass.CONVERTER.getbyte(data, Position, False)
            Position += roboclass.CONVERTER.BYTE_LENGTH
        return Position
