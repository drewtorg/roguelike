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

#AI for a basic monster
class BasicMonster:
	def take_turn(self):
		monster = self.owner

		if libtcod.map_is_in_fov(monster.map.fov_map, monster.x, monster.y):
			if monster.distance_to(monster.map.player) >= 2:
				monster.move_towards(monster.map.player.x, monster.map.player.y)

			elif monster.map.player.fighter.hp > 0:
				monster.fighter.attack(monster.map.player)

def player_death(player):
	print game.Game.state
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
	monster.send_to_back()
