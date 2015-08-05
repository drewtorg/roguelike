import libtcodpy as libtcod
import components as Components
import equipment
import object
import json
import glob
import os
# from sys import platform as _platform

class Decoder:
	def __init__(self, path):
		self.path = path

	def decode(self, file):
		decodeFile = open(os.path.join(self.path, file + '.json'))
		decodeString = decodeFile.read()
		return json.loads(decodeString, object_hook=self._decode_dict)

	def decode_spawn_chance(self, file):
		dict = self.decode(file)
		return dict['spawn_chance']

	def decode_all_spawn_chances(self):
		spawn_chances = {}
		for file in glob.glob(self.path + '/*.json'):
			fileName = os.path.split(file)[-1]
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
		enemy_dict = Decoder.decode(self, file)

		fighter_component = Components.Fighter(hp=enemy_dict['fighter']['hp'], dexterity=enemy_dict['fighter']['dexterity'],
			accuracy=enemy_dict['fighter']['accuracy'], power=enemy_dict['fighter']['power'], xp=enemy_dict['fighter']['xp'],
			death_function=vars(Components)[enemy_dict['death_function']], range=enemy_dict['fighter']['range'])

		ai_component = vars(Components)[enemy_dict['ai']]()

		color = vars(libtcod)[enemy_dict['color']]
		monster = object.Object(x, y, enemy_dict['char'], enemy_dict['name'], color=color,
			blocks=bool(enemy_dict['blocks']), fighter=fighter_component, ai=ai_component)
		return monster

class ItemDecoder(Decoder):
	def __init__(self, path):
		Decoder.__init__(self, path)

	def decode_item(self, file, x, y):
		item_dict = Decoder.decode(self, file)

		color = vars(libtcod)[item_dict['color']]
		item_component = Components.Item(use_function=vars(Components)[item_dict['use_function']], range=item_dict['range'])
		item = object.Object(x, y, item_dict['char'], item_dict['name'],
			color=color, always_visible=True, item=item_component)
		return item

class EquipmentDecoder(Decoder):
	def __init__(self, path):
		Decoder.__init__(self, path)

	def decode_equipment(self, file, x, y):
		item_dict = Decoder.decode(self, file)

		equipment_component = equipment.Equipment(slot=item_dict['slot'],
			power_bonus=item_dict['power_bonus'], dexterity_bonus=item_dict['dexterity_bonus'],
			max_hp_bonus=item_dict['max_hp_bonus'], accuracy_bonus=item_dict['accuracy_bonus'],
			range_bonus=item_dict['range_bonus'])

		color = vars(libtcod)[item_dict['color']]
		item = object.Object(x, y, item_dict['char'], item_dict['name'],
			color=color, always_visible=True, equipment=equipment_component)
		return item

class MapDecoder(Decoder):
	def __init__(self, path):
		Decoder.__init__(self, path)

	def decode_map(self, file):
		map_dict = Decoder.decode(self, file)
		map_dict['FOV_LIGHT_WALLS'] = bool(map_dict['FOV_LIGHT_WALLS'])
		return map_dict

class RaceDecoder(Decoder):
	def __init__(self, path):
		Decoder.__init__(self, path)

	def decode_all_races(self):
		races = []
		for file in glob.glob(self.path + '/*.json'):
			fileName = os.path.split(file)[-1]
			race = fileName.split('.')[0]
			races.append(race.title())
		return races

	def decode_race_fighter(self, file):
		race_dict = Decoder.decode(self, file)
		fighter_dict = race_dict['fighter']
		fighter = Components.Fighter(fighter_dict['hp'], fighter_dict['dexterity'],
			fighter_dict['accuracy'], fighter_dict['power'], fighter_dict['xp'],
			fighter_dict['range'], Components.player_death)
		return fighter

	def decode_race_color(self, file):
		race_dict = Decoder.decode(self, file)
		return vars(libtcod)[race_dict['color']]
