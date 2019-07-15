import tcod as libtcod

from game_messages import Message
from game_states import GameState
from render_functions import RenderOrder

def kill_player(player):
	player.char = '%'
	player.color = libtcod.dark_red

	return Message('You died!', libtcod.red), GameState.PLAYER_DEAD

def kill_monster(monster):
	death_message = Message('%s is dead!' % monster.name.capitalize(), libtcod.orange)

	monster.char = '%'
	monster.color = libtcod.dark_red
	monster.blocks = False
	monster.fighter = None
	monster.ai = None
	monster.name = 'remains of ' + monster.name
	monster.description = 'remains of ' + monster.description
	monster.render_order = RenderOrder.CORPSE

	return death_message