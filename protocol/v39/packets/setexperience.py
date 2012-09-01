from . import template

class handler(template.handler):
    def __init__(self, *args):
        self.NAME = "Set Experience"
        self.HEADER = 0x2B

    def receive(self, roboclass, data):
        Position = 0
        xpdict = dict()

        bar = roboclass.CONVERTER.getfloat(data, Position)
        xpdict['bar'] = bar
        Position += roboclass.CONVERTER.FLOAT_LENGTH

        level = roboclass.CONVERTER.getshort(data, Position)
        xpdict['level'] = level
        Position += roboclass.CONVERTER.SHORT_LENGTH

        total = roboclass.CONVERTER.getshort(data, Position)
        xpdict['total'] = total
        Position += roboclass.CONVERTER.SHORT_LENGTH

        roboclass.CHARACTER.updateexperience(xpdict)

        print("Experience dictionary:", xpdict)

    def getlength(self, roboclass, data):
        return 8
