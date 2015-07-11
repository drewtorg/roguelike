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
	INVENTORY_WIDTH = 50

	state = 'playing'
	game_msgs = []
	mouse = libtcod.Mouse()
	key = libtcod.Key()
	inventory = []
	main_console = libtcod.console_new(Game.SCREEN_WIDTH, Game.SCREEN_HEIGHT)
	panel = libtcod.console_new(Game.SCREEN_WIDTH, Game.PANEL_HEIGHT)
	map = Map(Game.MAP_WIDTH, Game.MAP_HEIGHT)
	player = None

	def __init__(self):
		libtcod.console_set_custom_font('fonts/terminal8x12_gs_tc.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
		libtcod.console_init_root(Game.SCREEN_WIDTH, Game.SCREEN_HEIGHT, 'Libtcod Tutorial', False)
		libtcod.sys_set_fps(Game.LIMIT_FPS)

		Game.player_action = None

		fighter_component = Components.Fighter(hp=30, defense=2, power=5, death_function=Components.player_death)
		player = Object(Game.map.origin[0], Game.map.origin[1], '@', 'Drew', libtcod.pink, Game.map, blocks=True, fighter=fighter_component)
		Game.map.objects.append(Game.player)

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
			libtcod.console_set_default_foreground(Game.panel, color)
			libtcod.console_print_ex(Game.panel, Game.MSG_X, y, libtcod.BKGND_NONE, libtcod.LEFT, line)
			y += 1

	def get_names_under_mouse(self):
		(x, y) = (Game.mouse.cx, Game.mouse.cy)

		names = [obj.name.capitalize() for obj in Game.map.objects
			if obj.x == x and obj.y == y and libtcod.map_is_in_fov(Game.map.fov_map, obj.x, obj.y)]

		names = ', '.join(names)
		return names

	def render_look(self):
		libtcod.console_set_default_foreground(Game.panel, libtcod.light_grey)
		libtcod.console_print_ex(Game.panel, 1, 0, libtcod.BKGND_NONE, libtcod.LEFT, self.get_names_under_mouse())

	def render_bar(self, x, y, total_width, name, value, maximum, bar_color, back_color):
		bar_width = int(float(value) / maximum * total_width)

		#render the background
		libtcod.console_set_default_background(Game.panel, back_color)
		libtcod.console_rect(Game.panel, x, y, total_width, 1, False, libtcod.BKGND_SCREEN)

		#render the bar on top
		libtcod.console_set_default_background(Game.panel, bar_color)
		if bar_width > 0:
			libtcod.console_rect(Game.panel, x, y, bar_width, 1, False, libtcod.BKGND_SCREEN)

		#render the text
		libtcod.console_set_default_foreground(Game.panel, libtcod.white)
		libtcod.console_print_ex(Game.panel, x + total_width / 2, y, libtcod.BKGND_NONE, libtcod.CENTER, name + ': ' + str(value) + '/' + str(maximum))

	def render_all(self):
		Game.map.recompute_fov()
		self.render_walls_and_floor()
		self.render_all_objects()

		libtcod.console_blit(Game.main_console, 0, 0, Game.SCREEN_WIDTH, Game.SCREEN_HEIGHT, 0, 0, 0)
		libtcod.console_set_default_background(Game.panel, libtcod.black)
		libtcod.console_clear(Game.panel)

		self.render_messages()
		self.render_bar(1, 1, Game.BAR_WIDTH, 'HP', Game.player.fighter.hp, Game.player.fighter.max_hp, libtcod.light_red, libtcod.dark_red)
		self.render_look()

		libtcod.console_blit(Game.panel, 0, 0, Game.SCREEN_WIDTH, Game.PANEL_HEIGHT, 0, 0, Game.PANEL_Y)

	def render_all_objects(self):
		for object in Game.map.objects:
			if object != Game.player:
				self.draw_object(object)
		self.draw_object(Game.player)

	def render_walls_and_floor(self):
		for y in range(Game.MAP_HEIGHT):
			for x in range(Game.MAP_WIDTH):
				visible = libtcod.map_is_in_fov(Game.map.fov_map, x, y)
				wall = Game.map[x][y].block_sight
				if not visible:
					if Game.map[x][y].explored:
						if wall:
							libtcod.console_put_char_ex(Game.main_console, x, y, '#', Map.COLOR_UNLIT, libtcod.black)
						else:
							libtcod.console_put_char_ex(Game.main_console, x, y, '.', Map.COLOR_UNLIT, libtcod.black)
				else:
					Game.map[x][y].explored = True
					if wall:
						libtcod.console_put_char_ex(Game.main_console, x, y, '#', Map.COLOR_LIT, libtcod.black)
					else:
						libtcod.console_put_char_ex(Game.main_console, x, y, '.', Map.COLOR_LIT, libtcod.black)

	def draw_object(self, object):
		if libtcod.map_is_in_fov(Game.map.fov_map, object.x, object.y):
			libtcod.console_set_default_foreground(Game.main_console, object.color)
			libtcod.console_put_char(Game.main_console, object.x, object.y, object.char, libtcod.BKGND_NONE)

	def handle_keys(self):
		libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS|libtcod.EVENT_MOUSE, Game.key, Game.mouse)
		if Game.key.vk == libtcod.KEY_ESCAPE:
			return 'exit'

		if Game.state == 'playing':
			if Game.key.vk == libtcod.KEY_UP:
				Game.player.move_or_attack(0, -1)
				Game.map.fov_recompute = True

			elif Game.key.vk == libtcod.KEY_DOWN:
				Game.player.move_or_attack(0, 1)
				Game.map.fov_recompute= True

			elif Game.key.vk == libtcod.KEY_LEFT:
				Game.player.move_or_attack(-1, 0)
				Game.map.fov_recompute = True

			elif Game.key.vk == libtcod.KEY_RIGHT:
				Game.player.move_or_attack(1, 0)
				Game.map.fov_recompute = True

			else:
				key_char = chr(Game.key.c)

				if key_char == 'g':
					for object in Game.map.objects:
						if object.x == Game.player.x and object.y == Game.player.y and object.item:
							object.item.pick_up()
							break
				if key_char == 'i':
					chosen_item = self.inventory_menu('Press the next next to an item to use it, or any other to cancel.\n')
					if chosen_item is not None:
						chosen_item.use()

				return 'didnt-take-turn'

	def menu(self, header, options, width):
		if len(options) > 26:
			raise ValueError('Cannot have a menu with more than 26 options')

		header_height = libtcod.console_get_height_rect(Game.main_console, 0, 0, width, Game.SCREEN_HEIGHT, header)
		height = len(options) + header_height

		window = libtcod.console_new(width, height)

		libtcod.console_set_default_foreground(window, libtcod.white)
		libtcod.console_print_rect_ex(window, 0, 0, width, height, libtcod.BKGND_NONE, libtcod.LEFT, header)

		y = header_height
		letter_index = ord('a')
		for option_text in options:
			text = '(' + chr(letter_index) + ')' + option_text
			libtcod.console_print_ex(window, 0, y, libtcod.BKGND_NONE, libtcod.LEFT, text)
			y += 1
			letter_index += 1

		x = Game.SCREEN_WIDTH/2 - width/2
		y = Game.SCREEN_HEIGHT/2 - height/2
		libtcod.console_blit(window, 0, 0, width, height, 0, x, y, 1.0, 0.7) #0.7 is the transparency

		libtcod.console_flush()
		key = libtcod.console_wait_for_keypress(True)
		index = key.c - ord('a')
		if index >= 0 and index < len(options):
			return index
		return None

	def inventory_menu(self, header):
		if len(Game.inventory) == 0:
			options = ['Inventory is empty.']
		else:
			options = [item.name for item in Game.inventory]

		index = self.menu(header, options, Game.INVENTORY_WIDTH)
		if index is None or len(Game.inventory) == 0:
			return None
		return Game.inventory[index].item

	def run(self):
		Game.message('Welcome stranger! Prepare to perish in the Tombs of the Ancient Kings.', libtcod.light_green)

		while not libtcod.console_is_window_closed():
			libtcod.console_set_default_foreground(0, Game.COLOR_LIT)

			self.render_all()

			libtcod.console_flush()

			player_action = self.handle_keys()

			if Game.state == 'playing' and player_action != 'didnt-take-turn':
				for object in Game.map.objects:
					if object.ai:
						object.ai.take_turn()

			if player_action == 'exit':
				break
