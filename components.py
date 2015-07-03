import libtcodpy as libtcod

#contains combat related properties and methods
class Fighter:
	def __init__(self, hp, defense, power):
		self.max_hp = hp
		self.hp = hp
		self.defense = defense
		self.power = power

#AI for a basic monster
class BasicMonster:
	def take_turn(self):
		monster = self.owner

		if libtcod.map_is_in_fov(monster.map.fov_map, monster.x, monster.y):
			if monster.distance_to(monster.map.player) >= 2:
				monster.move_towards(monster.map.player.x, monster.map.player.y)

			elif monster.map.player.fighter.hp > 0:
				print 'The ' + monster.name + ' attacks you!'