import libtcodpy as libtcod
import game

############################## BASIC COMPONENTS ###############################
CONFUSE_NUM_TURNS = 10

class Fighter:
	def __init__(self, hp, defense, power, xp, death_function=None):
		self.max_hp = hp
		self.hp = hp
		self.defense = defense
		self.power = power
		self.xp = xp
		self.death_function = death_function

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
		damage = self.power - target.fighter.defense	#################### TODO: real fighting logic ###########################

		if damage > 0:
			game.Game.message(self.owner.name.capitalize() + ' attacks ' + target.name + ' for ' + str(damage) + ' hit points.')
			self.xp += target.fighter.take_damage(damage)
		else:
			game.Game.message(self.owner.name.capitalize() + ' attacks ' + target.name + ' but it has no effect!')

	def heal(self, amount):
		self.hp += amount
		if self.hp > self.max_hp:
			self.hp = self.max_hp

	def has_max_hp(self):
		return self.hp == self.max_hp

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

		if monster.distance_to(game.Game.player) >= 2:
			monster.try_move_towards(game.Game.player)

		elif game.Game.player.fighter.hp > 0:
				monster.fighter.attack(game.Game.player)

		if self.current_path == []:
			monster.wander()


class ConfusedMonster:
	def __init__(self, old_ai, num_turns=CONFUSE_NUM_TURNS):
		self.old_ai = old_ai
		self.num_turns = num_turns
		monster = self.owner

	def take_turn(self):
		if self.num_turns > 0:
			monster.wander()
			self.num_turns -= 1

		else:
			monster.ai = self.old_ai
			game.Game.message('The ' + self.owner.name + ' is no longer confused!', libtcod.red)


class Item:
	def __init__(self, use_function=None):
		self.use_function = use_function

	def pick_up(self):
		if len(game.Game.inventory) >= 26:
			game.Game.message('Your inventory is full, cannot pick up ' + 'self.owner.name' + '.', libtcod.red)
		else:
			game.Game.inventory.append(self.owner)
			game.Game.map.remove_object(self.owner)
			game.Game.message('You picked up a ' + self.owner.name + '!', libtcod.green)

	def drop(self):
		game.Game.inventory.remove(self.owner)
		self.owner.x = game.Game.player.x
		self.owner.y = game.Game.player.y
		game.Game.map.add_object(self.owner)
		game.Game.message('You dropped a ' + self.owner.name + '.', libtcod.yellow)

	def use(self):
		if self.use_function is None:
			game.Game.message('The ' + self.owner.name + ' cannot be used.')
		else:
			if self.use_function() != 'cancelled':
				game.Game.inventory.remove(self.owner)

################################# ITEM FUNCTIONS ###############################
HEAL_AMOUNT = 4
lightning_RANGE = 5
lightning_DAMAGE = 20
CONFUSE_RANGE = 8
FIREBALL_RADIUS = 3
FIREBALL_DAMAGE = 12

def cast_heal():
	if game.Game.player.fighter.has_max_hp():
		game.Game.message('You are already at full health.', libtcod.red)
		return 'cancelled'
	game.Game.message('Your wounds start to feel better!', libtcod.light_violet)
	game.Game.player.fighter.heal(HEAL_AMOUNT)

def cast_lightning():
	monster = game.Game.map.closest_monster(lightning_RANGE)
	if monster is None:
		game.Game.message('No enemy is close enough to strike.', libtcod.red)
		return 'cancelled'
	game.Game.message('A lightning bolt strikes the ' + monster.name + ' with a loud thunder! The damage is ' + str(lightning_DAMAGE) + ' hit points.', libtcod.light_blue)
	monster.fighter.take_damage(lightning_DAMAGE)

def cast_confuse():
	game.Game.message('Left-click an enemy to confuse it, or right-click to cancel.', libtcod.light_cyan)
	monster =  game.Game.target_monster(CONFUSE_RANGE)
	if monster is None:
		return 'cancelled'
	old_ai = monster.ai
	monster.ai = ConfusedMonster(old_ai)
	monster.ai.owner = monster
	game.Game.message('The eyes of the ' + monster.name + ' look vacant, as he starts to stumble around!', libtcod.light_green)

def cast_fireball():
	game.Game.message('Left-click a target tile for the fireball, or right-click to cancel.', libtcod.light_cyan)
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
