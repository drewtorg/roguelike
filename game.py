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
	LEVEL_UP_BASE = 20
	LEVEL_UP_FACTOR = 15
	LEVEL_SCREEN_WIDTH = 40
	CHARACTER_SCREEN_WIDTH = 30

	libtcod.console_set_custom_font('fonts/terminal8x12_gs_tc.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
	libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, 'Rougelike', False)
	libtcod.sys_set_fps(LIMIT_FPS)
	main_console = libtcod.console_new(SCREEN_WIDTH, SCREEN_HEIGHT)

	@staticmethod
	def new_game():
		Game.state = 'playing'
		Game.dungeon_level = 1
		Game.game_msgs = []
		Game.mouse = libtcod.Mouse()
		Game.key = libtcod.Key()
		Game.inventory = []
		Game.panel = libtcod.console_new(Game.SCREEN_WIDTH, Game.PANEL_HEIGHT)
		Game.map = Map(Game.MAP_WIDTH, Game.MAP_HEIGHT)

		libtcod.console_clear(Game.main_console)

		_fighter_component = Components.Fighter(hp=30, defense=2, power=5, xp=0, death_function=Components.player_death)
		Game.player = Object(Game.map.origin[0], Game.map.origin[1], '@', 'Drew', libtcod.pink, blocks=True, fighter=_fighter_component)
		Game.player.level = 1
		Game.map.add_object(Game.player)

		Game.message('Welcome stranger! Prepare to perish in the Tombs of the Ancient Kings.', libtcod.light_green)

	@classmethod
	def message(cls, new_msg, color=libtcod.white):
		new_msg_lines = textwrap.wrap(new_msg, Game.MSG_WIDTH)

		for line in new_msg_lines:
			if len(cls.game_msgs) == Game.MSG_HEIGHT:
				del cls.game_msgs[0]
			cls.game_msgs.append( (line, color) )

	@staticmethod
	def render_messages():
		y = 1
		for (line, color) in Game.game_msgs:
			libtcod.console_set_default_foreground(Game.panel, color)
			libtcod.console_print_ex(Game.panel, Game.MSG_X, y, libtcod.BKGND_NONE, libtcod.LEFT, line)
			y += 1

	@staticmethod
	def get_names_under_mouse():
		(x, y) = (Game.mouse.cx, Game.mouse.cy)

		names = [obj.name.capitalize() for obj in Game.map.objects
			if obj.x == x and obj.y == y and Game.map.is_in_fov(obj)]

		names = ', '.join(names)
		return names

	@staticmethod
	def render_look():
		libtcod.console_set_default_foreground(Game.panel, libtcod.light_grey)
		libtcod.console_print_ex(Game.panel, 1, 0, libtcod.BKGND_NONE, libtcod.LEFT, Game.get_names_under_mouse())

	@staticmethod
	def render_bar(x, y, total_width, name, value, maximum, bar_color, back_color):
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

	@staticmethod
	def render_all():
		Game.map.recompute_fov()

		Game.render_walls_and_floor()
		Game.render_all_objects()
		libtcod.console_blit(Game.main_console, 0, 0, Game.SCREEN_WIDTH, Game.SCREEN_HEIGHT, 0, 0, 0)

		Game.render_panel()
		libtcod.console_blit(Game.panel, 0, 0, Game.SCREEN_WIDTH, Game.PANEL_HEIGHT, 0, 0, Game.PANEL_Y)

		libtcod.console_flush()

	@staticmethod
	def render_panel():
		libtcod.console_set_default_background(Game.panel, libtcod.black)
		libtcod.console_clear(Game.panel)

		Game.render_messages()
		Game.render_bar(1, 1, Game.BAR_WIDTH, 'HP', Game.player.fighter.hp, Game.player.fighter.max_hp, libtcod.light_red, libtcod.dark_red)
		Game.render_look()
		libtcod.console_print_ex(Game.panel, 1, 3, libtcod.BKGND_NONE, libtcod.LEFT, 'Dungeon level ' + str(Game.dungeon_level))

	@staticmethod
	def render_all_objects():
		for object in Game.map.objects:
			if object != Game.player:
				Game.draw_object(object)
		Game.draw_object(Game.player)

	@staticmethod
	def render_walls_and_floor():
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

	@staticmethod
	def draw_object(object):
		if Game.map.is_in_fov(object):
			libtcod.console_set_default_foreground(Game.main_console, object.color)
			libtcod.console_put_char(Game.main_console, object.x, object.y, object.char, libtcod.BKGND_NONE)

		elif object.always_visible and Game.map[object.x][object.y].explored:
			darker = object.color * .65
			libtcod.console_set_default_foreground(Game.main_console, darker)
			libtcod.console_put_char(Game.main_console, object.x, object.y, object.char, libtcod.BKGND_NONE)

	@staticmethod
	def menu(header, options, width):
		if header == '':
			header_height = 0

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
		key = libtcod.console_wait_for_keypress(True)
		index = key.c - ord('a')
		if index >= 0 and index < len(options):
			return index
		return None

	@staticmethod
	def inventory_menu(header):
		if len(Game.inventory) == 0:
			options = ['Inventory is empty.']
		else:
			options = [item.name for item in Game.inventory]

		index = Game.menu(header, options, Game.INVENTORY_WIDTH)
		if index is None or len(Game.inventory) == 0:
			return None
		return Game.inventory[index].item

	@staticmethod
	def main_menu():
		img = libtcod.image_load('img/menu_background1.png')

		while not libtcod.console_is_window_closed():
			libtcod.image_blit_2x(img, 0, 0, 0)

			libtcod.console_set_default_foreground(0, libtcod.light_yellow)
			libtcod.console_print_ex(0, Game.SCREEN_WIDTH/2, Game.SCREEN_HEIGHT/2 - 4, libtcod.BKGND_NONE, libtcod.CENTER, 'TITLE HERE')
			libtcod.console_print_ex(0, Game.SCREEN_WIDTH/2, Game.SCREEN_HEIGHT - 2, libtcod.BKGND_NONE, libtcod.CENTER, 'By Drew')

			choice = Game.menu('', ['Play a new game', 'Continue current game', 'Quit'], 24)

			if choice == 0:
				Game.new_game()
				Game.run()
			elif choice == 1:
				try:
					Game.run()
				except:
					Game.msgbox('\n No saved game to load.\n', 24)
					continue
			elif choice == 2:
				break

	@staticmethod
	def msgbox(text, width=50):
		Game.menu(text, [], width)

	@staticmethod
	def target_tile(max_range=None):
		while True:
			libtcod.console_flush()
			libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS|libtcod.EVENT_MOUSE, Game.key, Game.mouse)
			Game.render_all()

			(x, y) = (Game.mouse.cx, Game.mouse.cy)

			if (Game.mouse.lbutton_pressed and Game.map.is_tile_in_fov(x, y)) and (max_range is None or Game.player.distance(x, y) <= max_range):
				return (x, y)

			if Game.mouse.rbutton_pressed or Game.key.vk == libtcod.KEY_ESCAPE:
				return (None, None)

	@staticmethod
	def target_monster(max_range=None):
		while True:
			(x, y) = Game.target_tile(max_range)
			if x is None:
				return None

			for obj in Game.map.objects:
				if obj.x == x and obj.y == y and obj.fighter and obj != Game.player:
					return obj

	@staticmethod
	def update():
		for object in Game.map.objects:
			object.update()

	@staticmethod
	def next_level():
		Game.message('You take a moment to rest, and recover your strength.', libtcod.light_violet)
		Game.player.fighter.heal(Game.player.fighter.max_hp / 2)

		Game.message('You descend deeper into the heart of the dungeon...', libtcod.red)
		libtcod.console_clear(Game.main_console)
		Game.map = Map(Game.MAP_WIDTH, Game.MAP_HEIGHT)
		Game.player.x = Game.map.origin[0]
		Game.player.y = Game.map.origin[1]
		Game.map.add_object(Game.player)
		Game.dungeon_level += 1

	@staticmethod
	def check_level_up():
		level_up_exp = Game.get_exp_to_level()
		
		if Game.player.fighter.xp >= level_up_exp:
			Game.player.level += 1
			Game.player.fighter.xp -= level_up_exp
			Game.message('Your battle skills grow stronger! You reached level ' + str(Game.player.level) + '!', libtcod.yellow)

			choice = None
			while choice is None:
				choice = Game.menu('Level up! Choose a stat to raise:\n',
					['Constitution (+20 HP, from (' + str(Game.player.fighter.max_hp) + ')',
					'Strength (+1 attack, from (' + str(Game.player.fighter.power) + ')',
					'Agility (+1 defense, from (' + str(Game.player.fighter.defense) + ')'], Game.LEVEL_SCREEN_WIDTH)
			if choice == 0:
				Game.player.fighter.max_hp += 20
				Game.player.fighter.hp += 20
			elif choice == 1:
				Game.player.fighter.power += 1
			elif choice == 2:
				Game.player.fighter.defense += 1

	@staticmethod
	def get_exp_to_level():
		return Game.LEVEL_UP_BASE + Game.player.level * Game.LEVEL_UP_FACTOR

	@staticmethod
	def try_pick_up():
		for object in Game.map.objects:
			if object.x == Game.player.x and object.y == Game.player.y and object.item:
				object.item.pick_up()
				return
		Game.message('You wait.', libtcod.green)

	@staticmethod
	def handle_keys():
		libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS|libtcod.EVENT_MOUSE, Game.key, Game.mouse)
		if Game.key.vk == libtcod.KEY_ESCAPE:
			return 'exit'

		if Game.state == 'playing':
			#movement keys
			Game.map.fov_recompute = True
			if Game.key.vk == libtcod.KEY_UP or Game.key.vk == libtcod.KEY_KP8:
				Game.player.move_or_attack(0, -1)
			elif Game.key.vk == libtcod.KEY_DOWN or Game.key.vk == libtcod.KEY_KP2:
				Game.player.move_or_attack(0, 1)
			elif Game.key.vk == libtcod.KEY_LEFT or Game.key.vk == libtcod.KEY_KP4:
				Game.player.move_or_attack(-1, 0)
			elif Game.key.vk == libtcod.KEY_RIGHT or Game.key.vk == libtcod.KEY_KP6:
				Game.player.move_or_attack(1, 0)
			elif Game.key.vk == libtcod.KEY_HOME or Game.key.vk == libtcod.KEY_KP7:
				Game.player.move_or_attack(-1, -1)
			elif Game.key.vk == libtcod.KEY_PAGEUP or Game.key.vk == libtcod.KEY_KP9:
				Game.player.move_or_attack(1, -1)
			elif Game.key.vk == libtcod.KEY_END or Game.key.vk == libtcod.KEY_KP1:
				Game.player.move_or_attack(-1, 1)
			elif Game.key.vk == libtcod.KEY_PAGEDOWN or Game.key.vk == libtcod.KEY_KP3:
				Game.player.move_or_attack(1, 1)
			elif Game.key.vk == libtcod.KEY_KP5:
				Game.try_pick_up()
				pass

			else:
				Game.map.fov_recompute = False
				key_char = chr(Game.key.c)

				if key_char == 'g':
					Game.try_pick_up()

				if key_char == 'i':
					chosen_item = Game.inventory_menu('Press the key next to an item to use it.\n')
					if chosen_item is not None:
						chosen_item.use()

				if key_char == 'd':
					chosen_item = Game.inventory_menu('Press the key next to an item to drop it.\n')
					if chosen_item is not None:
						chosen_item.drop()

				if key_char == '<':
					if Game.map.stairs.x == Game.player.x and Game.map.stairs.y == Game.player.y:
						Game.next_level()

				if key_char == 'c':
					level_up_exp = Game.get_exp_to_level()
					Game.msgbox('Character Information\n\nLevel: ' + str(Game.player.level) + '\nExperience: ' + str(Game.player.fighter.xp) +
						'\nExperience to level up: ' + str(level_up_exp) + '\n\nMaximum HP: ' + str(Game.player.fighter.max_hp) +
						'\nAttack: ' + str(Game.player.fighter.power) + '\nDefense: ' + str(Game.player.fighter.defense), Game.CHARACTER_SCREEN_WIDTH)

				return 'didnt-take-turn'

	@staticmethod
	def run():
		player_action = None

		while not libtcod.console_is_window_closed():
			libtcod.console_set_default_foreground(0, Game.COLOR_LIT)

			Game.render_all()

			Game.check_level_up()

			player_action = Game.handle_keys()

			if player_action == 'exit':
				break

			if Game.state == 'playing' and player_action != 'didnt-take-turn':
				Game.update()
