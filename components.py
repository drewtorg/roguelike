import libtcodpy as libtcod
import game

############################## BASIC COMPONENTS ###############################
CONFUSE_NUM_TURNS = 6

class Fighter:
	def __init__(self, hp, dexterity, accuracy, power, xp, range, death_function=None):
		self.base_max_hp = hp
		self.hp = hp
		self.base_dexterity = dexterity
		self.base_power = power
		self.base_accuracy = accuracy
		self.xp = xp
		self.range = range
		self.death_function = death_function

	@property
	def power(self):
		bonus = sum(equipment.power_bonus for equipment in self.get_all_equipped())
		return self.base_power + bonus

	@property
	def dexterity(self):
		bonus = sum(equipment.dexterity_bonus for equipment in self.get_all_equipped())
		return self.base_dexterity + bonus

	@property
	def max_hp(self):
		bonus = sum(equipment.max_hp_bonus for equipment in self.get_all_equipped())
		return self.base_max_hp + bonus

	@property
	def accuracy(self):
		bonus = sum(equipment.accuracy_bonus for equipment in self.get_all_equipped())
		return self.base_accuracy + bonus

	def take_damage(self, damage):
		if damage > 0:
			self.hp -= damage

		if self.hp <= 0:
			self.hp = 0
			function = self.death_function
			if function is not None:
				function(self.owner)
			return self.xp
		return 0

	def attack(self, target):
		hit = libtcod.random_get_int(0, 1, self.accuracy) > target.fighter.dexterity

		if hit:
			damage = libtcod.random_get_int(0, self.power/2, self.power)

			if damage > 0:
				game.Game.message(self.owner.name.capitalize() + ' attacks ' + target.name + ' for ' + str(damage) + ' hit points.')
				self.xp += target.fighter.take_damage(damage)
			else:
				game.Game.message(self.owner.name.capitalize() + ' attacks ' + target.name + ' but it has no effect!')
		else:
			game.Game.message(self.owner.name.capitalize() + ' attacks ' + target.name + ' and misses!')

	def heal(self, percent):
		self.hp += int(percent * self.max_hp)
		if self.hp > self.max_hp:
			self.hp = self.max_hp

	def has_max_hp(self):
		return self.hp == self.max_hp

	def get_all_equipped(self):
		if self.owner == game.Game.player:
			equipped_list = []
			for item in game.Game.player.inventory:
				if item.equipment and item.equipment.is_equipped:
					equipped_list.append(item.equipment)
			return equipped_list
		else:
			return []

class BasicMonster:
	def __init__(self):
		self.current_path = []

	def take_turn(self):
		monster = self.owner

		#if you can't hit the player, try to move towards him
		if monster.distance_to(game.Game.player) >= 2:
			monster.try_move_towards(game.Game.player)

		elif game.Game.player.fighter.hp > 0:
				monster.fighter.attack(game.Game.player)

class WanderingMonster:
	def __init__(self):
		self.current_path = []

	def take_turn(self):
		monster = self.owner

		if monster.distance_to(game.Game.player) >= monster.fighter.range:
			monster.try_move_towards(game.Game.player)

		elif game.Game.player.fighter.hp > 0:
			monster.fighter.attack(game.Game.player)

		elif self.current_path == []:
			monster.wander()


class ConfusedMonster:
	def __init__(self, old_ai, num_turns=CONFUSE_NUM_TURNS):
		self.old_ai = old_ai
		self.num_turns = num_turns

	def take_turn(self):
		monster = self.owner

		if self.num_turns > 0:
			self.num_turns -= 1

		else:
			monster.ai = self.old_ai
			game.Game.message('The ' + self.owner.name + ' is no longer confused!', libtcod.red)


class Job:
	def __init__(self, name, abilities, max_mp, mp_regen):
		self.name = name
		self.abilities = abilities
		self.mp = max_mp
		self.max_mp = max_mp
		self.mp_regen = mp_regen

	def update(self):
		self.mp = min(self.mp + self.mp_regen, self.max_mp)

	def has_max_mp(self):
		return self.max_mp == self.mp

	def regen_mana(self, percent):
		self.mp += int(percent * self.max_mp)
		if self.mp > self.max_mp:
			self.mp = self.max_mp


