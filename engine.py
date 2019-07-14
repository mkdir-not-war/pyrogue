import tcod as libtcod
from random import choice

from components.fighter import Fighter
from entity import Entity, get_blocking_entities_at_location
from fov_functions import initialize_fov, recompute_fov
from game_states import GameState
from input_handlers import handle_keys
from render_functions import clear_all, render_all
from map_objects.game_map import GameMap
from map_objects.game_world import GameWorld

def main():
	screen_width = 80
	screen_height = 50

	map_width = 45
	map_height = 45

	fov_algorithm = libtcod.FOV_SHADOW
	fov_light_walls = True
	fov_radius = 9

	colors = {
		'light_ground': libtcod.Color(204, 120, 96),
		'light_wall': libtcod.Color(179, 51, 16),
		'light_tree': libtcod.Color(143, 181, 100),
		'light_water': libtcod.Color(191, 205, 255),
		'dark_ground': libtcod.Color(128, 75, 60),
		'dark_wall': libtcod.Color(64, 37, 30),
		'dark_tree': libtcod.Color(101, 128, 70),
		'dark_water': libtcod.Color(96, 103, 128)
	}

	# set up player entity and active entity list
	figther_component = Fighter(hp=30, defense=2, power=5)
	player = Entity(int(screen_width / 2), int(screen_height / 2), 
		'@', libtcod.white, 'Player', blocks=True, fighter=figther_component)
	entities = []

	# set up console
	libtcod.console_set_custom_font('arial10x10.png', 
		libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
	libtcod.console_init_root(screen_width, screen_height, 
		'libtcod tutorial revised', False)
	con = libtcod.console_new(screen_width, screen_height)

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
	portal = None
	dx, dy = (None, None)

	while not libtcod.console_is_window_closed():
		# poll input
		libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS, key, mouse)

		# compute field of vision
		if fov_recompute:
			recompute_fov(fov_map, player.x, player.y, fov_radius, 
				fov_light_walls, fov_algorithm)

		# draw screen
		render_all(con, entities, game_world.currmap, fov_map, fov_recompute, 
			screen_width, screen_height, colors)
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
						print('Open the door? y/n')
						game_state = GameState.OPEN_DOOR
						portal = target
						continue
					else:
						print('You kick the ' + target.name + 
							' in the shins, much to its dismay!')
				else:
					player.move(dx, dy)
					fov_recompute = True

				game_state = GameState.ENEMY_TURN

		if wait and game_state == GameState.PLAYERS_TURN:
			game_state = GameState.ENEMY_TURN

		if game_state == GameState.OPEN_DOOR:
			if confirm:
				game_world.movetonextroom(player, entities, 
					portal.door.direction)
				fov_map = initialize_fov(game_world.currmap)
				player.move(dx, dy) # move one step off the new door
				fov_recompute = True
				con.clear()
				game_state = GameState.PLAYERS_TURN
				portal = None		
			elif cancel:
				game_state = GameState.PLAYERS_TURN
				portal = None

		if exit:
			return True

		if fullscreen:
			libtcod.console_set_fullscreen(
				not libtcod.console_is_fullscreen())

		if game_state == GameState.ENEMY_TURN:
			for entity in entities:
				if entity.ai:
					entity.ai.take_turn(game_world.currmap, entities)
			game_state = GameState.PLAYERS_TURN

if __name__ == '__main__':
	main()