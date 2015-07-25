import libtcodpy as libtcod
import components as Components
import equipment
import object
import json
import glob

class Decoder:
    def __init__(self, path):
        self.path = path

    def decode(self, file):
        decodeFile = open(self.path + file + '.json')
        decodeString = decodeFile.read()
        return json.loads(decodeString, object_hook=self._decode_dict)

    def decode_spawn_chance(self, file):
        dict = self.decode(file)
        return dict['spawn_chance']

    def decode_all_spawn_chances(self):
        spawn_chances = {}
        for file in glob.glob(self.path + '/*.json'):
            fileName = file.split('/')[-1]
            enemyName = fileName.split('.')[0]
            spawn_chances[enemyName] = self.decode_spawn_chance(enemyName)
        return spawn_chances

    def _decode_list(self, data):
        rv = []
        for item in data:
            if isinstance(item, unicode):
                item = item.encode('utf-8')
            elif isinstance(item, list):
                item = self._decode_list(item)
            elif isinstance(item, dict):
                item = self._decode_dict(item)
            rv.append(item)
        return rv

    def _decode_dict(self, data):
        rv = {}
        for key, value in data.iteritems():
            if isinstance(key, unicode):
                key = key.encode('utf-8')
            if isinstance(value, unicode):
                value = value.encode('utf-8')
            elif isinstance(value, list):
                value = self._decode_list(value)
            elif isinstance(value, dict):
                value = self._decode_dict(value)
            rv[key] = value
        return rv

class EnemyDecoder(Decoder):
    def __init__(self, path):
        Decoder.__init__(self, path)

    def decode_enemy(self, file, x, y):
        monsterDict = Decoder.decode(self, file)

        fighter_component = Components.Fighter(hp=monsterDict['fighter']['hp'], dexterity=monsterDict['fighter']['dexterity'],
            accuracy=monsterDict['fighter']['accuracy'], power=monsterDict['fighter']['power'], xp=monsterDict['fighter']['xp'],
            death_function=Components.monster_death)

        ai_component = Components.WanderingMonster()

        monster = object.Object(x, y, monsterDict['char'], monsterDict['name'], libtcod.Color(monsterDict['r'],monsterDict['g'],monsterDict['b']),
            blocks=bool(monsterDict['blocks']), fighter=fighter_component, ai=ai_component)
        return monster

class ItemDecoder(Decoder):
    def __init__(self, file):
        Decoder.__init__(self, file)

    def decode_item(self, file, x, y):
        itemDict = Decoder.decode(self, file)

        item_component = Components.Item(use_function=item_functions[itemDict['use_function']])
        item = object.Object(x, y, itemDict['char'], itemDict['name'],
            libtcod.Color(itemDict['r'], itemDict['g'], itemDict['b']),
            always_visible=True, item=item_component)
        return item

item_functions = {
    "cast_heal" : Components.cast_heal
}

class EquipmentDecoder(Decoder):
    def __init__(self, file):
        Decoder.__init__(self, file)

    def decode_equipment(self, file, x, y):
        itemDict = Decoder.decode(self, file)

        equipment_component = equipment.Equipment(slot=itemDict['slot'],
            power_bonus=itemDict['power_bonus'], dexterity_bonus=itemDict['dexterity_bonus'],
            max_hp_bonus=itemDict['max_hp_bonus'], accuracy_bonus=itemDict['accuracy_bonus'])

        item = object.Object(x, y, itemDict['char'], itemDict['name'],
            libtcod.Color(itemDict['r'], itemDict['g'], itemDict['b']),
            always_visible=True, equipment=equipment_component)

        return item
