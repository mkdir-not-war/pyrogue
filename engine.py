import tcod as libtcod
from random import choice

from entity import Entity
from input_handlers import handle_keys
from render_functions import clear_all, render_all
from map_objects.game_map import GameMap

def main():
	screen_width = 80
	screen_height = 50

	map_width = 45
	map_height = 45

	colors = {
		'dark_ground': libtcod.Color(204, 120, 96),
		'dark_wall': libtcod.Color(179, 51, 16),
		'dark_tree': libtcod.Color(143, 181, 100),
		'dark_water': libtcod.Color(191, 205, 255)
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

	game_map = GameMap(map_width, map_height)
	game_map.generate()
	player.x, player.y = game_map.playerspawn()

	key = libtcod.Key()
	mouse = libtcod.Mouse()

	while not libtcod.console_is_window_closed():
		# poll input
		libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS, key, mouse)

		# draw screen
		render_all(con, entities, game_map, screen_width, screen_height, colors)
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

		if exit:
			return True

		if fullscreen:
			libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())

if __name__ == '__main__':
	main()