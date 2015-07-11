import libtcodpy as libtcod
import math
import game

class Object:
	def __init__(self, x, y, char, name, color, blocks=False, fighter=None, ai=None, item=None):
		self.x = x
		self.y = y
		self.char = char
		self.name = name
		self.color = color
		self.blocks = blocks

		self.fighter = fighter
		if self.fighter:
			self.fighter.owner = self

		self.ai = ai
		if self.ai:
			self.ai.owner = self

		self.item = item
		if self.item:
			self.item.owner = self

	def move_or_attack(self, dx, dy):
		x = self.x + dx
		y = self.y + dy

		target = None
		for object in game.Game.map.objects:
			if object.fighter and object.x == x and object.y == y:
				target = object
				break

		if target is not None:
			self.fighter.attack(target)
		else:
			self.move(dx, dy)

	def move(self, dx, dy):
		if not game.Game.map.is_blocked(self.x + dx, self.y + dy):
			self.x += dx
			self.y += dy

	def move_towards(self, target_x, target_y):
		dx = target_x - self.x
		dy = target_y - self.y
		distance = math.sqrt(dx ** 2 + dy **2)

		dx = int(round(dx/distance))
		dy = int(round(dy/distance))
		self.move(dx, dy)

	def distance_to(self, other):
		dx = other.x - self.x
		dy = other.y - self.y
		return math.sqrt(dx ** 2 + dy ** 2)
