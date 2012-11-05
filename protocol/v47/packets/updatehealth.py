from . import template

class handler(template.handler):
    def __init__(self, *args):
        self.NAME = "Update Health"
        self.HEADER = 0x08

    def receive(self, roboclass):
        hp = roboclass.PACKETS.POINTER.read('short')

        food = roboclass.PACKETS.POINTER.read('short')

        foodsaturation = roboclass.PACKETS.POINTER.read('float')

        healthdict = dict()
        healthdict['hp'] = hp
        healthdict['food'] = food
        healthdict['foodsaturation'] = foodsaturation
        roboclass.CHARACTER.updatehealth(healthdict)
        print("Health stats:\nHP:", hp, "\nFood:", food, "\nFood Saturation", foodsaturation)

        return roboclass.PACKETS.POINTER.getposition()
