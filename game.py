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
	
	state = 'playing'

	def __init__(self):

		libtcod.console_set_custom_font('terminal8x12_gs_tc.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
		libtcod.console_init_root(Game.SCREEN_WIDTH, Game.SCREEN_HEIGHT, 'Libtcod Tutorial', False)
		con = libtcod.console_new(Game.SCREEN_WIDTH, Game.SCREEN_HEIGHT)

		self.player_action = None

		self.map = Map(Game.MAP_WIDTH, Game.MAP_HEIGHT, con)
		self.player = Object(self.map.origin[0], self.map.origin[1], '@', 'Drew', libtcod.pink, con, True)
		self.map.objects.append(self.player);
		self.map.player = self.player

		
	def handle_keys(self):
		if Game.state == 'playing':
			key = libtcod.console_wait_for_keypress(True)

			if key.vk == libtcod.KEY_ESCAPE:
				return 'exit'

			if libtcod.console_is_key_pressed(libtcod.KEY_UP):
				self.player.move_or_attack(0, -1, self.map)
				self.map.fov_recompute = True

			elif libtcod.console_is_key_pressed(libtcod.KEY_DOWN):
				self.player.move_or_attack(0, 1, self.map)
				self.map.fov_recompute= True

			elif libtcod.console_is_key_pressed(libtcod.KEY_LEFT):
				self.player.move_or_attack(-1, 0, self.map)
				self.map.fov_recompute = True

			elif libtcod.console_is_key_pressed(libtcod.KEY_RIGHT):
				self.player.move_or_attack(1, 0, self.map)
				self.map.fov_recompute = True

			else:
				return 'didnt-take-turn'

	def run(self):
		while not libtcod.console_is_window_closed():
			libtcod.console_set_default_foreground(0, Game.COLOR_LIT)

			self.map.render_all()	

			libtcod.console_flush()

			player_action = self.handle_keys()
			# print player_action

			# if Game.state == 'playing' and player_action != 'didnt-take-turn':
			# 	for object in self.objects:
			# 		if object != self.player:
			# 			print 'The ' + object.name + ' growls!'

			if player_action == 'exit':
				break