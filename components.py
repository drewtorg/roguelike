import libtcodpy as libtcod
import game

#contains combat related properties and methods
class Fighter:
	def __init__(self, hp, defense, power, death_function=None):
		self.max_hp = hp
		self.hp = hp
		self.defense = defense
		self.power = power
		self.death_function = death_function

	def take_damage(self, damage):
		if damage > 0:
			self.hp -= damage

		if self.hp <= 0:
			self.hp = 0
			function = self.death_function
			if function is not None:
				function(self.owner)

	def attack(self, target):
		damage = self.power - target.fighter.defense

		if damage > 0:
			game.Game.message(self.owner.name.capitalize() + ' attacks ' + target.name + ' for ' + str(damage) + ' hit points.')
			target.fighter.take_damage(damage)
		else:
			game.Game.message(self.owner.name.capitalize() + ' attacks ' + target.name + ' but it has no effect!')

	def heal(self, amount):
		self.hp += amount
		if self.hp > self.max_hp:
			self.hp = self.max_hp

	def has_max_hp(self):
		return self.hp == self.max_hp

#AI for a basic monster
class BasicMonster:
	def take_turn(self):
		monster = self.owner

		if game.Game.map.is_in_fov(monster):
			if monster.distance_to(game.Game.player) >= 2:
				monster.move_towards(game.Game.player.x, game.Game.player.y)

			elif game.Game.player.fighter.hp > 0:
				monster.fighter.attack(game.Game.player)

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

	def use(self):
		if self.use_function is None:
			game.Game.message('The ' + self.owner.name + ' cannot be used.')
		else:
			if self.use_function() != 'cancelled':
				game.Game.inventory.remove(self.owner)

################################# ITEM FUNCTIONS ###############################
HEAL_AMOUNT = 4
LIGHTENING_RANGE = 5
LIGHTENING_DAMAGE = 20

def cast_heal():
	if game.Game.player.fighter.has_max_hp():
		game.Game.message('You are already at full health.', libtcod.red)
		return 'cancelled'
	game.Game.message('Your wounds start to feel better!', libtcod.light_violet)
	game.Game.player.fighter.heal(HEAL_AMOUNT)

def cast_lightening():
	monster = game.Game.map.closest_monster(LIGHTENING_RANGE)
	if monster is None:
		game.Game.message('No enemy is close enough to strike.', libtcod.red)
		return 'cancelled'
	game.Game.message('A lightening bolt strikes the ' + monster.name + ' with a loud thrunder! The damage is ' + str(LIGHTENING_DAMAGE) + ' hit points.', libtcod.light_blue)
	monster.fighter.take_damage(LIGHTENING_DAMAGE)

################################# DEATH FUNCTIONS ##############################
def player_death(player):
	game.Game.state = 'dead'
	game.Game.message('You died', libtcod.red)

	player.char = '%'
	player.color = libtcod.dark_red

def monster_death(monster):
	game.Game.message(monster.name.capitalize() + ' is dead!', libtcod.orange)

	monster.char = '%'
	monster.color = libtcod.dark_red
	monster.blocks = False
	monster.fighter = None
	monster.ai = None
	monster.name = 'remains of ' + monster.name
	game.Game.map.send_to_back(monster)
