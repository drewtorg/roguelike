from tile import Tile
from rect import Rect
import libtcodpy as libtcod
from object import Object
import components as Components
import game
import equipment
import decoder

enemyDecoder = decoder.EnemyDecoder('enemies/')
itemDecoder = decoder.ItemDecoder('items/')
equipmentDecoder = decoder.EquipmentDecoder('equipment/')

class Map:

	MAX_ROOM_MONSTERS = [[2, 1], [3, 4], [5, 6]]
	# MAX_ROOM_MONSTERS = [[0, 1], [3, 4], [5, 6]]
	MAX_ROOM_ITEMS = [[1, 1], [2, 4]]
	MAX_EQUIPMENT = 3
	EQUIPMENT_CHANCE = 75
	LIGHTNING_CHANCE = [[25, 4]]
	FIREBALL_CHANCE = [[25, 6]]
	CONFUSE_CHANCE = [[10, 2]]
	ROOM_MIN_SIZE = 6
	ROOM_MAX_SIZE = 10
	MAX_ROOMS = 30
	FOV_ALGO = 0
	FOV_LIGHT_WALLS = True
	TORCH_RADIUS = 5
	COLOR_LIT = libtcod.lighter_grey
	COLOR_UNLIT = libtcod.dark_grey


	def __init__(self, width, height):
		self.height = height
		self.width = width
		self.objects = []
		self.monster_chances = {}
		self.item_chances = {}
		self.equipment_count = 0
		self.make_map()
		self.fov_recompute = True
		self.fov_map = self.make_fov_map()


	def __getitem__(self, key):
		return self.map[key]

	def __len__(self):
		return len(self.map)

	def make_map(self):
		self.map = [[ Tile(True)
			for y in range(self.height) ]
				for x in range(self.width) ]

		rooms = []
		num_rooms = 0

		self.monster_chances = enemyDecoder.decode_all_spawn_chances()
		for chance in self.monster_chances:
			self.monster_chances[chance] = from_dungeon_level(self.monster_chances[chance])

		self.item_chances = itemDecoder.decode_all_spawn_chances()
		for chance in self.item_chances:
			self.item_chances[chance] = from_dungeon_level(self.item_chances[chance])

		self.equipment_chances = equipmentDecoder.decode_all_spawn_chances()
		for chance in self.equipment_chances:
			self.equipment_chances[chance] = from_dungeon_level(self.equipment_chances[chance])

		# self.item_chances['sword'] = 35
		# self.item_chances['shield'] = 35
		self.item_chances['lightning'] = from_dungeon_level(Map.LIGHTNING_CHANCE)
		self.item_chances['fireball'] = from_dungeon_level(Map.FIREBALL_CHANCE)
		self.item_chances['confuse'] = from_dungeon_level(Map.CONFUSE_CHANCE)

		for r in range(Map.MAX_ROOMS):
			#make a random room
			w = libtcod.random_get_int(0, Map.ROOM_MIN_SIZE, Map.ROOM_MAX_SIZE)
			h = libtcod.random_get_int(0, Map.ROOM_MIN_SIZE, Map.ROOM_MAX_SIZE)

			x = libtcod.random_get_int(0, 0, self.width - w - 1)
			y = libtcod.random_get_int(0, 0, self.height - h - 1)

			new_room = Rect(x, y, w, h)

			#make sure it doesn't intersect other rooms
			failed = False
			for other_room in rooms:
				if new_room.intersect(other_room):
					failed = True
					break

			if not failed:
				self.create_room(new_room)
				self.place_objects(new_room)
				(new_x, new_y) = new_room.center()

				if num_rooms == 0:
					self.origin = (new_x, new_y)

				else:
					#connect our room to the previous room
					(prev_x, prev_y) = rooms[num_rooms-1].center()

					if libtcod.random_get_int(0, 0, 1) == 1:
						self.create_h_tunnel(prev_x, new_x, prev_y)
						self.create_v_tunnel(prev_y, new_y, new_x)
					else:
						self.create_v_tunnel(prev_y, new_y, prev_x)
						self.create_h_tunnel(prev_x, new_x, new_y)

				rooms.append(new_room)
				num_rooms+= 1

		self.stairs = Object(new_x, new_y, '<', 'stairs', libtcod.white, always_visible=True)
		self.objects.append(self.stairs)
		self.send_to_back(self.stairs)

	def place_objects(self, room):
		num_monsters = libtcod.random_get_int(0, 0, from_dungeon_level(Map.MAX_ROOM_MONSTERS))
		self.place_monsters(room, num_monsters)

		num_items = libtcod.random_get_int(0, 0, from_dungeon_level(Map.MAX_ROOM_ITEMS))
		self.place_items(room, num_items)

		num_equipment = libtcod.random_get_int(0, 0, 100)
		self.place_equipment(room, num_equipment)

	def place_items(self, room, num_items):
		for i in range(num_items):
			x = libtcod.random_get_int(0, room.x1 + 1, room.x2 - 1)
			y = libtcod.random_get_int(0, room.y1 + 1, room.y2 - 1)

			if not self.is_blocked(x, y):
				choice = random_choice(self.item_chances)
				if choice == 'minor healing potion':
					item = itemDecoder.decode_item('minor healing potion', x, y)
				elif choice == 'lightning':
					item_component = Components.Item(use_function=Components.cast_lightning)
					item = Object(x, y, '#', 'scroll of lightning', libtcod.dark_amber, always_visible=True, item=item_component)
				elif choice == 'fireball':
					item_component = Components.Item(use_function=Components.cast_confuse)
					item = Object(x, y, '#', 'scroll of confusion', libtcod.dark_amber, always_visible=True, item=item_component)
				elif choice == 'confuse':
					item_component = Components.Item(use_function=Components.cast_fireball)
					item = Object(x, y, '#', 'scroll of fireball', libtcod.dark_amber, always_visible=True, item=item_component)
				elif choice == 'sword':
					item = equipmentDecoder.decode_equipment('sword', x, y)
				elif choice == 'shield':
						equipment_component = equipment.Equipment(slot='left hand', dexterity_bonus=3)
						item = Object(x, y, '[', 'shield', libtcod.darker_orange, always_visible=True, equipment=equipment_component)
				self.objects.insert(0, item)

	def place_monsters(self, room, num_monsters):
		for i in range(num_monsters):
			x = libtcod.random_get_int(0, room.x1 + 1, room.x2 - 1)
			y = libtcod.random_get_int(0, room.y1 + 1, room.y2 - 1)

			if not self.is_blocked(x, y):
				choice = random_choice(self.monster_chances)
				monster = enemyDecoder.decode_enemy(choice, x, y)
				self.add_object(monster)

	def place_equipment(self, room, equipment_chance):
		if equipment_chance > Map.EQUIPMENT_CHANCE and self.equipment_count < Map.MAX_EQUIPMENT:
			x = libtcod.random_get_int(0, room.x1 + 1, room.x2 - 1)
			y = libtcod.random_get_int(0, room.y1 + 1, room.y2 - 1)

			choice = random_choice(self.equipment_chances)
			item = equipmentDecoder.decode_equipment(choice, x, y)
			self.objects.insert(0, item)

	def create_room(self, room):
		for x in range(room.x1 + 1, room.x2):
			for y in range(room.y1 + 1, room.y2):
				self.map[x][y].blocked = False
				self.map[x][y].block_sight = False

	def create_h_tunnel(self, x1, x2, y):
		for x in range(min(x1, x2), max(x1, x2) + 1):
			self.map[x][y].blocked = False
			self.map[x][y].block_sight = False

	def create_v_tunnel(self, y1, y2, x):
		for y in range(min(y1, y2), max(y1, y2) + 1):
			self.map[x][y].blocked = False
			self.map[x][y].block_sight = False

	def is_blocked(self, x, y):
		if self.map[x][y].blocked:
			return True

		for object in self.objects:
			if object.blocks and object.x == x and object.y == y:
				return True

		return False

	def make_fov_map(self):
		self.fov_recompute = True
		fov_map = libtcod.map_new(self.width, self.height)
		for y in range(self.height):
			for x in range(self.width):
				libtcod.map_set_properties(fov_map, x, y, not self.map[x][y].block_sight, not self.map[x][y].blocked)
		return fov_map

	def recompute_fov(self):
		if self.fov_recompute:
			self.fov_recompute = False
			libtcod.map_compute_fov(self.fov_map, game.Game.player.x, game.Game.player.y, Map.TORCH_RADIUS, Map.FOV_LIGHT_WALLS, Map.FOV_ALGO)

	def closest_monster(self, max_range):
		closest_enemy = None
		closest_distance = max_range + 1

		for object in self.objects:
			if object.fighter and not object == game.Game.player and self.is_in_fov(object):
				dist = game.Game.player.distance_to(object)
				if dist < closest_distance:
					closest_enemy = object
					closest_distance = dist
		return closest_enemy

	def add_object(self, object):
		self.objects.append(object)

	def remove_object(self, object):
		self.objects.remove(object)

	def send_to_back(self, object):
		self.remove_object(object)
		self.objects.insert(0, object)

	def is_in_fov(self, object):
		return libtcod.map_is_in_fov(self.fov_map, object.x, object.y)

	def is_tile_in_fov(self, x, y):
		return libtcod.map_is_in_fov(self.fov_map, x, y)

	def object_at(self, x, y):
		for object in self.objects:
			if object.x == x and object.y == y:
				return object
		return None

def random_choice_index(chances):
	dice = libtcod.random_get_int(0, 1, sum(chances))

	running_sum = 0
	choice = 0
	for w in chances:
		running_sum += w

		if dice <= running_sum:
			return choice
		choice += 1

def random_choice(chances_dict):
	chances = chances_dict.values()
	strings = chances_dict.keys()

	return strings[random_choice_index(chances)]

def from_dungeon_level(table):
	for (value, level) in reversed(table):
		if game.Game.dungeon_level >= level:
			return value
	return 0
