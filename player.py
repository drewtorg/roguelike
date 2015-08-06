from object import Object

class Player(Object):
    def __init__(self, x, y, char, name, color, fighter_component, race, job, start_equipment=None):
        self.level = 1
        self.job = job
        self.race = race
        self.inventory = []
        if start_equipment is not None:
            self.inventory.append(start_equipment)
            start_equipment.equipment.is_equipped = True

        Object.__init__(self, x, y, char, name, color, blocks=True, fighter=fighter_component, race=race)

    def get_range(self):
        equipment = self.fighter.get_all_equipped()
        range = self.fighter.range
        for item in equipment:
            range += item.range_bonus
        return range

    def update(self):
        self.job.update()

    def use_ability(self, ability):
        if ability['cost'] <= self.job.mp:
            ability['use_function']()
            self.job.mp -= ability['cost'] + self.job.mp_regen
