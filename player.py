from object import Object

class Player(Object):
    def __init__(self, x, y, char, name, color, fighter_component):
        self.inventory = []
        self.level = 1

        Object.__init__(self, x, y, char, name, color, blocks=True, fighter=fighter_component)
