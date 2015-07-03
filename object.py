import libtcodpy as libtcod

class Object:
	def __init__(self, x, y, char, name, color, console, blocks=False):
		self.x = x
		self.y = y
		self.char = char
		self.name = name
		self.color = color
		self.con = console
		self.blocks = blocks

	def move_or_attack(self, dx, dy, map):
		x = self.x + dx
		y = self.y + dy

		target = None
		for object in map.objects:
			if object.x == x and object.y == y:
				target = object
				break

		if target is not None:
			print 'You swing your sword at the ' + target.name + ' and miss horrendously!'
		else:
			self.move(dx, dy, map)

	def move(self, dx, dy, map):
		if not map.is_blocked(self.x + dx, self.y + dy):
			self.x += dx
			self.y += dy

	def draw(self, fov_map):
		if libtcod.map_is_in_fov(fov_map, self.x, self.y):
			libtcod.console_set_default_foreground(self.con, self.color)
			libtcod.console_put_char(self.con, self.x, self.y, self.char, libtcod.BKGND_NONE)