class Item:
	def __init__(self, use_function=None, range=0):
		self.use_function = use_function

	def pick_up(self):
		if len(game.Game.player.inventory) >= 26:
			game.Game.message('Your inventory is full, cannot pick up ' + self.owner.name + '.', libtcod.red)
		else:
			game.Game.player.inventory.append(self.owner)
			game.Game.map.remove_object(self.owner)
			game.Game.message('You picked up a ' + self.owner.name + '!', libtcod.green)

			equipment = self.owner.equipment
			if equipment and self.owner.equipment.get_equipped_in_slot(equipment.slot) is None:
				equipment.equip()

	def drop(self):
		if self.owner.equipment:
			self.owner.equipment.dequip()

		game.Game.player.inventory.remove(self.owner)
		self.owner.x = game.Game.player.x
		self.owner.y = game.Game.player.y
		game.Game.map.add_object(self.owner)
		game.Game.message('You dropped a ' + self.owner.name + '.', libtcod.yellow)

	def use(self):
		if self.owner.equipment:
			self.owner.equipment.toggle_equip()
			return

		if self.use_function is None:
			game.Game.message('The ' + self.owner.name + ' cannot be used.')
		else:
			if self.use_function() != 'cancelled':
				game.Game.player.inventory.remove(self.owner)

################################# ITEM FUNCTIONS ###############################
HEAL_AMOUNT = .3
REGEN_AMOUNT = .5
LIGHTNING_RANGE = 5
LIGHTNING_DAMAGE = 40
CONFUSE_RANGE = 8
FIREBALL_RADIUS = 3
FIREBALL_DAMAGE = 25

def cast_heal():
	if game.Game.player.fighter.has_max_hp():
		game.Game.message('You are already at full health.', libtcod.red)
		return 'cancelled'
	game.Game.message('Your wounds start to feel better!', libtcod.light_violet)
	game.Game.player.fighter.heal(HEAL_AMOUNT)

def cast_restore():
	health = cast_heal()
	mana = cast_regen_mana()
	if health == 'cancelled' and mana == 'cancelled':
		return 'cancelled'

def cast_regen_mana():
	if game.Game.player.job.has_max_mp():
		game.Game.message('You are already at full mana.', libtcod.red)
		return 'cancelled'
	game.Game.message('You feel invigorated!', libtcod.light_violet)
	game.Game.player.job.regen_mana(REGEN_AMOUNT)

def cast_lightning():
	monster = game.Game.map.closest_monster(LIGHTNING_RANGE)
	if monster is None:
		game.Game.message('No enemy is close enough to strike.', libtcod.red)
		return 'cancelled'
	game.Game.message('A lightning bolt strikes the ' + monster.name + ' with a loud thunder! The damage is ' + str(LIGHTNING_DAMAGE) + ' hit points.', libtcod.light_blue)
	monster.fighter.take_damage(LIGHTNING_DAMAGE)

def cast_confuse():
	game.Game.message('Hit enter on an enemy to confuse it, or escape to cancel.', libtcod.light_cyan)
	monster = game.Game.target_monster(CONFUSE_RANGE)

	if monster is None:
		return 'cancelled'
	old_ai = monster.ai
	monster.ai = ConfusedMonster(old_ai)
	monster.ai.owner = monster
	game.Game.message('The eyes of the ' + monster.name + ' look vacant, as he starts to stumble around!', libtcod.light_green)

def cast_fireball():
	game.Game.message('Hit enter on target tile for the fireball, or escape to cancel.', libtcod.light_cyan)
	(x, y) = game.Game.target_tile()
	if x is None:
		return 'cancelled'
	game.Game.message('The fireball explodes, burning everything within ' + str(FIREBALL_RADIUS) + ' tiles!', libtcod.orange)

	for obj in game.Game.map.objects:
		if obj.distance(x, y) <= FIREBALL_RADIUS and obj.fighter:
			game.Game.message('The ' + obj.name + ' gets burned for ' + str(FIREBALL_DAMAGE) + ' hit points!', libtcod.orange)
			obj.fighter.take_damage(FIREBALL_DAMAGE)

################################# DEATH FUNCTIONS ##############################
def player_death(player):
	game.Game.state = 'dead'
	game.Game.message('You died', libtcod.red)

	player.char = '%'
	player.color = libtcod.dark_red

def monster_death(monster):
	game.Game.message(monster.name.capitalize() + ' is dead! You gain ' + str(monster.fighter.xp) + ' experience points.', libtcod.orange)

	monster.char = '%'
	monster.color = libtcod.dark_red
	monster.blocks = False
	monster.fighter = None
	monster.ai = None
	monster.name = 'remains of ' + monster.name
	game.Game.map.send_to_back(monster)
