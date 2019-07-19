import tcod as libtcod
from random import choice

from data.colors import colors
from components.fighter import Fighter
from death_functions import kill_monster, kill_player
from entity import Entity, get_blocking_entities_at_location
from fov_functions import initialize_fov, recompute_fov
from game_messages import MessageLog, Message
from game_states import GameState
from input_handlers import handle_keys
from render_functions import clear_all, render_all, RenderOrder
from map_objects.game_map import GameMap
from map_objects.game_world import GameWorld

def main():
	screen_width = 80 # /4 = 20
	screen_height = 50 # /4 ~= 12

	# Map panel parameters
	map_width = 45
	map_height = 40

	fov_algorithm = libtcod.FOV_SHADOW
	fov_light_walls = True
	fov_radius = 9

	# Health/Stats panel parameters
	bar_x = 4
	bar_width = 24
	panel_height = screen_height - map_height - 1
	panel_y = screen_height - panel_height

	# Message panel parameters
	message_x = bar_width + bar_x + 2
	message_width = screen_width - bar_width - bar_x - 2
	message_height = panel_height - 2

	message_log = MessageLog(message_x, message_width, message_height)

	# set up player entity and active entity list
	# TODO: Allow player to assign stats when starting to play
	fighter_component = Fighter(
		hp=30, 
		defense=5, spdefense=5, 
		attack=5, spattack=5, 
		speed=5)
	player = Entity(int(screen_width / 2), int(screen_height / 2), 
		'@', libtcod.white, 'Player', 
		render_order=RenderOrder.ACTOR, blocks=True, fighter=fighter_component)
	entities = []

	# set up console
	libtcod.console_set_custom_font('arial10x10.png', 
		libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
	libtcod.console_init_root(screen_width, screen_height, 
		'libtcod tutorial revised', False, 
		libtcod.RENDERER_SDL2, vsync=True)

	# set up all panels
	con = libtcod.console.Console(screen_width, screen_height)
	panel = libtcod.console.Console(screen_width, panel_height)

	# load map, entities and player
	game_world = GameWorld(map_width, map_height)
	game_world.loadfirstfloor(player, entities)

	# player field of vision variables
	fov_recompute = True
	fov_map = initialize_fov(game_world.currmap)

	# input variables
	key = libtcod.Key()
	mouse = libtcod.Mouse()

	# state variables
	game_state = GameState.PLAYERS_TURN

	while not libtcod.console_is_window_closed():
		# poll input
		libtcod.sys_check_for_event(
			libtcod.EVENT_KEY_PRESS | libtcod.EVENT_MOUSE, 
			key, mouse)

		# compute field of vision
		if fov_recompute:
			recompute_fov(fov_map, player.x, player.y, fov_radius, 
				fov_light_walls, fov_algorithm)

		# draw screen
		render_all(con, panel, entities, player, game_world.currmap, 
			message_log, fov_map, fov_recompute, 
			screen_width, screen_height, 
			bar_x, bar_width, panel_height, panel_y, mouse)
		fov_recompute = False
		libtcod.console_flush()

		# erase previous player position
		clear_all(con, entities)

		# parse input
		action = handle_keys(key)

		move = action.get('move')
		exit = action.get('exit')
		fullscreen = action.get('fullscreen')
		confirm = action.get('confirm')
		cancel = action.get('cancel')
		wait = action.get('wait')

		player_turn_results = []

		# update
		if move and game_state == GameState.PLAYERS_TURN:
			dx, dy = move # saves dx and dy outside of the while loop too
			dest_x = player.x + dx
			dest_y = player.y + dy

			if not game_world.currmap.tileblocked(dest_x, dest_y):
				target = get_blocking_entities_at_location(
					entities, dest_x, dest_y)

				if target:
					if target.door:
						game_world.movetonextroom(player, entities, 
							target.door.direction)
						fov_map = initialize_fov(game_world.currmap)
						fov_recompute = True
						con.clear()
					elif target.stairs:
						pass
					else:
						attack_results = player.fighter.attacktarget(
							target, player.fighter.attacks[0])
						player_turn_results.extend(attack_results)
				else:
					player.move(dx, dy)
					fov_recompute = True

				if (game_state == GameState.PLAYERS_TURN):
					game_state = GameState.ENEMY_TURN

		if wait and game_state == GameState.PLAYERS_TURN:
			game_state = GameState.ENEMY_TURN

		if exit:
			return True

		if fullscreen:
			libtcod.console_set_fullscreen(
				not libtcod.console_is_fullscreen())

		for player_turn_result in player_turn_results:
			message = player_turn_result.get('message')
			dead_entity = player_turn_result.get('dead')

			if message:
				message_log.add_message(message)

			if dead_entity:
				if dead_entity == player:
					message, game_state = kill_player(dead_entity)
				else:
					message = kill_monster(dead_entity)

				message_log.add_message(message)

		if game_state == GameState.ENEMY_TURN:
			for entity in entities:
				if entity.ai:
					enemy_turn_results = entity.ai.take_turn(
						game_world.currmap, entities)

					for enemy_turn_result in enemy_turn_results:
						message = enemy_turn_result.get('message')
						dead_entity = enemy_turn_result.get('dead')

						if message:
							message_log.add_message(message)

						if dead_entity:
							if dead_entity == player:
								message, game_state = kill_player(dead_entity)
							else:
								message = kill_monster(dead_entity)

							message_log.add_message(message)

							if game_state == GameState.PLAYER_DEAD:
								break

					if game_state == GameState.PLAYER_DEAD:
						break
			else:
				game_state = GameState.PLAYERS_TURN

if __name__ == '__main__':
	main()