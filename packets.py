import constants

import struct
import logging
import queue

# *** DATA TYPES ***

class MCtypetemplate():
    def __init__(self, roboclass):
        self.LENGTH = 0
        self.RECEIVEBUFFER = roboclass.NETWORK.RECEIVEBUFFER
        self.SENDBUFFER = roboclass.NETWORK.SENDBUFFER
        self.FORMAT = None
        self.UFORMAT = None

    def read(self, signed=True):
        rawbytes = self.RECEIVEBUFFER.pop(self.LENGTH)
        if signed:
            return struct.unpack(self.FORMAT, rawbytes)[0]
        else:
            return struct.unpack(self.UFORMAT, rawbytes)[0]

    def write(self, data, signed=True):
        if signed:
            tosend = struct.pack(self.FORMAT, data)
        else:
            tosend = struct.pack(self.UFORMAT, data)
        self.SENDBUFFER.add(tosend)

class MCbytearray(MCtypetemplate):
    def read(self, length):
        return self.RECEIVEBUFFER.pop(length)

    def write(self, *args):
        raise Exception("Writing not defined for Byte Array format")

class MCshort(MCtypetemplate):
    def __init__(self, roboclass):
        self.LENGTH = 2
        self.RECEIVEBUFFER = roboclass.NETWORK.RECEIVEBUFFER
        self.SENDBUFFER = roboclass.NETWORK.SENDBUFFER
        self.FORMAT = '!h'
        self.UFORMAT = '!H'

class MCshortdata(MCtypetemplate):
    def __init__(self, roboclass):
        self.LENGTH = None
        self.RECEIVEBUFFER = roboclass.NETWORK.RECEIVEBUFFER
        self.SENDBUFFER = roboclass.NETWORK.SENDBUFFER
        self.ROBOCLASS = roboclass
        self.FORMAT = '!h'
        self.UFORMAT = '!H'

    def read(self, signed=True):
        if signed:
            length = MCshort(self.ROBOCLASS).read()
        else:
            length = MCshort(self.ROBOCLASS).read(False)
        return self.RECEIVEBUFFER.pop(length)

    def write(self, data, signed=True):
        if signed:
            datalength = struct.pack(self.FORMAT, len(data))
        else:
            datalength = struct.pack(self.UFORMAT, len(data))
        self.SENDBUFFER.add(datalength)
        self.SENDBUFFER.add(data)

class MCstring(MCtypetemplate):
    def __init__(self, roboclass):
        self.LENGTH = None
        self.RECEIVEBUFFER = roboclass.NETWORK.RECEIVEBUFFER
        self.SENDBUFFER = roboclass.NETWORK.SENDBUFFER
        self.ROBOCLASS = roboclass
        self.FORMAT = '!h'
        self.UFORMAT = '!H'
        self.STRINGTYPE = "UTF-16be"

    def read(self, signed=True):
        if signed:
            length = MCshort(self.ROBOCLASS).read()
        else:
            length = MCshort(self.ROBOCLASS).read(False)
        length *= 2
        return self.RECEIVEBUFFER.pop(length).decode(self.STRINGTYPE)

    def write(self, data, signed=True):
        if signed:
            datalength = struct.pack(self.FORMAT, len(data))
        else:
            datalength = struct.pack(self.UFORMAT, len(data))
        self.SENDBUFFER.add(datalength)
        self.SENDBUFFER.add(data.encode(self.STRINGTYPE))

class MCbyte(MCtypetemplate):
    def __init__(self, roboclass):
        self.LENGTH = 1
        self.RECEIVEBUFFER = roboclass.NETWORK.RECEIVEBUFFER
        self.SENDBUFFER = roboclass.NETWORK.SENDBUFFER
        self.FORMAT = 'b'
        self.UFORMAT = 'B'

class MCbool(MCtypetemplate):
    def __init__(self, roboclass):
        self.LENGTH = 1
        self.RECEIVEBUFFER = roboclass.NETWORK.RECEIVEBUFFER
        self.SENDBUFFER = roboclass.NETWORK.SENDBUFFER
        self.FORMAT = '?'
        self.UFORMAT = '?'

class MCint(MCtypetemplate):
    def __init__(self, roboclass):
        self.LENGTH = 4
        self.RECEIVEBUFFER = roboclass.NETWORK.RECEIVEBUFFER
        self.SENDBUFFER = roboclass.NETWORK.SENDBUFFER
        self.FORMAT = '!i'
        self.UFORMAT = '!I'

class MCintdata(MCtypetemplate):
    def __init__(self, roboclass):
        self.LENGTH = 4
        self.RECEIVEBUFFER = roboclass.NETWORK.RECEIVEBUFFER
        self.SENDBUFFER = roboclass.NETWORK.SENDBUFFER
        self.ROBOCLASS = roboclass
        self.FORMAT = '!i'
        self.UFORMAT = '!I'

    def read(self, signed=True):
        if signed:
            length = MCint(self.ROBOCLASS).read()
        else:
            length = MCint(self.ROBOCLASS).read(False)
        return self.RECEIVEBUFFER.pop(length)

    def write(self, data, signed=True):
        if signed:
            datalength = struct.pack(self.FORMAT, len(data))
        else:
            datalength = struct.pack(self.UFORMAT, len(data))
        self.SENDBUFFER.add(datalength)
        self.SENDBUFFER.add(data)

class MClong(MCtypetemplate):
    def __init__(self, roboclass):
        self.LENGTH = 8
        self.RECEIVEBUFFER = roboclass.NETWORK.RECEIVEBUFFER
        self.SENDBUFFER = roboclass.NETWORK.SENDBUFFER
        self.FORMAT = '!q'
        self.UFORMAT = '!Q'

