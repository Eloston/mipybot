from . import template

class handler(template.handler):
    def __init__(self, *args):
        self.NAME = "Chat Message"
        self.HEADER = 0x03

    def receive(self, roboclass, data):
        print("Message:", roboclass.CONVERTER.getstringdata(data)['string'])

    def getlength(self, roboclass, data):
        return roboclass.CONVERTER.SHORT_LENGTH+roboclass.CONVERTER.getstringdata(data)["length"]
