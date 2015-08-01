import libtcodpy as libtcod
from map import Map
import decoder
from player import Player
from renderer import Renderer

race_decoder = decoder.RaceDecoder('races/')

class Game:
    LEVEL_UP_BASE = 200
    LEVEL_UP_FACTOR = 150
    MAP_WIDTH = 80
    MAP_HEIGHT = 43

    @staticmethod
    def new_game(race):
        Game.state = 'playing'
        Game.dungeon_level = 1
        Game.mouse = libtcod.Mouse()
        Game.key = libtcod.Key()
        Game.map = Map(Game.MAP_WIDTH, Game.MAP_HEIGHT)

        _fighter_component = race_decoder.decode_race_fighter(race)
        _color = race_decoder.decode_race_color(race)
        Game.player = Player(Game.map.origin[0], Game.map.origin[1], '@', 'Drew', _color, fighter_component=_fighter_component, race=race)
        Game.map.add_object(Game.player)

        Game.renderer = Renderer(Game.map, Game.player)
        Game.renderer.clear_console()

        Game.message('Welcome stranger! Prepare to perish in the Tombs of the Ancient Kings.', libtcod.light_green)

    @staticmethod
    def message(new_msg, color=libtcod.white):
        Game.renderer.add_message(new_msg, color)

    @staticmethod
    def inventory_menu(header):
        if len(Game.player.inventory) == 0:
            options = ['Inventory is empty.']
        else:
            options = []
            for item in Game.player.inventory:
                text = item.name
                if item.equipment and item.equipment.is_equipped:
                    text = text + ' (on ' + item.equipment.slot + ')'
                options.append(text)

        index = Renderer.menu(header, options, Renderer.INVENTORY_WIDTH)
        if index is None or len(Game.player.inventory) == 0:
            return None
        return Game.player.inventory[index].item

    @staticmethod
    def main_menu():
        img = libtcod.image_load('img/menu_background1.png')

        while not libtcod.console_is_window_closed():
            Renderer.render_main_screen(img)

            choice = Renderer.menu('', ['Play a new game', 'Continue current game', 'Quit'], 24)

            if choice == 0:
                Renderer.render_main_screen(img)

                races = race_decoder.decode_all_races()
                race = Renderer.menu('Pick a race', races, 15)
                if race is None:
                    continue

                # Renderer.render_main_screen(img)
                #
                # classes = class_decoder.decode_all_classes()
                # class = Renderer.menu('Pick a class', classes, 15)
                Game.new_game(races[race].lower())
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
        Renderer.menu(text, [], width)

    @staticmethod
    def target_tile(max_range=None):
        box = libtcod.console_new(1, 1)
        x = Game.player.x
        y = Game.player.y
        libtcod.console_set_default_background(box, libtcod.orange)
        libtcod.console_clear(box)
        key = Game.key

        while (x, y) != (0, 0):
            Game.renderer.render_all()
            Game.renderer.render_names_under_target(x, y)
            Game.renderer.render_target_tile(box, x, y)

            key = libtcod.console_wait_for_keypress(True)
            key = libtcod.console_wait_for_keypress(True)

            direction = Game.get_direction(key)
            if direction is not None:
                x += direction[0]
                y += direction[1]

            else:
                return (None, None)

            if direction == (0, 0):
                if Game.map.is_tile_in_fov(x, y) and (max_range is None or Game.player.distance(x, y) <= max_range):
                    return (x, y)
                else:
                    Game.message('That is out of range.', libtcod.red)

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
        Game.dungeon_level += 1
        Game.map = Map(Game.MAP_WIDTH, Game.MAP_HEIGHT)
        Game.player.x = Game.map.origin[0]
        Game.player.y = Game.map.origin[1]
        Game.map.add_object(Game.player)

        Renderer.clear_console()
        Game.renderer = Renderer(Game.map, Game.player)

    @staticmethod
    def check_level_up():
        level_up_exp = Game.get_exp_to_level()

        while Game.player.fighter.xp >= level_up_exp:
            Game.player.level += 1
            Game.player.fighter.xp -= level_up_exp
            Game.message('Your battle skills grow stronger! You reached level ' + str(Game.player.level) + '!', libtcod.yellow)

            choice = None
            while choice is None:
                choice = Renderer.menu('Level up! Choose a stat to raise:\n',
                    ['Constitution (+20 HP, from (' + str(Game.player.fighter.max_hp) + ')',
                    'Strength (+1 attack, from (' + str(Game.player.fighter.power) + ')',
                    'Agility (+1 dexterity, from (' + str(Game.player.fighter.dexterity) + ')'], Renderer.LEVEL_SCREEN_WIDTH)

            if choice == 0:
                Game.player.fighter.base_max_hp += 20
                Game.player.fighter.hp += 20
            elif choice == 1:
                Game.player.fighter.base_power += 1
            elif choice == 2:
                Game.player.fighter.base_dexterity += 1
            renderer.render_all()

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
    def get_direction(key):
        if key.vk == libtcod.KEY_UP or key.vk == libtcod.KEY_KP8:
            return (0, -1)
        elif key.vk == libtcod.KEY_DOWN or key.vk == libtcod.KEY_KP2:
            return (0, 1)
        elif key.vk == libtcod.KEY_LEFT or key.vk == libtcod.KEY_KP4:
            return (-1, 0)
        elif key.vk == libtcod.KEY_RIGHT or key.vk == libtcod.KEY_KP6:
            return (1, 0)
        elif key.vk == libtcod.KEY_HOME or key.vk == libtcod.KEY_KP7:
            return (-1, -1)
        elif key.vk == libtcod.KEY_PAGEUP or key.vk == libtcod.KEY_KP9:
            return (1, -1)
        elif key.vk == libtcod.KEY_END or key.vk == libtcod.KEY_KP1:
            return (-1, 1)
        elif key.vk == libtcod.KEY_PAGEDOWN or key.vk == libtcod.KEY_KP3:
            return (1, 1)
        elif key.vk == libtcod.KEY_KP5 or key.vk == libtcod.KEY_ENTER:
            return (0, 0)
        return None

    @staticmethod
    def handle_keys():
        Game.key = libtcod.console_wait_for_keypress(True)
        Game.key = libtcod.console_wait_for_keypress(True)

        if Game.key.vk == libtcod.KEY_ESCAPE:
            return 'exit'

        if Game.state == 'playing':
            #movement keys
            Game.map.fov_recompute = True
            direction = Game.get_direction(Game.key)

            if direction is None:
                Game.map.fov_recompute = False
                key_char = chr(Game.key.c)

                if key_char == 'c':
                    level_up_exp = Game.get_exp_to_level()
                    Game.msgbox('Character Information\n\nLevel: ' + str(Game.player.level) + '\nExperience: ' + str(Game.player.fighter.xp) +
                        '\nExperience to level up: ' + str(level_up_exp) + '\n\nMaximum HP: ' + str(Game.player.fighter.max_hp) +
                        '\nAttack: ' + str(Game.player.fighter.power) + '\nDexterity: ' + str(Game.player.fighter.dexterity), Renderer.CHARACTER_SCREEN_WIDTH)

                elif key_char == 'd':
                    chosen_item = Game.inventory_menu('Press the key next to an item to drop it.\n')
                    if chosen_item is not None:
                        chosen_item.drop()

                elif key_char == 'g':
                    Game.try_pick_up()

                elif key_char == 'i':
                    chosen_item = Game.inventory_menu('Press the key next to an item to use it.\n')
                    if chosen_item is not None:
                        chosen_item.use()

                elif key_char == 'l':
                    Game.target_tile()

                elif key_char == '<':
                    if Game.map.stairs.x == Game.player.x and Game.map.stairs.y == Game.player.y:
                        Game.next_level()

                return 'didnt-take-turn'

            elif direction == (0, 0):
                Game.try_pick_up()
                pass

            else:
                Game.player.move_or_attack(direction[0], direction[1])


    @staticmethod
    def run():
        player_action = None

        while not libtcod.console_is_window_closed():
            Game.renderer.render_all()
            Game.check_level_up()

            player_action = Game.handle_keys()

            if player_action == 'exit':
                break

            if Game.state == 'playing' and player_action != 'didnt-take-turn':
                Game.update()
