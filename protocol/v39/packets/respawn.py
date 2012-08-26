from . import template

class handler(template.handler):
    def __init__(self, *args):
        self.NAME = "Respawn"
        self.HEADER = 0x09

    def receive(self, roboclass, data):
        dimension = roboclass.CONVERTER.getinteger(data)
        Position += roboclass.CONVERTER.INTEGER_LENGTH
        difficulty = roboclass.CONVERTER.getbyte(data, Position)
        Position += roboclass.CONVERTER.BYTE_LENGTH
        gamemode = roboclass.CONVERTER.getbyte(data, Position)
        Position += roboclass.CONVERTER.BYTE_LENGTH
        worldheight = roboclass.CONVERTER.getshort(data, Position)
        Position += roboclass.CONVERTER.SHORT_LENGTH
        leveltype = roboclass.CONVERTER.getstringdata(data, Position)['string']
        worldinfodict = dict()
        worldinfodict['dimension'] = dimension
        worldinfodict['difficulty'] = difficulty
        worldinfodict['gamemode'] = gamemode
        worldinfodict['maxheight'] = worldheight
        worldinfodict['leveltype'] = leveltype
        roboclass.CHARACTER.updateworldinfo(worldinfodict)

    def getlength(self, roboclass, data):
        Length = roboclass.CONVERTER.INTEGER_LENGTH + roboclass.CONVERTER.BYTE_LENGTH + roboclass.CONVERTER.BYTE_LENGTH + roboclass.CONVERTER.SHORT_LENGTH
        Length += roboclass.CONVERTER.getstringdata(data, Length)['length']
        return Length