class MCfloat(MCtypetemplate):
    def __init__(self, roboclass):
        self.LENGTH = 4
        self.RECEIVEBUFFER = roboclass.NETWORK.RECEIVEBUFFER
        self.SENDBUFFER = roboclass.NETWORK.SENDBUFFER
        self.FORMAT = '!f'
        self.UFORMAT = '!f'

class MCdouble(MCtypetemplate):
    def __init__(self, roboclass):
        self.LENGTH = 8
        self.RECEIVEBUFFER = roboclass.NETWORK.RECEIVEBUFFER
        self.SENDBUFFER = roboclass.NETWORK.SENDBUFFER
        self.FORMAT = '!d'
        self.UFORMAT = '!d'

class MCslot(MCtypetemplate):
    def __init__(self, roboclass):
        self.LENGTH = None
        self.RECEIVEBUFFER = roboclass.NETWORK.RECEIVEBUFFER
        self.SENDBUFFER = roboclass.NETWORK.SENDBUFFER
        self.ROBOCLASS = roboclass

    def write(self, data):
        raise Exception("Writing not defined for Slot format")

    def read(self):
        blockid = MCshort(self.ROBOCLASS).read()
        if not blockid == -1:
            MCbyte(self.ROBOCLASS).read()
            MCshort(self.ROBOCLASS).read()
            metadatalength = MCshort(self.ROBOCLASS).read()
            if not metadatalength == -1:
                self.RECEIVEBUFFER.pop(metadatalength)

class MCobjectdata(MCtypetemplate):
    def __init__(self, roboclass):
        self.LENGTH = None
        self.RECEIVEBUFFER = roboclass.NETWORK.RECEIVEBUFFER
        self.SENDBUFFER = roboclass.NETWORK.SENDBUFFER
        self.ROBOCLASS = roboclass

    def write(self, data):
        raise Exception("Writing not defined for Object Data format")

    def read(self):
        typevalue = MCint(self.ROBOCLASS).read()
        if typevalue > 0:
            MCshort(self.ROBOCLASS).read()
            MCshort(self.ROBOCLASS).read()
            MCshort(self.ROBOCLASS).read()

class MCentitymetadata(MCtypetemplate):
    def __init__(self, roboclass):
        self.LENGTH = None
        self.RECEIVEBUFFER = roboclass.NETWORK.RECEIVEBUFFER
        self.SENDBUFFER = roboclass.NETWORK.SENDBUFFER
        self.ROBOCLASS = roboclass

    def write(self, data):
        raise Exception("Writing not defined for Entity Metadata format")

    def read(self):
        x = MCbyte(self.ROBOCLASS).read(False)
        while not x == 127:
            ty = x >> 5
            if ty == 0:
                MCbyte(self.ROBOCLASS).read()
            if ty == 1:
                MCshort(self.ROBOCLASS).read()
            if ty == 2:
                MCint(self.ROBOCLASS).read()
            if ty == 3:
                MCfloat(self.ROBOCLASS).read()
            if ty == 4:
                MCstring(self.ROBOCLASS).read()
            if ty == 5:
                MCslot(self.ROBOCLASS).read()
            if ty == 6:
                MCint(self.ROBOCLASS).read()
                MCint(self.ROBOCLASS).read()
                MCint(self.ROBOCLASS).read()
            x = MCbyte(self.ROBOCLASS).read(False)

# *** PACKET PROCESSING CODE ***

class packet_template():
    def load(self, roboclass):
        self.ROBOCLASS = roboclass
        self.variables()
        self.ROBOCLASS.NETWORK.PACKETS.PACKETSIGNALS.newsignal(self.ID)
        self.LOGGER = roboclass.LOGGINGTOOLS.makelogger(''.join(['Network.Packets.', hex(self.ID)[2:].upper()]))

    def variables(self):
        self.NAME = "Template"
        self.ID = 0x00 # Put an integer protocol header ID here like 0x00 for Keep Alive

    def linksignals(self):
        pass

    def read(self):
        raise Exception("Reading not programmed for packet "+self.NAME)

    def write(self):
        raise Exception("Writing not programmed for packet "+self.NAME)

class packet00(packet_template):
    def variables(self):
        self.NAME = "Keep Alive"
        self.ID = 0x00
        self.KEEPALIVEVALUE = None

    def linksignals(self):
        self.ROBOCLASS.NETWORK.PACKETS.PACKETSIGNALS.getsignal(0x00).addreceiver(self.ROBOCLASS.NETWORK.PACKETS.send, {'packetid': 0x00})

    def read(self):
        self.KEEPALIVEVALUE = MCint(self.ROBOCLASS).read()

    def write(self):
        MCint(self.ROBOCLASS).write(self.KEEPALIVEVALUE)

class packet01(packet_template):
    def variables(self):
        self.NAME = "Login Request"
        self.ID = 0x01

    def read(self):
        self.ROBOCLASS.CHARACTER.ENTITYID = MCint(self.ROBOCLASS).read()
        self.ROBOCLASS.WORLD.LEVELTYPE = MCstring(self.ROBOCLASS).read()
        self.ROBOCLASS.CHARACTER.GAMEMODE = MCbyte(self.ROBOCLASS).read()
        self.ROBOCLASS.WORLD.DIMENSION = MCbyte(self.ROBOCLASS).read()
        self.ROBOCLASS.CHARACTER.DIFFICULTY = MCbyte(self.ROBOCLASS).read()
        MCbyte(self.ROBOCLASS).read()
        self.ROBOCLASS.WORLD.MAXPLAYERS = MCbyte(self.ROBOCLASS).read()

    def linksignals(self):
        self.ROBOCLASS.NETWORK.PACKETS.PACKETSIGNALS.getsignal(0x01).addreceiver(self.ROBOCLASS.CLOCKTHREAD.start)

