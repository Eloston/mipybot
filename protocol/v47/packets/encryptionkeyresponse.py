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

    def receive(self, roboclass):
        # As of this protocol version, the packet we get here doesn't carry anything useful. But to play safe we read the length anyways
        roboclass.PACKETS.POINTER.read('short') # Shared Secret short
        roboclass.PACKETS.POINTER.read('short') # Verification token short
        roboclass.ENCRYPTION.ENCRYPTION_ENABLED = True
        roboclass.PACKETS.send(0xCD)

        return roboclass.PACKETS.POINTER.getposition()
