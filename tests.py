# The really messy, ugly, one-file test script used to learn the Minecraft protocol
# This script can be run directly
'''
Information here is using:
http://www.wiki.vg/Protocol
http://www.wiki.vg/Protocol_Encryption
http://www.wiki.vg/Data_Types
https://www.dlitz.net/software/pycrypto/api/current/
https://www.dlitz.net/software/pycrypto/doc/
https://github.com/sadimusi/mc3p
'''
import socket
import struct
import binascii
from Crypto import Random
from Crypto.Cipher import AES, PKCS1_v1_5
from Crypto.PublicKey import RSA
def packetheader(PACKET):
    return int(binascii.hexlify(PACKET[:1]), 16)
def trimheader(PACKET):
    return PACKET[1:]
'''
def createRSAobject(PUBLICKEY):
    return RSA.RSAImplementation().importKey(PUBLICKEY)
'''
def createPKCSobject(PUBLICKEY):
    return PKCS1_v1_5.new(PUBLICKEY)
def generateAES():
    # Just a note, key and IV are the same
    key = Random.new().read(AES.block_size)
    cipher = AES.new(key, AES.MODE_CFB, key)
    return [key, cipher]
def parserecieve(PACKET):
    global ENCRYPTION_ENABLED
    if ENCRYPTION_ENABLED:
        global AESCIPHER
        PACKET = AESCIPHER.decrypt(PACKET)
    if PACKET == b'':
        print("Blank packet?!")
        return None
    packet_type = packetheader(PACKET)
    if packet_type == 0xFD:
        print("Got 0xFD")
        PACKET = trimheader(PACKET)
        #print("Data is (without header):", PACKET)
        Position = 0
        ServerID_length = struct.unpack('!h', PACKET[:SHORT_LENGTH])[0]
        #print("Server ID length is (after decoding):", ServerID_length)
        ServerID_length *= 2 # Need to multiply by two since UTF-16 has 2 bytes per character
        Position += SHORT_LENGTH
        ServerID = PACKET[Position:Position+ServerID_length].decode(STRENC)
        Position += ServerID_length
        #print("Server ID is:", ServerID)
        PublicKey_length = struct.unpack('!h', PACKET[Position:Position+SHORT_LENGTH])[0]
        #print("Public Key length is:", PublicKey_length)
        Position += SHORT_LENGTH
        PublicKey = PACKET[Position:Position+PublicKey_length]
        PublicKey = RSA.importKey(PublicKey) # Decode into ASN.1 defined by X.509
        #print("Public Key is:", PublicKey)
        Position += PublicKey_length
        Token_length = struct.unpack("!h", PACKET[Position:Position+SHORT_LENGTH])[0]
        #print("Verification Token length is:", Token_length)
        Position += SHORT_LENGTH
        Token = PACKET[Position:Position+Token_length]
        #print("Verification Token is:", Token)
        print("Generating PKCS and AES information")
        PKCSObject = createPKCSobject(PublicKey)
        TempAES = generateAES()
        global AESKEY
        AESKEY = TempAES[0]
        global AESCIPHER
        AESCIPHER = TempAES[1]
        del TempAES
        print("Sending Encryption Key Response (0xFC)")
        AESKeyEnc = PKCSObject.encrypt(AESKEY)
        #print("Encrypted AES Key:", AESKeyEnc)
        TokenEnc = PKCSObject.encrypt(Token)
        #print("Encrypted Token Key:", TokenEnc)
        s.send(b'\xFC'+struct.pack('!h', len(AESKeyEnc))+AESKeyEnc+struct.pack('!h', len(TokenEnc))+TokenEnc)
    if packet_type == 0xFC:
        print("Got 0xFC")
        if trimheader(PACKET) == b'\x00\x00\x00\x00':
            print("Encryption Sucessful! Enabling Encryption and sending Client Statuses (0xCD) packet")
            ENCRYPTION_ENABLED = True
            s.send(AESCIPHER.encrypt(b'\xCD\x00'))
        else:
            print("Encryption Unsucessful! Packet contents (with header):", PACKET)
    if packet_type == 0x01:
        print("Got Login!")        
        #print("Got Login! Information:")
        #PACKET = trimheader(PACKET)
    if packet_type == 0xFF:
        print("Got Disconnect!")
        print("Message:", PACKET[3:].decode(STRENC))
    else:
        print("Unknown packet:", hex(packet_type), "|", PACKET)

USERNAME = "MiPyBot"
HOST = "blahblah"
PORT = 25565
STRENC = "UTF-16be"
SHORT_LENGTH = 2
ENCRYPTION_ENABLED = False
AESCIPHER = None
AESKEY = None
# Code below was commented out and defined above to make testing much faster
'''
readbuffer = ''
HOST = input("Host: ")
while True:
    try:
        PORT = int(input("Port: "))
        break
    except:
        print("Not a valid port")
'''
s=socket.socket()
s.connect((HOST, PORT))
# The Minecraft handshake (0x02) packet below
s.send(b'\x02\x27'+struct.pack('!h', len(USERNAME))+bytes(USERNAME.encode(STRENC))+struct.pack('!h', len(HOST))+bytes(HOST.encode(STRENC))+struct.pack('!i', PORT))
receive = s.recv(1024) # We will recieve an Encryption Key Request (0xFD) packet
parserecieve(receive) # Will parse 0xFD
receive = s.recv(1024) # We will receive 0xFC
parserecieve(receive) # We will parse 0xFC
receive = s.recv(1024) # We will receive login or disconnect
parserecieve(receive) # Parse to end the test
