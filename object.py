import libtcodpy as libtcod

class Object:
	def __init__(self, x, y, char, color, console):
		self.x = x
		self.y = y
		self.char = char
		self.color = color
		self.con = console

	def move(self, dx, dy, map):
		if not map[self.x + dx][self.y + dy].blocked:
			self.x += dx
			self.y += dy

	def draw(self):
		libtcod.console_set_default_foreground(self.con, self.color)
		libtcod.console_put_char(self.con, self.x, self.y, self.char, libtcod.BKGND_NONE)

	def clear(self):
		libtcod.console_put_char_ex(self.con, self.x, self.y, '.', libtcod.white, libtcod.black)