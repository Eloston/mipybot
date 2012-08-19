from . import template
import struct
from Crypto.Cipher import PKCS1_v1_5

class handler(template.handler):
    def __init__(self):
        self.NAME = "Encryption Key Response"
        self.HEADER = 0xFC

    def send(self, roboclass):
        roboclass.PKCSCIPHER = PKCS1_v1_5.new(roboclass.ENCRYPTIONREQUESTLIST[1])
        aeskeyenc = roboclass.PKCSCIPHER.encrypt(roboclass.AESKEY)
        tokenenc = roboclass.PKCSCIPHER.encrypt(roboclass.ENCRYPTIONREQUESTLIST[2])
        aeskeyenc_length = struct.pack('!h', len(aeskeyenc))
        tokenenc_length = struct.pack('!h', len(tokenenc))
        return aeskeyenc_length+aeskeyenc+tokenenc_length+tokenenc

    def receive(self, roboclass, data):
        # As of this protocol version, the packet we get here doesn't carry anything useful.
        roboclass.ENCRYPTION_ENABLED = True
        roboclass.PACKETS.senddata(roboclass, 0xCD)
        
    def getlength(self, roboclass, data):
        # Note, since this function is only called when this is received from the server, there should be two zero shorts and zero length byte arrays, so the total packet size should be 5. But the server may return something bigger, so we'll play safe.
        Length = roboclass.SHORT_LENGTH # Server ID short
        Length += struct.unpack('!h', data[:roboclass.SHORT_LENGTH])[0] # Length of the shared secret
        Length += roboclass.SHORT_LENGTH # Length of the verification token short
        Length += struct.unpack('!h', data[:roboclass.SHORT_LENGTH])[0] # Length of the verification token
        return Length