class packet02(packet_template):
    def variables(self):
        self.NAME = "Handshake"
        self.ID = 0x02

    def write(self):
        MCbyte(self.ROBOCLASS).write(constants.Protocolver)
        MCstring(self.ROBOCLASS).write(self.ROBOCLASS.USERNAME)
        MCstring(self.ROBOCLASS).write(self.ROBOCLASS.HOST)
        MCint(self.ROBOCLASS).write(self.ROBOCLASS.PORT)

class packet03(packet_template):
    def variables(self):
        self.NAME = "Chat Message"
        self.ID = 0x03

    def read(self):
        self.LOGGER.info("Message: "+MCstring(self.ROBOCLASS).read())

class packet04(packet_template):
    def variables(self):
        self.NAME = "Time Update"
        self.ID = 0x04

    def read(self):
        self.ROBOCLASS.WORLD.AGE = MClong(self.ROBOCLASS).read()
        self.ROBOCLASS.WORLD.TIME = MClong(self.ROBOCLASS).read()

class packet05(packet_template):
    def variables(self):
        self.NAME = "Entity Equipment"
        self.ID = 0x05

    def read(self):
        MCint(self.ROBOCLASS).read()
        MCshort(self.ROBOCLASS).read()
        MCslot(self.ROBOCLASS).read()

class packet06(packet_template):
    def variables(self):
        self.NAME = "Spawn Position"
        self.ID = 0x06

    def read(self):
        MCint(self.ROBOCLASS).read()
        MCint(self.ROBOCLASS).read()
        MCint(self.ROBOCLASS).read()

class packet07(packet_template):
    def variables(self):
        self.NAME = "Use Entity"
        self.ID = 0x07

class packet08(packet_template):
    def variables(self):
        self.NAME = "Update Health"
        self.ID = 0x08

    def read(self):
        print("Got Health Update!")
        self.ROBOCLASS.CHARACTER.HEALTH = MCshort(self.ROBOCLASS).read()
        self.ROBOCLASS.CHARACTER.FOOD = MCshort(self.ROBOCLASS).read()
        self.ROBOCLASS.CHARACTER.FOODSATURATION = MCfloat(self.ROBOCLASS).read()

class packet09(packet_template):
    def variables(self):
        self.NAME = "Respawn"
        self.ID = 0x09

    def read(self):
        self.ROBOCLASS.WORLD.DIMENSION = MCint(self.ROBOCLASS).read()
        self.ROBOCLASS.CHARACTER.DIFFICULTY = MCbyte(self.ROBOCLASS).read()
        self.ROBOCLASS.CHARACTER.GAMEMODE = MCbyte(self.ROBOCLASS).read()
        self.ROBOCLASS.WORLD.BUILDLIMIT = MCshort(self.ROBOCLASS).read()
        self.ROBOCLASS.WORLD.LEVELTYPE = MCstring(self.ROBOCLASS).read()

class packet0A(packet_template):
    def variables(self):
        self.NAME = "Player"
        self.ID = 0x0A

    def write(self):
        MCbool(self.ROBOCLASS).write(self.ROBOCLASS.CHARACTER.ONGROUND)

    def linksignals(self):
        self.ROBOCLASS.MAINSIGNALS.getsignal("clockupdate").addreceiver(self.ROBOCLASS.NETWORK.PACKETS.send, {'packetid': 0x0A})

class packet0B(packet_template):
    def variables(self):
        self.NAME = "Player Position"
        self.ID = 0x0B

    def write(self):
        MCdouble(self.ROBOCLASS).write(self.ROBOCLASS.CHARACTER.X)
        MCdouble(self.ROBOCLASS).write(self.ROBOCLASS.CHARACTER.Y)
        MCdouble(self.ROBOCLASS).write(self.ROBOCLASS.CHARACTER.STANCE)
        MCdouble(self.ROBOCLASS).write(self.ROBOCLASS.CHARACTER.Z)
        MCbool(self.ROBOCLASS).write(self.ROBOCLASS.CHARACTER.ONGROUND)

class packet0C(packet_template):
    def variables(self):
        self.NAME = "Player Look"
        self.ID = 0x0C

class packet0D(packet_template):
    def variables(self):
        self.NAME = "Player Position and Look"
        self.ID = 0x0D

    def read(self):
        self.ROBOCLASS.CHARACTER.X = MCdouble(self.ROBOCLASS).read()
        self.ROBOCLASS.CHARACTER.STANCE = MCdouble(self.ROBOCLASS).read()
        self.ROBOCLASS.CHARACTER.Y = MCdouble(self.ROBOCLASS).read()
        self.ROBOCLASS.CHARACTER.Z = MCdouble(self.ROBOCLASS).read()
        self.ROBOCLASS.CHARACTER.YAW = MCfloat(self.ROBOCLASS).read()
        self.ROBOCLASS.CHARACTER.PITCH = MCfloat(self.ROBOCLASS).read()
        self.ROBOCLASS.CHARACTER.ONGROUND = MCbool(self.ROBOCLASS).read()

    def write(self):
        MCdouble(self.ROBOCLASS).write(self.ROBOCLASS.CHARACTER.X)
        MCdouble(self.ROBOCLASS).write(self.ROBOCLASS.CHARACTER.Y)
        MCdouble(self.ROBOCLASS).write(self.ROBOCLASS.CHARACTER.STANCE)
        MCdouble(self.ROBOCLASS).write(self.ROBOCLASS.CHARACTER.Z)
        MCfloat(self.ROBOCLASS).write(self.ROBOCLASS.CHARACTER.YAW)
        MCfloat(self.ROBOCLASS).write(self.ROBOCLASS.CHARACTER.PITCH)
        MCbool(self.ROBOCLASS).write(self.ROBOCLASS.CHARACTER.ONGROUND)

    def linksignals(self):
        self.ROBOCLASS.NETWORK.PACKETS.PACKETSIGNALS.getsignal(0x0D).addreceiver(self.ROBOCLASS.NETWORK.PACKETS.send, {'packetid': 0x0D})

