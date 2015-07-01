import libtcodpy as libtcod
from tile import Tile
from object import Object
from rect import Rect
from map import Map

class Game:

	def __init__(self):
		self.SCREEN_WIDTH = 80
		self.SCREEN_HEIGHT = 50
		self.LIMIT_FPS = 20
		MAP_WIDTH = 80
		MAP_HEIGHT = 45


		self.con = libtcod.console_new(self.SCREEN_WIDTH, self.SCREEN_HEIGHT)
		self.player = Object(self.SCREEN_WIDTH / 2, self.SCREEN_HEIGHT / 2, '@', libtcod.white, self.con)
		self.map = Map(MAP_WIDTH, MAP_HEIGHT)
		self.player.x = self.map.originX
		self.player.y = self.map.originY
		self.objects = [self.player]

	def render_all(self):
		for y in range(self.map.height):
			for x in range(self.map.width):
				wall = self.map[x][y].block_sight
				if wall:
					libtcod.console_put_char_ex(self.con, x, y, '#', libtcod.white, libtcod.black)
				else:
					libtcod.console_put_char_ex(self.con, x, y, '.', libtcod.white, libtcod.black)

		for object in self.objects:
			object.draw()

		libtcod.console_blit(self.con, 0, 0, self.SCREEN_WIDTH, self.SCREEN_HEIGHT, 0, 0, 0)

	def handle_keys(self):

		key = libtcod.console_wait_for_keypress(True)

		if key.vk == libtcod.KEY_ESCAPE:
			return True

		if libtcod.console_is_key_pressed(libtcod.KEY_UP):
			self.player.move(0, -1, self.map)

		elif libtcod.console_is_key_pressed(libtcod.KEY_DOWN):
			self.player.move(0, 1, self.map)

		elif libtcod.console_is_key_pressed(libtcod.KEY_LEFT):
			self.player.move(-1, 0, self.map)

		elif libtcod.console_is_key_pressed(libtcod.KEY_RIGHT):
			self.player.move(1, 0, self.map)

	def run(self):
		libtcod.console_set_custom_font('arial10x10.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
		libtcod.console_init_root(self.SCREEN_WIDTH, self.SCREEN_HEIGHT, 'Libtcod Tutorial', False)

		while not libtcod.console_is_window_closed():
			libtcod.console_set_default_foreground(0, libtcod.white)

			self.render_all()	

			libtcod.console_flush()

			for obj in self.objects:
				obj.clear()

			exit = self.handle_keys()
			if exit:
				break

game = Game()
game.run()