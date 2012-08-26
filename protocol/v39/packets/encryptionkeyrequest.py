from . import template

class handler(template.handler):
    def __init__(self):
        self.NAME = "Encryption Key Request"
        self.HEADER = 0xFD

    def receive(self, roboclass, data):
        serverid_length = roboclass.CONVERTER.getstringdata(data)["length"]
        serverid = roboclass.CONVERTER.getstringdata(data)["string"]
        Position = roboclass.CONVERTER.SHORT_LENGTH # ServerID short
        Position += serverid_length

        publickey_length = roboclass.CONVERTER.getshortdata(data, Position)["length"]
        publickey = roboclass.CONVERTER.getshortdata(data, Position)["data"]
        Position += roboclass.CONVERTER.SHORT_LENGTH
        Position += publickey_length

        token_length = roboclass.CONVERTER.getshortdata(data, Position)["length"]
        token = roboclass.CONVERTER.getshortdata(data, Position)["data"]
        Position += roboclass.CONVERTER.SHORT_LENGTH
        Position += token_length

        roboclass.ENCRYPTION.makePKCSCIPHER(publickey)
        roboclass.ENCRYPTION.SERVERID = serverid
        roboclass.ENCRYPTION.VERIFICATIONTOKEN = token

        roboclass.PACKETS.send(0xFC)

    def getlength(self, roboclass, data):
        Length = roboclass.CONVERTER.SHORT_LENGTH # Server ID short
        Length += roboclass.CONVERTER.getstringdata(data)["length"] # Length of the server ID
        Length += roboclass.CONVERTER.getshort(data, Length) # Length of the public key
        Length += roboclass.CONVERTER.SHORT_LENGTH # Length of the public key short
        Length += roboclass.CONVERTER.getshort(data, Length) # Length of the verification token
        Length += roboclass.CONVERTER.SHORT_LENGTH # Length of the verification token short
        return Length
