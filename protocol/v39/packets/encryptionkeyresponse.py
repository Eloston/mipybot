from . import template

class handler(template.handler):
    def __init__(self):
        self.NAME = "Encryption Key Response"
        self.HEADER = 0xFC

    def send(self, roboclass):
        aeskeyenc = roboclass.ENCRYPTION.PKCSencrypt(roboclass.ENCRYPTION.AESKEY)
        tokenenc = roboclass.ENCRYPTION.PKCSencrypt(roboclass.ENCRYPTION.VERIFICATIONTOKEN)

        aeskeyenc_length = roboclass.CONVERTER.makeshort(len(aeskeyenc))
        tokenenc_length = roboclass.CONVERTER.makeshort(len(tokenenc))

        return aeskeyenc_length+aeskeyenc+tokenenc_length+tokenenc

    def receive(self, roboclass, data):
        # As of this protocol version, the packet we get here doesn't carry anything useful.
        roboclass.ENCRYPTION.ENCRYPTION_ENABLED = True
        roboclass.PACKETS.send(0xCD)
        
    def getlength(self, roboclass, data):
        # Note, since this function is only called when this is received from the server, there should be two zero shorts and zero length byte arrays, so the total packet size should be 5. But the server may return something bigger, so we'll play safe.
        Length = roboclass.CONVERTER.getshort(data) # Length of the shared secret
        Length += roboclass.CONVERTER.SHORT_LENGTH # Shared Secret short
        Length += roboclass.CONVERTER.getshort(data, Length) # Length of the verification token
        Length += roboclass.CONVERTER.SHORT_LENGTH # Verification token short
        return Length
