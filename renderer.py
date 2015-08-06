import game
import libtcodpy as libtcod
import textwrap
from map import Map

class Renderer:

	SCREEN_WIDTH = 80
	SCREEN_HEIGHT = 50
	LIMIT_FPS = 20
	FOV_ALGO = 0
	FOV_LIGHT_WALLS = True
	TORCH_RADIUS = 5
	BAR_WIDTH = 20
	PANEL_HEIGHT = 7
	PANEL_Y = SCREEN_HEIGHT - PANEL_HEIGHT
	MSG_X = BAR_WIDTH + 2
	MSG_WIDTH = SCREEN_WIDTH - BAR_WIDTH
	MSG_HEIGHT = PANEL_HEIGHT - 1
	INVENTORY_WIDTH = 50
	LEVEL_SCREEN_WIDTH = 40
	CHARACTER_SCREEN_WIDTH = 30


	# libtcod.console_set_custom_font('fonts/terminal8x12_gs_tc.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
	libtcod.console_set_custom_font('fonts/terminal8x12_gs_ro.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_ASCII_INROW)
	libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, 'Roguelike', False)
	libtcod.sys_set_fps(LIMIT_FPS)

	main_console = libtcod.console_new(SCREEN_WIDTH, SCREEN_HEIGHT)
	panel = libtcod.console_new(SCREEN_WIDTH, PANEL_HEIGHT)

	def __init__(self, map, player, messages=[]):
		self.map = map
		self.messages = messages
		self.player = player

	def add_message(self, message, color):
		new_msg_lines = textwrap.wrap(message, Renderer.MSG_WIDTH)

		for line in new_msg_lines:
			if len(self.messages) == Renderer.MSG_HEIGHT:
				del self.messages[0]
			self.messages.append( (line, color) )

	def render_messages(self):
		y = 1
		for (line, color) in self.messages:
			libtcod.console_set_default_foreground(Renderer.panel, color)
			libtcod.console_print_ex(Renderer.panel, Renderer.MSG_X, y, libtcod.BKGND_NONE, libtcod.LEFT, line)
			y += 1

	@staticmethod
	def clear_console():
		libtcod.console_clear(Renderer.main_console)

	@staticmethod
	def menu(header, options, width, transparency=.7):
		if header == '':
			header_height = 0

		if len(options) > 26:
			raise ValueError('Cannot have a menu with more than 26 options')

		header_height = libtcod.console_get_height_rect(Renderer.main_console, 0, 0, width, Renderer.SCREEN_HEIGHT, header)
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

		x = Renderer.SCREEN_WIDTH/2 - width/2
		y = Renderer.SCREEN_HEIGHT/2 - height/2

		libtcod.console_blit(window, 0, 0, width, height, 0, x, y, 1.0, transparency)
		libtcod.console_flush()

		key = libtcod.console_wait_for_keypress(True)
		key = libtcod.console_wait_for_keypress(True)

		index = key.c - ord('a')
		if index >= 0 and index < len(options):
			return index
		return None

	def render_target_tile(self, box, x, y):
		libtcod.console_blit(box, 0, 0, 1, 1, 0, x, y, 1.0, 0.6)
		libtcod.console_flush()

	def render_names_under_target(self, x, y):
		names = [obj.name.capitalize() for obj in self.map.objects
			if obj.x == x and obj.y == y and self.map.is_in_fov(obj)]

		names = ', '.join(names)

		libtcod.console_set_default_foreground(Renderer.panel, libtcod.light_grey)
		libtcod.console_print_ex(Renderer.panel, 1, 0, libtcod.BKGND_NONE, libtcod.LEFT, names)
		libtcod.console_blit(Renderer.panel, 0, 0, Renderer.SCREEN_WIDTH, Renderer.PANEL_HEIGHT, 0, 0, Renderer.PANEL_Y)


	def render_bar(self, x, y, total_width, name, value, maximum, bar_color, back_color):
		bar_width = int(float(value) / maximum * total_width)

		#render the background
		libtcod.console_set_default_background(Renderer.panel, back_color)
		libtcod.console_rect(Renderer.panel, x, y, total_width, 1, False, libtcod.BKGND_SCREEN)

		#render the bar on top
		libtcod.console_set_default_background(Renderer.panel, bar_color)
		if bar_width > 0:
			libtcod.console_rect(Renderer.panel, x, y, bar_width, 1, False, libtcod.BKGND_SCREEN)

		#render the text
		libtcod.console_set_default_foreground(Renderer.panel, libtcod.white)
		libtcod.console_print_ex(Renderer.panel, x + total_width / 2, y, libtcod.BKGND_NONE, libtcod.CENTER, name + ': ' + str(value) + '/' + str(maximum))


	def render_all(self):
		self.map.recompute_fov()

		self.render_walls_and_floor()
		self.render_all_objects()
		libtcod.console_blit(Renderer.main_console, 0, 0, Renderer.SCREEN_WIDTH, Renderer.SCREEN_HEIGHT, 0, 0, 0)

		self.render_panel()
		libtcod.console_blit(Renderer.panel, 0, 0, Renderer.SCREEN_WIDTH, Renderer.PANEL_HEIGHT, 0, 0, Renderer.PANEL_Y)

		libtcod.console_flush()


	def render_panel(self):
		libtcod.console_set_default_background(Renderer.panel, libtcod.black)
		libtcod.console_clear(Renderer.panel)

		self.render_messages()
		self.render_bar(1, 1, Renderer.BAR_WIDTH, 'HP', self.player.fighter.hp, self.player.fighter.max_hp, libtcod.light_red, libtcod.dark_red)
		self.render_bar(1, 3, Renderer.BAR_WIDTH, 'MP', self.player.job.mp, self.player.job.max_mp, libtcod.light_blue, libtcod.dark_blue)
		libtcod.console_print_ex(Renderer.panel, 1, 5, libtcod.BKGND_NONE, libtcod.LEFT, 'Dungeon level ' + str(game.Game.dungeon_level))


	def render_all_objects(self):
		for object in self.map.objects:
			if object != self.player:
				self.render_object(object)
		self.render_object(self.player)


	def render_walls_and_floor(self):
		for y in range(self.map.height):
			for x in range(self.map.width):
				visible = libtcod.map_is_in_fov(self.map.fov_map, x, y)
				wall = self.map[x][y].block_sight
				if not visible:
					if self.map[x][y].explored:
						if wall:
							libtcod.console_put_char_ex(Renderer.main_console, x, y, libtcod.CHAR_BLOCK2, Map.COLOR_UNLIT, libtcod.black)
						else:
							libtcod.console_put_char_ex(Renderer.main_console, x, y, '.', Map.COLOR_UNLIT, libtcod.black)
				else:
					self.map[x][y].explored = True
					if wall:
						libtcod.console_put_char_ex(Renderer.main_console, x, y, libtcod.CHAR_BLOCK2, Map.COLOR_LIT, libtcod.black)
					else:
						libtcod.console_put_char_ex(Renderer.main_console, x, y, '.', Map.COLOR_LIT, libtcod.black)


	def render_object(self, object):
		if self.map.is_in_fov(object):
			libtcod.console_set_default_foreground(Renderer.main_console, object.color)
			libtcod.console_put_char(Renderer.main_console, object.x, object.y, object.char, libtcod.BKGND_NONE)

		elif object.always_visible and self.map[object.x][object.y].explored:
			darker = object.color * .65
			libtcod.console_set_default_foreground(Renderer.main_console, darker)
			libtcod.console_put_char(Renderer.main_console, object.x, object.y, object.char, libtcod.BKGND_NONE)

	@staticmethod
	def render_main_screen(img):
		libtcod.image_blit_2x(img, 0, 0, 0)

		libtcod.console_set_default_foreground(0, libtcod.light_yellow)
		libtcod.console_print_ex(0, Renderer.SCREEN_WIDTH/2, Renderer.SCREEN_HEIGHT/2 - 4, libtcod.BKGND_NONE, libtcod.CENTER, 'Salty Territory')
		libtcod.console_print_ex(0, Renderer.SCREEN_WIDTH/2, Renderer.SCREEN_HEIGHT - 2, libtcod.BKGND_NONE, libtcod.CENTER, 'By Drew')
