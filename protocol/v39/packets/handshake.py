from . import template

class handler(template.handler):
    def __init__(self, *args):
        self.NAME = "Handshake"
        self.HEADER = 0x02

    def send(self, roboclass):
        protocolver = roboclass.CONVERTER.makebyte(roboclass.NETWORK.PROTOCOL)
        username = roboclass.CONVERTER.makestring(roboclass.CHARACTER.USERNAME)
        host = roboclass.CONVERTER.makestring(roboclass.NETWORK.HOST)
        port = roboclass.CONVERTER.makeinteger(roboclass.NETWORK.PORT)
        return protocolver+username+host+port
