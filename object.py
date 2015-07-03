import libtcodpy as libtcod
import math

class Object:
	def __init__(self, x, y, char, name, color, console, map, blocks=False, fighter=None, ai=None):
		self.x = x
		self.y = y
		self.char = char
		self.name = name
		self.color = color
		self.con = console
		self.blocks = blocks
		self.map = map

		self.fighter = fighter
		if self.fighter:
			self.fighter.owner = self

		self.ai = ai
		if self.ai:
			self.ai.owner = self

	def move_or_attack(self, dx, dy):
		x = self.x + dx
		y = self.y + dy

		target = None
		for object in self.map.objects:
			if object.x == x and object.y == y:
				target = object
				break

		if target is not None:
			print 'You swing your sword at the ' + target.name + ' and miss horrendously!'
		else:
			self.move(dx, dy)

	def move(self, dx, dy):
		if not self.map.is_blocked(self.x + dx, self.y + dy):
			self.x += dx
			self.y += dy

	def draw(self):
		if libtcod.map_is_in_fov(self.map.fov_map, self.x, self.y):
			libtcod.console_set_default_foreground(self.con, self.color)
			libtcod.console_put_char(self.con, self.x, self.y, self.char, libtcod.BKGND_NONE)

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