import game
import libtcodpy as libtcod
import decoder

class Equipment:

    MODIFIER_CHANCE = 90
    modifier_decoder = decoder.ModifierDecoder('modifiers/')
    prefixes = modifier_decoder.decode_prefixes()
    postfixes = modifier_decoder.decode_postfixes()

    def __init__(self, slot, power_bonus=0, dexterity_bonus=0, max_hp_bonus=0, accuracy_bonus=0, range_bonus=0, max_mp_bonus=0, mp_regen_bonus=0):
        self.slot = slot
        self.is_equipped = False
        self.power_bonus = power_bonus
        self.dexterity_bonus = dexterity_bonus
        self.max_hp_bonus = max_hp_bonus
        self.accuracy_bonus = accuracy_bonus
        self.range_bonus = range_bonus
        self.max_mp_bonus = max_mp_bonus
        self.mp_regen_bonus = mp_regen_bonus

        self.prefix = self.get_new_prefix()
        self.postfix = self.get_new_postfix()
        self.add_stats(self.postfix)


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
        game.Game.player.fighter.hp += self.max_hp_bonus
        game.Game.player.job.mp += self.max_mp_bonus
        game.Game.message('Equipped ' + self.owner.name + ' on ' + self.slot + '.', libtcod.light_green)

    def dequip(self):
        if not self.is_equipped:
            return
        self.is_equipped = False
        game.Game.player.fighter.hp -= self.max_hp_bonus
        game.Game.player.job.mp -= self.max_mp_bonus
        game.Game.message('Dequipped ' + self.owner.name + ' on ' + self.slot + '.', libtcod.light_yellow)

    def get_equipped_in_slot(self, slot):
        for obj in game.Game.player.inventory:
            if obj.equipment and obj.equipment.slot == slot and obj.equipment.is_equipped:
                return obj.equipment
        return None

    def get_new_prefix(self):
        if libtcod.random_get_int(0, 0, 100) > Equipment.MODIFIER_CHANCE:
            index = libtcod.random_get_int(0, 0, len(Equipment.prefixes) - 1)
            return Equipment.prefixes[index]
        return None

    def get_new_postfix(self):
        if libtcod.random_get_int(0, 0, 100) > Equipment.MODIFIER_CHANCE:
            index = libtcod.random_get_int(0, 0, len(Equipment.postfixes) - 1)
            return Equipment.postfixes[index]
        return None

    def add_stats(self, modifier):
        if modifier is not None:
            for mod in modifier['bonuses']:
                vars(self)[mod['stat']] += mod['amount']

    def reassign_name(self):
        if self.prefix is not None:
            self.owner.name = self.prefix['word'] + ' ' + self.owner.name

        if self.postfix is not None:
            self.owner.name += ' of the ' + self.postfix['word']
