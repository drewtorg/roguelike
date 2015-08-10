import game

def heroic_strike(player):
    monster = game.Game.target_monster(player.get_range())
    if monster is not None:
        damage = player.fighter.power
        game.Game.message(player.name.capitalize() + ' attacks ' + monster.name + ' for ' + str(damage) + ' hit points.')
        monster.fighter.take_damage(damage)
        return 'hit'
    return 'cancelled'

def bladestorm(player):
    monsters = game.Game.target_all_neighbors(player.x, player.y)
    if monsters != []:
        for monster in monsters:
            player.fighter.attack(monster)
        return 'hit'
    return 'cancelled'