class packet0E(packet_template):
    def variables(self):
        self.NAME = "Player Digging"
        self.ID = 0x0E

class packet0F(packet_template):
    def variables(self):
        self.NAME = "Player Block Placement"
        self.ID = 0x0F

class packet10(packet_template):
    def variables(self):
        self.NAME = "Held Item Change"
        self.ID = 0x10

    def read(self):
        MCshort(self.ROBOCLASS).read()

class packet11(packet_template):
    def variables(self):
        self.NAME = "Use Bed"
        self.ID = 0x11

class packet12(packet_template):
    def variables(self):
        self.NAME = "Animation"
        self.ID = 0x12

    def read(self):
        MCint(self.ROBOCLASS).read()
        MCbyte(self.ROBOCLASS).read()

class packet13(packet_template):
    def variables(self):
        self.NAME = "Entity Action"
        self.ID = 0x13

class packet14(packet_template):
    def variables(self):
        self.NAME = "Spawn Named Entity"
        self.ID = 0x14

    def read(self):
        MCint(self.ROBOCLASS).read()
        MCstring(self.ROBOCLASS).read()
        MCint(self.ROBOCLASS).read()
        MCint(self.ROBOCLASS).read()
        MCint(self.ROBOCLASS).read()
        MCbyte(self.ROBOCLASS).read()
        MCbyte(self.ROBOCLASS).read()
        MCshort(self.ROBOCLASS).read()
        MCentitymetadata(self.ROBOCLASS).read()

class packet16(packet_template):
    def variables(self):
        self.NAME = "Collect Item"
        self.ID = 0x16

    def read(self):
        MCint(self.ROBOCLASS).read()
        MCint(self.ROBOCLASS).read()

class packet17(packet_template):
    def variables(self):
        self.NAME = "Spawn Object/Vehicle"
        self.ID = 0x17

    def read(self):
        MCint(self.ROBOCLASS).read()
        MCbyte(self.ROBOCLASS).read()
        MCint(self.ROBOCLASS).read()
        MCint(self.ROBOCLASS).read()
        MCint(self.ROBOCLASS).read()
        MCbyte(self.ROBOCLASS).read()
        MCbyte(self.ROBOCLASS).read()
        MCobjectdata(self.ROBOCLASS).read()

class packet18(packet_template):
    def variables(self):
        self.NAME = "Spawn Mob"
        self.ID = 0x18

    def read(self):
        MCint(self.ROBOCLASS).read()
        MCbyte(self.ROBOCLASS).read()
        MCint(self.ROBOCLASS).read()
        MCint(self.ROBOCLASS).read()
        MCint(self.ROBOCLASS).read()
        MCbyte(self.ROBOCLASS).read()
        MCbyte(self.ROBOCLASS).read()
        MCbyte(self.ROBOCLASS).read()
        MCshort(self.ROBOCLASS).read()
        MCshort(self.ROBOCLASS).read()
        MCshort(self.ROBOCLASS).read()
        MCentitymetadata(self.ROBOCLASS).read()

class packet19(packet_template):
    def variables(self):
        self.NAME = "Spawn Painting"
        self.ID = 0x19

    def read(self):
        MCint(self.ROBOCLASS).read()
        MCstring(self.ROBOCLASS).read()
        MCint(self.ROBOCLASS).read()
        MCint(self.ROBOCLASS).read()
        MCint(self.ROBOCLASS).read()
        MCint(self.ROBOCLASS).read()

class packet1A(packet_template):
    def variables(self):
        self.NAME = "Spawn Experience Orb"
        self.ID = 0x1A

    def read(self):
        MCint(self.ROBOCLASS).read()
        MCint(self.ROBOCLASS).read()
        MCint(self.ROBOCLASS).read()
        MCint(self.ROBOCLASS).read()
        MCshort(self.ROBOCLASS).read()

class packet1C(packet_template):
    def variables(self):
        self.NAME = "Entity Velocity"
        self.ID = 0x1C

    def read(self):
        MCint(self.ROBOCLASS).read()
        MCshort(self.ROBOCLASS).read()
        MCshort(self.ROBOCLASS).read()
        MCshort(self.ROBOCLASS).read()

class packet1D(packet_template):
    def variables(self):
        self.NAME = "Destroy Entity"
        self.ID = 0x1D

    def read(self):
        count = MCbyte(self.ROBOCLASS).read()
        for number in range(0, count):
            MCint(self.ROBOCLASS).read()

class packet1E(packet_template):
    def variables(self):
        self.NAME = "Entity"
        self.ID = 0x1E

    def read(self):
        MCint(self.ROBOCLASS).read()

class packet1F(packet_template):
    def variables(self):
        self.NAME = "Entity Relative Move"
        self.ID = 0x1F

    def read(self):
        MCint(self.ROBOCLASS).read()
        MCbyte(self.ROBOCLASS).read()
        MCbyte(self.ROBOCLASS).read()
        MCbyte(self.ROBOCLASS).read()

class packet20(packet_template):
    def variables(self):
        self.NAME = "Entity Look"
        self.ID = 0x20

    def read(self):
        MCint(self.ROBOCLASS).read()
        MCbyte(self.ROBOCLASS).read()
        MCbyte(self.ROBOCLASS).read()

