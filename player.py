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
            fighter_component.hp += start_equipment.equipment.max_hp_bonus
            self.job.mp += start_equipment.equipment.max_mp_bonus

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
            result = ability['use_function'](self)

            if result != 'cancelled':
                self.job.mp -= ability['cost'] + self.job.mp_regen

    def get_all_equipped(self):
        equipped_list = []
        for item in self.inventory:
            if item.equipment and item.equipment.is_equipped:
                equipped_list.append(item.equipment)
        return equipped_list
