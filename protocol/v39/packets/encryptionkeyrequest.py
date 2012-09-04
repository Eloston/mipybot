from . import template

class handler(template.handler):
    def __init__(self):
        self.NAME = "Encryption Key Request"
        self.HEADER = 0xFD

    def receive(self, roboclass):
        serverid = roboclass.PACKETS.POINTER.read('string')

        publickey = roboclass.PACKETS.POINTER.read('shortdata')

        token = roboclass.PACKETS.POINTER.read('shortdata')

        roboclass.ENCRYPTION.makePKCSCIPHER(publickey)
        roboclass.ENCRYPTION.SERVERID = serverid
        roboclass.ENCRYPTION.VERIFICATIONTOKEN = token

        roboclass.PACKETS.send(0xFC)

        return roboclass.PACKETS.POINTER.getposition()