class packet21(packet_template):
    def variables(self):
        self.NAME = "Entity Look and Relative Move"
        self.ID = 0x21

    def read(self):
        MCint(self.ROBOCLASS).read()
        MCbyte(self.ROBOCLASS).read()
        MCbyte(self.ROBOCLASS).read()
        MCbyte(self.ROBOCLASS).read()
        MCbyte(self.ROBOCLASS).read()
        MCbyte(self.ROBOCLASS).read()

class packet22(packet_template):
    def variables(self):
        self.NAME = "Entity Teleport"
        self.ID = 0x22

    def read(self):
        MCint(self.ROBOCLASS).read()
        MCint(self.ROBOCLASS).read()
        MCint(self.ROBOCLASS).read()
        MCint(self.ROBOCLASS).read()
        MCbyte(self.ROBOCLASS).read()
        MCbyte(self.ROBOCLASS).read()

class packet23(packet_template):
    def variables(self):
        self.NAME = "Entity Head Look"
        self.ID = 0x23

    def read(self):
        MCint(self.ROBOCLASS).read()
        MCbyte(self.ROBOCLASS).read()

class packet26(packet_template):
    def variables(self):
        self.NAME = "Entity Status"
        self.ID = 0x26

    def read(self):
        MCint(self.ROBOCLASS).read()
        MCbyte(self.ROBOCLASS).read()

class packet27(packet_template):
    def variables(self):
        self.NAME = "Attach Entity"
        self.ID = 0x27

    def read(self):
        MCint(self.ROBOCLASS).read()
        MCint(self.ROBOCLASS).read()

class packet28(packet_template):
    def variables(self):
        self.NAME = "Entity Metadata"
        self.ID = 0x28

    def read(self):
        MCint(self.ROBOCLASS).read()
        MCentitymetadata(self.ROBOCLASS).read()

class packet29(packet_template):
    def variables(self):
        self.NAME = "Entity Effect"
        self.ID = 0x29

    def read(self):
        MCint(self.ROBOCLASS).read()
        MCbyte(self.ROBOCLASS).read()
        MCbyte(self.ROBOCLASS).read()
        MCshort(self.ROBOCLASS).read()

class packet2A(packet_template):
    def variables(self):
        self.NAME = "Remove Entity Effect"
        self.ID = 0x2A

    def read(self):
        MCint(self.ROBOCLASS).read()
        MCbyte(self.ROBOCLASS).read()

class packet2B(packet_template):
    def variables(self):
        self.NAME = "Set Experience"
        self.ID = 0x2B

    def read(self):
        self.ROBOCLASS.CHARACTER.XPBAR = MCfloat(self.ROBOCLASS).read()
        self.ROBOCLASS.CHARACTER.XPLEVEL = MCshort(self.ROBOCLASS).read()
        self.ROBOCLASS.CHARACTER.XPTOTAL = MCshort(self.ROBOCLASS).read()

class packet33(packet_template):
    def variables(self):
        self.NAME = "Chunk Data"
        self.ID = 0x33

    def read(self):
        MCint(self.ROBOCLASS).read()
        MCint(self.ROBOCLASS).read()
        MCbool(self.ROBOCLASS).read()
        MCshort(self.ROBOCLASS).read(False)
        MCshort(self.ROBOCLASS).read(False)
        MCintdata(self.ROBOCLASS).read()

class packet34(packet_template):
    def variables(self):
        self.NAME = "Multi Block Change"
        self.ID = 0x34

    def read(self):
        MCint(self.ROBOCLASS).read()
        MCint(self.ROBOCLASS).read()
        MCshort(self.ROBOCLASS).read()
        MCintdata(self.ROBOCLASS).read()

class packet35(packet_template):
    def variables(self):
        self.NAME = "Block Change"
        self.ID = 0x35

    def read(self):
        MCint(self.ROBOCLASS).read()
        MCbyte(self.ROBOCLASS).read()
        MCint(self.ROBOCLASS).read()
        MCshort(self.ROBOCLASS).read()
        MCbyte(self.ROBOCLASS).read()

class packet36(packet_template):
    def variables(self):
        self.NAME = "Block Action"
        self.ID = 0x36

    def read(self):
        MCint(self.ROBOCLASS).read()
        MCshort(self.ROBOCLASS).read()
        MCint(self.ROBOCLASS).read()
        MCbyte(self.ROBOCLASS).read()
        MCbyte(self.ROBOCLASS).read()
        MCshort(self.ROBOCLASS).read()

class packet37(packet_template):
    def variables(self):
        self.NAME = "Block Action"
        self.ID = 0x37

    def read(self):
        MCint(self.ROBOCLASS).read()
        MCint(self.ROBOCLASS).read()
        MCint(self.ROBOCLASS).read()
        MCint(self.ROBOCLASS).read()
        MCbyte(self.ROBOCLASS).read()

class packet38(packet_template):
    def variables(self):
        self.NAME = "Map Chunk Bulk"
        self.ID = 0x38

    def read(self):
        count = MCshort(self.ROBOCLASS).read()
        datalength = MCint(self.ROBOCLASS).read()
        MCbool(self.ROBOCLASS).read()
        MCbytearray(self.ROBOCLASS).read(datalength)
        for number in range(0, count):
            MCint(self.ROBOCLASS).read()
            MCint(self.ROBOCLASS).read()
            MCshort(self.ROBOCLASS).read(False)
            MCshort(self.ROBOCLASS).read(False)

