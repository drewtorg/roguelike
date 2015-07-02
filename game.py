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
		self.MAP_WIDTH = 80
		self.MAP_HEIGHT = 45
		self.FOV_ALGO = 0
		self.FOV_LIGHT_WALLS = True
		self.TORCH_RADIUS = 5
		self.LIT = libtcod.white
		self.UNLIT = libtcod.dark_grey

		self.con = libtcod.console_new(self.SCREEN_WIDTH, self.SCREEN_HEIGHT)
		self.player = Object(self.SCREEN_WIDTH / 2, self.SCREEN_HEIGHT / 2, '@', libtcod.white, self.con)
		self.map = Map(self.MAP_WIDTH, self.MAP_HEIGHT)
		self.player.x = self.map.originX
		self.player.y = self.map.originY
		self.objects = [self.player]

		self.fov_recompute = True
		self.fov_map = self.make_fov_map()

		libtcod.console_set_custom_font('terminal8x12_gs_tc.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
		libtcod.console_init_root(self.SCREEN_WIDTH, self.SCREEN_HEIGHT, 'Libtcod Tutorial', False)

	def make_fov_map(self):
		fov_map = libtcod.map_new(self.MAP_WIDTH, self.MAP_HEIGHT)
		for y in range(self.MAP_HEIGHT):
			for x in range(self.MAP_WIDTH):
				libtcod.map_set_properties(fov_map, x, y, not self.map[x][y].block_sight, not self.map[x][y].blocked)
		return fov_map

	def recompute_fov(self):
		if self.fov_recompute:
			self.fov_recompute = False
			libtcod.map_compute_fov(self.fov_map, self.player.x, self.player.y, self.TORCH_RADIUS, self.FOV_LIGHT_WALLS, self.FOV_ALGO)

	def render_all(self):
		self.recompute_fov()

		for y in range(self.map.height):
			for x in range(self.map.width):
				visible = libtcod.map_is_in_fov(self.fov_map, x, y)
				wall = self.map[x][y].block_sight
				if not visible:
					if self.map[x][y].explored:
						if wall:
							libtcod.console_put_char_ex(self.con, x, y, '#', self.UNLIT, libtcod.black)
						else:
							libtcod.console_put_char_ex(self.con, x, y, '.', self.UNLIT, libtcod.black)
				else:
					self.map[x][y].explored = True
					if wall:
						libtcod.console_put_char_ex(self.con, x, y, '#', self.LIT, libtcod.black)
					else:
						libtcod.console_put_char_ex(self.con, x, y, '.', self.LIT, libtcod.black)

		for object in self.objects:
			object.draw(self.fov_map)

		libtcod.console_blit(self.con, 0, 0, self.SCREEN_WIDTH, self.SCREEN_HEIGHT, 0, 0, 0)

	def handle_keys(self):
		key = libtcod.console_wait_for_keypress(True)

		if key.vk == libtcod.KEY_ESCAPE:
			return True

		if libtcod.console_is_key_pressed(libtcod.KEY_UP):
			self.player.move(0, -1, self.map)
			self.fov_recompute = True

		elif libtcod.console_is_key_pressed(libtcod.KEY_DOWN):
			self.player.move(0, 1, self.map)
			self.fov_recompute = True

		elif libtcod.console_is_key_pressed(libtcod.KEY_LEFT):
			self.player.move(-1, 0, self.map)
			self.fov_recompute = True

		elif libtcod.console_is_key_pressed(libtcod.KEY_RIGHT):
			self.player.move(1, 0, self.map)
			self.fov_recompute = True

	def run(self):
		while not libtcod.console_is_window_closed():
			libtcod.console_set_default_foreground(0, libtcod.white)

			self.render_all()	

			libtcod.console_flush()

			for obj in self.objects:
				obj.clear()

			exit = self.handle_keys()
			if exit:
				break