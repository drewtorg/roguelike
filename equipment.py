import game
import libtcodpy as libtcod

class Equipment:
    def __init__(self, slot, power_bonus=0, dexterity_bonus=0, max_hp_bonus=0, accuracy_bonus=0, range_bonus=0):
        self.slot = slot
        self.is_equipped = False
        self.power_bonus = power_bonus
        self.dexterity_bonus = dexterity_bonus
        self.max_hp_bonus = max_hp_bonus
        self.accuracy_bonus = accuracy_bonus
        self.range_bonus = range_bonus

    def toggle_equip(self):
        if self.is_equipped:
            self.dequip()
        else:
            self.equip()

    def equip(self):
        old_equipment = self.get_equipped_in_slot(self.slot)
        if old_equipment is not None:
            old_equipment.dequip()

        self.is_equipped = True
        game.Game.message('Equipped ' + self.owner.name + ' on ' + self.slot + '.', libtcod.light_green)

    def dequip(self):
        if not self.is_equipped:
            return
        self.is_equipped = False
        game.Game.message('Dequipped ' + self.owner.name + ' on ' + self.slot + '.', libtcod.light_yellow)

    def get_equipped_in_slot(self, slot):
        for obj in game.Game.player.inventory:
            if obj.equipment and obj.equipment.slot == slot and obj.equipment.is_equipped:
                return obj.equipment
        return None