class packet3C(packet_template):
    def variables(self):
        self.NAME = "Explosion"
        self.ID = 0x3C

    def read(self):
        MCdouble(self.ROBOCLASS).read()
        MCdouble(self.ROBOCLASS).read()
        MCdouble(self.ROBOCLASS).read()
        MCfloat(self.ROBOCLASS).read()
        count = MCint(self.ROBOCLASS).read()
        for number in range(0, count):
            MCbyte(self.ROBOCLASS).read()
            MCbyte(self.ROBOCLASS).read()
            MCbyte(self.ROBOCLASS).read()
        MCfloat(self.ROBOCLASS).read()
        MCfloat(self.ROBOCLASS).read()
        MCfloat(self.ROBOCLASS).read()

class packet3D(packet_template):
    def variables(self):
        self.NAME = "Sound or Particle Effect"
        self.ID = 0x3D

    def read(self):
        MCint(self.ROBOCLASS).read()
        MCint(self.ROBOCLASS).read()
        MCbyte(self.ROBOCLASS).read()
        MCint(self.ROBOCLASS).read()
        MCint(self.ROBOCLASS).read()
        MCbool(self.ROBOCLASS).read()

class packet3E(packet_template):
    def variables(self):
        self.NAME = "Named Sound Effect"
        self.ID = 0x3E

    def read(self):
        MCstring(self.ROBOCLASS).read()
        MCint(self.ROBOCLASS).read()
        MCint(self.ROBOCLASS).read()
        MCint(self.ROBOCLASS).read()
        MCfloat(self.ROBOCLASS).read()
        MCbyte(self.ROBOCLASS).read()

class packet46(packet_template):
    def variables(self):
        self.NAME = "Change Game State"
        self.ID = 0x46

    def read(self):
        MCbyte(self.ROBOCLASS).read()
        self.ROBOCLASS.CHARACTER.GAMEMODE = MCbyte(self.ROBOCLASS).read()

class packet47(packet_template):
    def variables(self):
        self.NAME = "Global Entity"
        self.ID = 0x47

    def read(self):
        MCint(self.ROBOCLASS).read()
        MCbyte(self.ROBOCLASS).read()
        MCint(self.ROBOCLASS).read()
        MCint(self.ROBOCLASS).read()
        MCint(self.ROBOCLASS).read()

class packet64(packet_template):
    def variables(self):
        self.NAME = "Open Window"
        self.ID = 0x64

    def read(self):
        MCbyte(self.ROBOCLASS).read()
        MCbyte(self.ROBOCLASS).read()
        MCstring(self.ROBOCLASS).read()
        MCbyte(self.ROBOCLASS).read()

class packet65(packet_template):
    def variables(self):
        self.NAME = "Close Window"
        self.ID = 0x65

    def read(self):
        MCbyte(self.ROBOCLASS).read()

class packet66(packet_template):
    def variables(self):
        self.NAME = "Click Window"
        self.ID = 0x66

class packet67(packet_template):
    def variables(self):
        self.NAME = "Set Slot"
        self.ID = 0x67

    def read(self):
        MCbyte(self.ROBOCLASS).read()
        MCshort(self.ROBOCLASS).read()
        MCslot(self.ROBOCLASS).read()

class packet68(packet_template):
    def variables(self):
        self.NAME = "Set Window Items"
        self.ID = 0x68

    def read(self):
        MCbyte(self.ROBOCLASS).read()
        count = MCshort(self.ROBOCLASS).read()
        for number in range(0, count):
            MCslot(self.ROBOCLASS).read()

class packet69(packet_template):
    def variables(self):
        self.NAME = "Update Window Property"
        self.ID = 0x69

    def read(self):
        MCbyte(self.ROBOCLASS).read()
        MCshort(self.ROBOCLASS).read()
        MCshort(self.ROBOCLASS).read()

class packet6A(packet_template):
    def variables(self):
        self.NAME = "Confirm Transaction"
        self.ID = 0x6A

    def read(self):
        MCbyte(self.ROBOCLASS).read()
        MCshort(self.ROBOCLASS).read()
        MCbool(self.ROBOCLASS).read()

class packet6B(packet_template):
    def variables(self):
        self.NAME = "Creative Inventory Action"
        self.ID = 0x6B

    def read(self):
        MCshort(self.ROBOCLASS).read()
        MCslot(self.ROBOCLASS).read()

class packet6C(packet_template):
    def variables(self):
        self.NAME = "Enchant Item"
        self.ID = 0x6C

    def read(self):
        MCbyte(self.ROBOCLASS).read()
        MCbyte(self.ROBOCLASS).read()

class packet82(packet_template):
    def variables(self):
        self.NAME = "Update Sign"
        self.ID = 0x82

    def read(self):
        MCint(self.ROBOCLASS).read()
        MCshort(self.ROBOCLASS).read()
        MCint(self.ROBOCLASS).read()
        MCstring(self.ROBOCLASS).read()
        MCstring(self.ROBOCLASS).read()
        MCstring(self.ROBOCLASS).read()
        MCstring(self.ROBOCLASS).read()

class packet83(packet_template):
    def variables(self):
        self.NAME = "Item Data"
        self.ID = 0x83

    def read(self):
        MCshort(self.ROBOCLASS).read()
        MCshort(self.ROBOCLASS).read()
        MCshortdata(self.ROBOCLASS).read()

class packet84(packet_template):
    def variables(self):
        self.NAME = "Update Tile Entity"
        self.ID = 0x84

    def read(self):
        MCint(self.ROBOCLASS).read()
        MCshort(self.ROBOCLASS).read()
        MCint(self.ROBOCLASS).read()
        MCbyte(self.ROBOCLASS).read()
        MCshortdata(self.ROBOCLASS).read()

class packetC8(packet_template):
    def variables(self):
        self.NAME = "Increment Statistic"
        self.ID = 0xC8

    def read(self):
        MCint(self.ROBOCLASS).read()
        MCbyte(self.ROBOCLASS).read()

