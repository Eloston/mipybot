from . import template

class handler(template.handler):
    def __init__(self, *args):
        self.NAME = "Entity Metadata"
        self.HEADER = 0x28

    def getlength(self, roboclass, data):
        Position = roboclass.CONVERTER.INTEGER_LENGTH
        x = roboclass.CONVERTER.getbyte(data, Position, False)
        Position += roboclass.CONVERTER.BYTE_LENGTH
        while not x == 127:
            print("HAIIIIIIIIIIIIIIIIIIIIIIII")
            print("Index:", x & 0x1F)
            ty = x >> 5
            if ty == 0:
                print("Type 0")
                Position += roboclass.CONVERTER.BYTE_LENGTH
            if ty == 1:
                print("Type 1")
                Position += roboclass.CONVERTER.SHORT_LENGTH
            if ty == 2:
                print("Type 2")
                Position += roboclass.CONVERTER.INTEGER_LENGTH
            if ty == 3:
                print("Type 3")
                Position += roboclass.CONVERTER.FLOAT_LENGTH
            if ty == 4:
                print("Type 4")
                #Position += roboclass.CONVERTER.getstringdata(data, Position)['length']
                #Position += roboclass.CONVERTER.SHORT_LENGTH
                Position += 16
            if ty == 5:
                print("Type 5")
                Position += roboclass.CONVERTER.SHORT_LENGTH*2 + roboclass.CONVERTER.BYTE_LENGTH
            if ty == 6:
                print("Type 6")
                Position += roboclass.CONVERTER.INTEGER_LENGTH*3
            x = roboclass.CONVERTER.getbyte(data, Position, False)
            Position += roboclass.CONVERTER.BYTE_LENGTH
        return Position
