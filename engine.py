import tcod as libtcod
from random import choice

from entity import Entity
from fov_functions import initialize_fov, recompute_fov
from input_handlers import handle_keys
from render_functions import clear_all, render_all
from map_objects.game_map import GameMap

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

	player = Entity(int(screen_width / 2), int(screen_height / 2), 
		'@', libtcod.white)
	npc = Entity(int(screen_width / 2 - 5), int(screen_height / 2), 
		'@', libtcod.yellow)
	entities = [player] #[npc, player]

	libtcod.console_set_custom_font('arial10x10.png', 
		libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)

	libtcod.console_init_root(screen_width, screen_height, 
		'libtcod tutorial revised', False)

	con = libtcod.console_new(screen_width, screen_height)

	# load map and place player
	game_map = GameMap(map_width, map_height)
	exits = [False, False, False, False]
	exits[0] = False
	exits[1] = True
	exits[2] = True
	exits[3] = False
	game_map.generate(*exits)
	player.x, player.y = game_map.playerspawn()

	fov_recompute = True

	fov_map = initialize_fov(game_map)

	key = libtcod.Key()
	mouse = libtcod.Mouse()

	while not libtcod.console_is_window_closed():
		# poll input
		libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS, key, mouse)

		# compute field of vision
		if fov_recompute:
			recompute_fov(fov_map, player.x, player.y, fov_radius, 
				fov_light_walls, fov_algorithm)

		# draw screen
		render_all(con, entities, game_map, fov_map, fov_recompute, screen_width, screen_height, colors)
		fov_recompute = False
		libtcod.console_flush()

		# erase previous player position
		clear_all(con, entities)

		# parse input
		action = handle_keys(key)

		move = action.get('move')
		exit = action.get('exit')
		fullscreen = action.get('fullscreen')

		# update
		if move:
			dx, dy = move
			if not game_map.tileblocked(player.x + dx, player.y + dy):
				player.move(dx, dy)
				fov_recompute = True

		if exit:
			return True

		if fullscreen:
			libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())

if __name__ == '__main__':
	main()