class packetC9(packet_template):
    def variables(self):
        self.NAME = "Player List Item"
        self.ID = 0xC9

    def read(self):
        MCstring(self.ROBOCLASS).read()
        MCbool(self.ROBOCLASS).read()
        MCshort(self.ROBOCLASS).read()

class packetCA(packet_template):
    def variables(self):
        self.NAME = "Player Abilities"
        self.ID = 0xCA

    def read(self):
        MCbyte(self.ROBOCLASS).read()
        MCbyte(self.ROBOCLASS).read()
        MCbyte(self.ROBOCLASS).read()

class packetCB(packet_template):
    def variables(self):
        self.NAME = "Tab-complete"
        self.ID = 0xCB

    def read(self):
        MCstring(self.ROBOCLASS).read()

class packetCC(packet_template):
    def variables(self):
        self.NAME = "Client Settings"
        self.ID = 0xCC

class packetCD(packet_template):
    def variables(self):
        self.NAME = "Client Statuses"
        self.ID = 0xCD
        self.ISRESPAWNING = False

    def write(self):
        MCbyte(self.ROBOCLASS).write(self.ISRESPAWNING)
        if not self.ISRESPAWNING:
            self.ISRESPAWNING = True

class packetFA(packet_template):
    def variables(self):
        self.NAME = "Plugin Message"
        self.ID = 0xFA

    def read(self):
        MCstring(self.ROBOCLASS).read()
        MCshortdata(self.ROBOCLASS).read()

class packetFC(packet_template):
    def variables(self):
        self.NAME = "Encryption Key Response"
        self.ID = 0xFC

    def read(self):
        MCshortdata(self.ROBOCLASS).read()
        MCshortdata(self.ROBOCLASS).read()
        self.ROBOCLASS.NETWORK.CONNECTION.ENCRYPTION.ENCRYPTION_ENABLED = True

    def write(self):
        encryptedaeskey = self.ROBOCLASS.NETWORK.CONNECTION.ENCRYPTION.PKCSencrypt(self.ROBOCLASS.NETWORK.CONNECTION.ENCRYPTION.AESKEY)
        encryptedtoken = self.ROBOCLASS.NETWORK.CONNECTION.ENCRYPTION.PKCSencrypt(self.ROBOCLASS.NETWORK.CONNECTION.ENCRYPTION.VERIFICATIONTOKEN)
        MCshortdata(self.ROBOCLASS).write(encryptedaeskey)
        MCshortdata(self.ROBOCLASS).write(encryptedtoken)

    def linksignals(self):
        self.ROBOCLASS.NETWORK.PACKETS.PACKETSIGNALS.getsignal(0xFC).addreceiver(self.ROBOCLASS.NETWORK.PACKETS.send, {'packetid': 0xCD})

class packetFD(packet_template):
    def variables(self):
        self.NAME = "Encryption Key Request"
        self.ID = 0xFD

    def read(self):
        MCstring(self.ROBOCLASS).read()
        self.ROBOCLASS.NETWORK.CONNECTION.ENCRYPTION.ENCODEDPUBLICKEY = MCshortdata(self.ROBOCLASS).read()
        self.ROBOCLASS.NETWORK.CONNECTION.ENCRYPTION.VERIFICATIONTOKEN = MCshortdata(self.ROBOCLASS).read()

    def linksignals(self):
        if constants.EnableEncryption:
            self.ROBOCLASS.NETWORK.PACKETS.PACKETSIGNALS.getsignal(0xFD).addreceiver(self.ROBOCLASS.NETWORK.CONNECTION.ENCRYPTION.makePKCSCIPHER)
            self.ROBOCLASS.NETWORK.PACKETS.PACKETSIGNALS.getsignal(0xFD).addreceiver(self.ROBOCLASS.NETWORK.CONNECTION.ENCRYPTION.generateAES)
            self.ROBOCLASS.NETWORK.PACKETS.PACKETSIGNALS.getsignal(0xFD).addreceiver(self.ROBOCLASS.NETWORK.PACKETS.send, {'packetid': 0xFC})
        else:
            print("Encryption is Disabled")
            self.ROBOCLASS.NETWORK.PACKETS.PACKETSIGNALS.getsignal(0xFD).addreceiver(self.ROBOCLASS.NETWORK.PACKETS.send, {'packetid': 0xCD})

class packetFE(packet_template):
    pass

class packetFF(packet_template):
    def variables(self):
        self.NAME = "Disconnect/Kick"
        self.ID = 0xFF

    def read(self):
        self.LOGGER.info("Message: "+MCstring(self.ROBOCLASS).read())
        self.ROBOCLASS.MAINSIGNALS.emit('stop')

    def linksignals(self):
        self.ROBOCLASS.NETWORK.PACKETS.PACKETSIGNALS.getsignal(0xFF).addreceiver(self.ROBOCLASS.MAINSIGNALS.emit, {'signame': 'stop'})

