from . import template
import struct

class handler():
    def __init__(self, *args):
        self.NAME = "Handshake"
        self.HEADER = 0x02

    def send(self, roboclass):
        protocolver = struct.pack('B', roboclass.PROTOCOL)
        username_length = struct.pack('!h', len(roboclass.USERNAME))
        username = roboclass.USERNAME.encode(roboclass.STRING_ENCODE)
        host_length = struct.pack('!h', len(roboclass.HOST))
        host = roboclass.HOST.encode(roboclass.STRING_ENCODE)
        port = struct.pack('!i', roboclass.PORT)
        return protocolver+username_length+username+host_length+host+port
