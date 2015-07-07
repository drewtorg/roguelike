import libtcodpy as libtcod
from tile import Tile
from object import Object
from rect import Rect
from map import Map
import components as Components

class Game:

	SCREEN_WIDTH = 80
	SCREEN_HEIGHT = 50
	LIMIT_FPS = 20
	MAP_WIDTH = 80
	MAP_HEIGHT = 43
	FOV_ALGO = 0
	FOV_LIGHT_WALLS = True
	TORCH_RADIUS = 5
	COLOR_LIT = libtcod.lighter_grey
	COLOR_UNLIT = libtcod.dark_grey
	BAR_WIDTH = 20
	PANEL_HEIGHT = 7
	PANEL_Y = SCREEN_HEIGHT - PANEL_HEIGHT

	state = 'playing'

	def __init__(self):
		libtcod.console_set_custom_font('fonts/terminal8x12_gs_tc.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
		libtcod.console_init_root(Game.SCREEN_WIDTH, Game.SCREEN_HEIGHT, 'Libtcod Tutorial', False)
		self.con = libtcod.console_new(Game.SCREEN_WIDTH, Game.SCREEN_HEIGHT)

		self.player_action = None

		self.map = Map(Game.MAP_WIDTH, Game.MAP_HEIGHT, self.con)
		fighter_component = Components.Fighter(hp=30, defense=2, power=5, death_function=Components.player_death)
		self.player = Object(self.map.origin[0], self.map.origin[1], '@', 'Drew', libtcod.pink, self.con, self.map, blocks=True, fighter=fighter_component)
		self.map.objects.append(self.player);
		self.map.player = self.player

		self.panel = libtcod.console_new(Game.SCREEN_WIDTH, Game.PANEL_HEIGHT)

	def render_bar(self, x, y, total_width, name, value, maximum, bar_color, back_color):
		bar_width = int(float(value) / maximum * total_width)

		#render the background
		libtcod.console_set_default_background(self.panel, back_color)
		libtcod.console_rect(self.panel, x, y, total_width, 1, False, libtcod.BKGND_SCREEN)

		#render the bar on top
		libtcod.console_set_default_background(self.panel, bar_color)
		if bar_width > 0:
			libtcod.console_rect(self.panel, x, y, bar_width, 1, False, libtcod.BKGND_SCREEN)

		libtcod.console_set_default_foreground(self.panel, libtcod.white)
		libtcod.console_print_ex(self.panel, x + total_width / 2, y, libtcod.BKGND_NONE, libtcod.CENTER, name + ': ' + str(value) + '/' + str(maximum))

	def render_all(self):
		self.map.recompute_fov()

		for y in range(Game.MAP_HEIGHT):
			for x in range(Game.MAP_WIDTH):
				visible = libtcod.map_is_in_fov(self.map.fov_map, x, y)
				wall = self.map[x][y].block_sight
				if not visible:
					if self.map[x][y].explored:
						if wall:
							libtcod.console_put_char_ex(self.con, x, y, '#', Map.COLOR_UNLIT, libtcod.black)
						else:
							libtcod.console_put_char_ex(self.con, x, y, '.', Map.COLOR_UNLIT, libtcod.black)
				else:
					self.map[x][y].explored = True
					if wall:
						libtcod.console_put_char_ex(self.con, x, y, '#', Map.COLOR_LIT, libtcod.black)
					else:
						libtcod.console_put_char_ex(self.con, x, y, '.', Map.COLOR_LIT, libtcod.black)

		for object in self.map.objects:
			if object != self.player:
				object.draw()
		self.player.draw()

		libtcod.console_blit(self.con, 0, 0, Game.SCREEN_WIDTH, Game.SCREEN_HEIGHT, 0, 0, 0)

		libtcod.console_set_default_background(self.panel, libtcod.black)
		libtcod.console_clear(self.panel)

		self.render_bar(1, 1, Game.BAR_WIDTH, 'HP', self.player.fighter.hp, self.player.fighter.max_hp, libtcod.light_red, libtcod.dark_red)
		libtcod.console_blit(self.panel, 0, 0, Game.SCREEN_WIDTH, Game.PANEL_HEIGHT, 0, 0, Game.PANEL_Y)

	def handle_keys(self):
		key = libtcod.console_wait_for_keypress(True)

		if key.vk == libtcod.KEY_ESCAPE:
			return 'exit'

		if Game.state == 'playing':

			if libtcod.console_is_key_pressed(libtcod.KEY_UP):
				self.player.move_or_attack(0, -1)
				self.map.fov_recompute = True

			elif libtcod.console_is_key_pressed(libtcod.KEY_DOWN):
				self.player.move_or_attack(0, 1)
				self.map.fov_recompute= True

			elif libtcod.console_is_key_pressed(libtcod.KEY_LEFT):
				self.player.move_or_attack(-1, 0)
				self.map.fov_recompute = True

			elif libtcod.console_is_key_pressed(libtcod.KEY_RIGHT):
				self.player.move_or_attack(1, 0)
				self.map.fov_recompute = True

			else:
				return 'didnt-take-turn'

	def run(self):
		while not libtcod.console_is_window_closed():
			libtcod.console_set_default_foreground(0, Game.COLOR_LIT)

			self.render_all()

			libtcod.console_flush()

			player_action = self.handle_keys()

			if Game.state == 'playing' and player_action != 'didnt-take-turn':
				for object in self.map.objects:
					if object.ai:
						object.ai.take_turn()

			if player_action == 'exit':
				break