class manager():
    def load(self, roboclass):
        self.ROBOCLASS = roboclass

        self.PACKETSIGNALS = self.ROBOCLASS.INTERNALIB.signalmanager()
        self.PACKETSIGNALS.newsignal("start")
        self.PACKETSIGNALS.getsignal("start").addreceiver(self.send, {'packetid': 0x02})

        self.SENDLISTQUEUE = queue.Queue()

        self.LOGGER = roboclass.LOGGINGTOOLS.makelogger("Network.Packets")

        self.PACKETHANDLERS = dict()
        self.PACKETHANDLERS[0x00] = packet00()
        self.PACKETHANDLERS[0x01] = packet01()
        self.PACKETHANDLERS[0x02] = packet02()
        self.PACKETHANDLERS[0x03] = packet03()
        self.PACKETHANDLERS[0x04] = packet04()
        self.PACKETHANDLERS[0x05] = packet05()
        self.PACKETHANDLERS[0x06] = packet06()
        self.PACKETHANDLERS[0x07] = packet07()
        self.PACKETHANDLERS[0x08] = packet08()
        self.PACKETHANDLERS[0x09] = packet09()
        self.PACKETHANDLERS[0x0A] = packet0A()
        self.PACKETHANDLERS[0x0B] = packet0B()
        self.PACKETHANDLERS[0x0C] = packet0C()
        self.PACKETHANDLERS[0x0D] = packet0D()
        self.PACKETHANDLERS[0x0E] = packet0E()
        self.PACKETHANDLERS[0x0F] = packet0F()
        self.PACKETHANDLERS[0x10] = packet10()
        self.PACKETHANDLERS[0x11] = packet11()
        self.PACKETHANDLERS[0x12] = packet12()
        self.PACKETHANDLERS[0x13] = packet13()
        self.PACKETHANDLERS[0x14] = packet14()
        self.PACKETHANDLERS[0x16] = packet16()
        self.PACKETHANDLERS[0x17] = packet17()
        self.PACKETHANDLERS[0x18] = packet18()
        self.PACKETHANDLERS[0x19] = packet19()
        self.PACKETHANDLERS[0x1A] = packet1A()
        self.PACKETHANDLERS[0x1C] = packet1C()
        self.PACKETHANDLERS[0x1D] = packet1D()
        self.PACKETHANDLERS[0x1E] = packet1E()
        self.PACKETHANDLERS[0x1F] = packet1F()
        self.PACKETHANDLERS[0x20] = packet20()
        self.PACKETHANDLERS[0x21] = packet21()
        self.PACKETHANDLERS[0x22] = packet22()
        self.PACKETHANDLERS[0x23] = packet23()
        self.PACKETHANDLERS[0x26] = packet26()
        self.PACKETHANDLERS[0x27] = packet27()
        self.PACKETHANDLERS[0x28] = packet28()
        self.PACKETHANDLERS[0x29] = packet29()
        self.PACKETHANDLERS[0x2A] = packet2A()
        self.PACKETHANDLERS[0x2B] = packet2B()
        self.PACKETHANDLERS[0x33] = packet33()
        self.PACKETHANDLERS[0x34] = packet34()
        self.PACKETHANDLERS[0x35] = packet35()
        self.PACKETHANDLERS[0x36] = packet36()
        self.PACKETHANDLERS[0x37] = packet37()
        self.PACKETHANDLERS[0x38] = packet38()
        self.PACKETHANDLERS[0x3C] = packet3C()
        self.PACKETHANDLERS[0x3D] = packet3D()
        self.PACKETHANDLERS[0x3E] = packet3E()
        self.PACKETHANDLERS[0x46] = packet46()
        self.PACKETHANDLERS[0x47] = packet47()
        self.PACKETHANDLERS[0x64] = packet64()
        self.PACKETHANDLERS[0x65] = packet65()
        self.PACKETHANDLERS[0x66] = packet66()
        self.PACKETHANDLERS[0x67] = packet67()
        self.PACKETHANDLERS[0x68] = packet68()
        self.PACKETHANDLERS[0x69] = packet69()
        self.PACKETHANDLERS[0x6A] = packet6A()
        self.PACKETHANDLERS[0x6B] = packet6B()
        self.PACKETHANDLERS[0x6C] = packet6C()
        self.PACKETHANDLERS[0x82] = packet82()
        self.PACKETHANDLERS[0x83] = packet83()
        self.PACKETHANDLERS[0x84] = packet84()
        self.PACKETHANDLERS[0xC8] = packetC8()
        self.PACKETHANDLERS[0xC9] = packetC9()
        self.PACKETHANDLERS[0xCA] = packetCA()
        self.PACKETHANDLERS[0xCB] = packetCB()
        self.PACKETHANDLERS[0xCC] = packetCC()
        self.PACKETHANDLERS[0xCD] = packetCD()
        self.PACKETHANDLERS[0xFA] = packetFA()
        self.PACKETHANDLERS[0xFC] = packetFC()
        self.PACKETHANDLERS[0xFD] = packetFD()
        self.PACKETHANDLERS[0xFE] = packetFE()
        self.PACKETHANDLERS[0xFF] = packetFF()

        for packethandler in list(self.PACKETHANDLERS.values()):
            packethandler.load(self.ROBOCLASS)
            packethandler.linksignals()

    def start(self):
        self.PACKETSIGNALS.emit("start")

    def read_iteration(self):
        packetid = MCbyte(self.ROBOCLASS).read(False)
        #self.LOGGER.info("Got packet "+hex(packetid))
        #print("Got packet", hex(packetid))
        try:
            self.PACKETHANDLERS[packetid].read()
        except:
            self.LOGGER.exception("Packet reading of packet "+hex(packetid)+" has raised an exception.\nData Dump: "+str(self.ROBOCLASS.NETWORK.RECEIVEBUFFER.BUFFER))
            self.ROBOCLASS.MAINSIGNALS.emit('stop')
        self.PACKETSIGNALS.emit(packetid)

    def send_iteration(self):
        header = self.SENDLISTQUEUE.get()
        MCbyte(self.ROBOCLASS).write(header, False)
        self.PACKETHANDLERS[header].write()
        self.ROBOCLASS.NETWORK.SENDBUFFER.flush()

    def send(self, packetid):
        self.SENDLISTQUEUE.put(packetid)
        #self.LOGGER.info("Sending packet "+hex(packetid))
        #print("Sending packet", hex(packetid))
