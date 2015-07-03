import libtcodpy as libtcod
from tile import Tile
from object import Object
from rect import Rect
from map import Map

class Game:

	SCREEN_WIDTH = 80
	SCREEN_HEIGHT = 50
	LIMIT_FPS = 20
	MAP_WIDTH = 80
	MAP_HEIGHT = 45
	FOV_ALGO = 0
	FOV_LIGHT_WALLS = True
	TORCH_RADIUS = 5
	COLOR_LIT = libtcod.lighter_grey
	COLOR_UNLIT = libtcod.dark_grey
	
	def __init__(self):

		self.game_state = 'playing'
		player_action = None

		self.con = libtcod.console_new(Game.SCREEN_WIDTH, Game.SCREEN_HEIGHT)
		self.player = Object(Game.SCREEN_WIDTH / 2, Game.SCREEN_HEIGHT / 2, '@', 'Drew', libtcod.pink, self.con, True)
		self.map = Map(Game.MAP_WIDTH, Game.MAP_HEIGHT, self.con)
		self.player.x = self.map.originX
		self.player.y = self.map.originY
		self.objects = self.map.objects
		self.objects.append(self.player)

		self.fov_recompute = True
		self.fov_map = self.make_fov_map()

		libtcod.console_set_custom_font('terminal8x12_gs_tc.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
		libtcod.console_init_root(Game.SCREEN_WIDTH, Game.SCREEN_HEIGHT, 'Libtcod Tutorial', False)

	def make_fov_map(self):
		fov_map = libtcod.map_new(Game.MAP_WIDTH, Game.MAP_HEIGHT)
		for y in range(Game.MAP_HEIGHT):
			for x in range(Game.MAP_WIDTH):
				libtcod.map_set_properties(fov_map, x, y, not self.map[x][y].block_sight, not self.map[x][y].blocked)
		return fov_map

	def recompute_fov(self):
		if self.fov_recompute:
			self.fov_recompute = False
			libtcod.map_compute_fov(self.fov_map, self.player.x, self.player.y, Game.TORCH_RADIUS, Game.FOV_LIGHT_WALLS, Game.FOV_ALGO)

	def render_all(self):
		self.recompute_fov()

		for y in range(self.map.height):
			for x in range(self.map.width):
				visible = libtcod.map_is_in_fov(self.fov_map, x, y)
				wall = self.map[x][y].block_sight
				if not visible:
					if self.map[x][y].explored:
						if wall:
							libtcod.console_put_char_ex(self.con, x, y, '#', Game.COLOR_UNLIT, libtcod.black)
						else:
							libtcod.console_put_char_ex(self.con, x, y, '.', Game.COLOR_UNLIT, libtcod.black)
				else:
					self.map[x][y].explored = True
					if wall:
						libtcod.console_put_char_ex(self.con, x, y, '#', Game.COLOR_LIT, libtcod.black)
					else:
						libtcod.console_put_char_ex(self.con, x, y, '.', Game.COLOR_LIT, libtcod.black)

		for object in self.objects:
			object.draw(self.fov_map)

		libtcod.console_blit(self.con, 0, 0, Game.SCREEN_WIDTH, Game.SCREEN_HEIGHT, 0, 0, 0)

	def handle_keys(self):
		if self.game_state == 'playing':
			key = libtcod.console_wait_for_keypress(True)

			if key.vk == libtcod.KEY_ESCAPE:
				return 'exit'

			if libtcod.console_is_key_pressed(libtcod.KEY_UP):
				self.player.move_or_attack(0, -1, self.map)
				self.fov_recompute = True

			elif libtcod.console_is_key_pressed(libtcod.KEY_DOWN):
				self.player.move_or_attack(0, 1, self.map)
				self.fov_recompute = True

			elif libtcod.console_is_key_pressed(libtcod.KEY_LEFT):
				self.player.move_or_attack(-1, 0, self.map)
				self.fov_recompute = True

			elif libtcod.console_is_key_pressed(libtcod.KEY_RIGHT):
				self.player.move_or_attack(1, 0, self.map)
				self.fov_recompute = True

			else:
				return 'didnt-take-turn'

	def run(self):
		while not libtcod.console_is_window_closed():
			libtcod.console_set_default_foreground(0, Game.COLOR_LIT)

			self.render_all()	

			libtcod.console_flush()

			player_action = self.handle_keys()
			# print player_action

			# if self.game_state == 'playing' and player_action != 'didnt-take-turn':
			# 	for object in self.objects:
			# 		if object != self.player:
			# 			print 'The ' + object.name + ' growls!'

			if player_action == 'exit':
				break