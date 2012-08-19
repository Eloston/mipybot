from . import template
import struct

class handler():
    def __init__(self, *args):
        self.NAME = "Login Request"
        self.HEADER = 0x01

    def receive(self, roboclass, data):
        entityid = struct.unpack('!i', data[:roboclass.INTEGER_LENGTH])[0]
        Position = roboclass.INTEGER_LENGTH
        leveltype_length = struct.unpack('!h', data[Position:Position+roboclass.SHORT_LENGTH])[0] * 2
        Position += roboclass.SHORT_LENGTH
        leveltype = data[Position:Position+leveltype_length].decode(roboclass.STRING_ENCODE)
        Position += leveltype_length
        gamemode = data[Position]
        Position += 1 # Gamemode is a byte, so we advance a byte
        dimension = data[Position]
        Position += 1
        difficulty = data[Position]
        Position += 1
        unused = data[Position] # Seems to be only 0
        Position += 1
        maxplayers = data[Position]
        print("Login Information:\nEntity ID: ", entityid, "\nLevel Type: ", leveltype, "\nGame mode: ", gamemode, "\nDimension: ", dimension, "\nDifficulty: ", difficulty, "\nUnused: ", unused, "\nMax Players: ", maxplayers, "\n--------------------")

    def getlength(self, roboclass, data):
        Length = roboclass.INTEGER_LENGTH # Entity ID 
        Length += struct.unpack('!h', data[Length:Length+roboclass.SHORT_LENGTH])[0] * 2 # Level type string
        Length += roboclass.SHORT_LENGTH # Level type string short
        Length += 5 # Game Mode, Dimension, Difficulty, Unused, and Max players
        return Length
