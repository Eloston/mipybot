from . import template

class handler(template.handler):
    def __init__(self, *args):
        self.NAME = "Login Request"
        self.HEADER = 0x01

    def receive(self, roboclass, data):
        entityid = roboclass.CONVERTER.getinteger(data)
        Position = roboclass.CONVERTER.INTEGER_LENGTH
        leveltype_dict = roboclass.CONVERTER.getstringdata(data, Position)
        Position += leveltype_dict["length"]
        leveltype = leveltype_dict["string"]
        Position += roboclass.CONVERTER.SHORT_LENGTH
        gamemode = roboclass.CONVERTER.getbyte(data, Position)
        Position += roboclass.CONVERTER.BYTE_LENGTH # Gamemode is a byte, so we advance a byte
        dimension = roboclass.CONVERTER.getbyte(data, Position)
        Position += roboclass.CONVERTER.BYTE_LENGTH
        difficulty = roboclass.CONVERTER.getbyte(data, Position)
        Position += roboclass.CONVERTER.BYTE_LENGTH
        unused = roboclass.CONVERTER.getbyte(data, Position) # Seems to be only 0
        Position += roboclass.CONVERTER.BYTE_LENGTH
        maxplayers = roboclass.CONVERTER.getbyte(data, Position)

        roboclass.CHARACTER.ENTITYID = entityid
        roboclass.NETWORK.MAXPLAYERS = maxplayers
        worldinfodict = dict()
        worldinfodict['leveltype'] = leveltype
        worldinfodict['dimension'] = dimension
        worldinfodict['gamemode'] = gamemode
        worldinfodict['difficulty'] = difficulty
        roboclass.CHARACTER.updateworldinfo(worldinfodict)

        print("Login Information:\nEntity ID: ", entityid, "\nLevel Type: ", leveltype, "\nGame mode: ", gamemode, "\nDimension: ", dimension, "\nDifficulty: ", difficulty, "\nUnused: ", unused, "\nMax Players: ", maxplayers, "\n--------------------")

    def getlength(self, roboclass, data):
        Length = roboclass.CONVERTER.INTEGER_LENGTH # Entity ID
        Length += roboclass.CONVERTER.getstringdata(data, Length)["length"] # Level type string
        Length += roboclass.CONVERTER.SHORT_LENGTH # Level type string short
        Length += 5 # Game Mode, Dimension, Difficulty, Unused, and Max players
        return Length
