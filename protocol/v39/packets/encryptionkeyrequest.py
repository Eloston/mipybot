from . import template
import struct
from Crypto.PublicKey import RSA

class handler(template.handler):
    def __init__(self):
        self.NAME = "Encryption Key Request"
        self.HEADER = 0xFD

    def receive(self, roboclass, data):
        Position = roboclass.SHORT_LENGTH # ServerID short
        serverid_length = struct.unpack('!h', data[:roboclass.SHORT_LENGTH])[0] * 2 # Server ID is a UTF-16be string
        serverid = data[Position:Position+serverid_length].decode(roboclass.STRING_ENCODE)
        Position += serverid_length
        publickey_length = struct.unpack('!h', data[Position:Position+roboclass.SHORT_LENGTH])[0]
        Position += roboclass.SHORT_LENGTH
        publickey = data[Position:Position+publickey_length]
        publickey = RSA.importKey(publickey) # Decode into ASN.1 defined by X.509
        Position += publickey_length
        token_length = struct.unpack("!h", data[Position:Position+roboclass.SHORT_LENGTH])[0]
        Position += roboclass.SHORT_LENGTH
        token = data[Position:Position+token_length]
        Position += token_length
        roboclass.ENCRYPTIONREQUESTLIST = [serverid, publickey, token]
        roboclass.PACKETS.senddata(roboclass, 0xFC)

    def getlength(self, roboclass, data):
        Length = roboclass.SHORT_LENGTH # Header + the server ID short
        Length += struct.unpack('!h', data[:roboclass.SHORT_LENGTH])[0] * 2 # Length of the server ID
        Length += struct.unpack('!h', data[Length:Length+roboclass.SHORT_LENGTH])[0] # Length of the public key
        Length += roboclass.SHORT_LENGTH # Length of the public key short
        Length += struct.unpack('!h', data[Length:Length+roboclass.SHORT_LENGTH])[0] # Length of the verification token
        Length += roboclass.SHORT_LENGTH # Length of the verification token short
        return Length
