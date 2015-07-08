import libtcodpy as libtcod
from tile import Tile
from object import Object
from rect import Rect
from map import Map
import components as Components
import textwrap

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
	MSG_X = BAR_WIDTH + 2
	MSG_WIDTH = SCREEN_WIDTH - BAR_WIDTH
	MSG_HEIGHT = PANEL_HEIGHT - 1

	state = 'playing'
	game_msgs = []
	mouse = libtcod.Mouse()
	key = libtcod.Key()

	def __init__(self):
		libtcod.console_set_custom_font('fonts/terminal8x12_gs_tc.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
		libtcod.console_init_root(Game.SCREEN_WIDTH, Game.SCREEN_HEIGHT, 'Libtcod Tutorial', False)
		libtcod.sys_set_fps(Game.LIMIT_FPS)
		self.con = libtcod.console_new(Game.SCREEN_WIDTH, Game.SCREEN_HEIGHT)

		self.player_action = None

		self.map = Map(Game.MAP_WIDTH, Game.MAP_HEIGHT)
		fighter_component = Components.Fighter(hp=30, defense=2, power=5, death_function=Components.player_death)
		self.player = Object(self.map.origin[0], self.map.origin[1], '@', 'Drew', libtcod.pink, self.map, blocks=True, fighter=fighter_component)
		self.map.objects.append(self.player);
		self.map.player = self.player

		self.panel = libtcod.console_new(Game.SCREEN_WIDTH, Game.PANEL_HEIGHT)

	@classmethod
	def message(cls, new_msg, color=libtcod.white):
		new_msg_lines = textwrap.wrap(new_msg, Game.MSG_WIDTH)

		for line in new_msg_lines:
			if len(cls.game_msgs) == Game.MSG_HEIGHT:
				del cls.game_msgs[0]
			cls.game_msgs.append( (line, color) )

	def render_messages(self):
		y = 1
		for (line, color) in Game.game_msgs:
			libtcod.console_set_default_foreground(self.panel, color)
			libtcod.console_print_ex(self.panel, Game.MSG_X, y, libtcod.BKGND_NONE, libtcod.LEFT, line)
			y += 1

	def get_names_under_mouse(self):
		(x, y) = (Game.mouse.cx, Game.mouse.cy)

		names = [obj.name.capitalize() for obj in self.map.objects
			if obj.x == x and obj.y == y and libtcod.map_is_in_fov(self.map.fov_map, obj.x, obj.y)]

		names = ', '.join(names)
		return names

	def render_look(self):
		libtcod.console_set_default_foreground(self.panel, libtcod.light_grey)
		libtcod.console_print_ex(self.panel, 1, 0, libtcod.BKGND_NONE, libtcod.LEFT, self.get_names_under_mouse())

	def render_bar(self, x, y, total_width, name, value, maximum, bar_color, back_color):
		bar_width = int(float(value) / maximum * total_width)

		#render the background
		libtcod.console_set_default_background(self.panel, back_color)
		libtcod.console_rect(self.panel, x, y, total_width, 1, False, libtcod.BKGND_SCREEN)

		#render the bar on top
		libtcod.console_set_default_background(self.panel, bar_color)
		if bar_width > 0:
			libtcod.console_rect(self.panel, x, y, bar_width, 1, False, libtcod.BKGND_SCREEN)

		#render the text
		libtcod.console_set_default_foreground(self.panel, libtcod.white)
		libtcod.console_print_ex(self.panel, x + total_width / 2, y, libtcod.BKGND_NONE, libtcod.CENTER, name + ': ' + str(value) + '/' + str(maximum))

	def render_all(self):
		self.map.recompute_fov()
		self.render_walls_and_floor()
		self.render_all_objects()

		libtcod.console_blit(self.con, 0, 0, Game.SCREEN_WIDTH, Game.SCREEN_HEIGHT, 0, 0, 0)
		libtcod.console_set_default_background(self.panel, libtcod.black)
		libtcod.console_clear(self.panel)

		self.render_messages()
		self.render_bar(1, 1, Game.BAR_WIDTH, 'HP', self.player.fighter.hp, self.player.fighter.max_hp, libtcod.light_red, libtcod.dark_red)
		self.render_look()

		libtcod.console_blit(self.panel, 0, 0, Game.SCREEN_WIDTH, Game.PANEL_HEIGHT, 0, 0, Game.PANEL_Y)

	def render_all_objects(self):
		for object in self.map.objects:
			if object != self.player:
				self.draw_object(object)
		self.draw_object(self.player)

	def render_walls_and_floor(self):
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

	def draw_object(self, object):
		if libtcod.map_is_in_fov(self.map.fov_map, object.x, object.y):
			libtcod.console_set_default_foreground(self.con, object.color)
			libtcod.console_put_char(self.con, object.x, object.y, object.char, libtcod.BKGND_NONE)

	def handle_keys(self):
		libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS|libtcod.EVENT_MOUSE, Game.key, Game.mouse)
		if Game.key.vk == libtcod.KEY_ESCAPE:
			return 'exit'

		if Game.state == 'playing':
			if Game.key.vk == libtcod.KEY_UP:
				self.player.move_or_attack(0, -1)
				self.map.fov_recompute = True

			elif Game.key.vk == libtcod.KEY_DOWN:
				self.player.move_or_attack(0, 1)
				self.map.fov_recompute= True

			elif Game.key.vk == libtcod.KEY_LEFT:
				self.player.move_or_attack(-1, 0)
				self.map.fov_recompute = True

			elif Game.key.vk == libtcod.KEY_RIGHT:
				self.player.move_or_attack(1, 0)
				self.map.fov_recompute = True

			else:
				return 'didnt-take-turn'

	def run(self):
		Game.message('Welcome stranger! Prepare to perish in the Tombs of the Ancient Kings.', libtcod.light_green)

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
