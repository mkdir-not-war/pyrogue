import tcod as libtcod

def render_all(con, entities, game_map, fov_map, fov_recompute, screen_width, screen_height, colors):
	# Draw all the tiles in the game map
	if fov_recompute:
		for y in range(game_map.height):
			for x in range(game_map.width):
				visible = libtcod.map_is_in_fov(fov_map, x, y)
				name = game_map.tilename(x, y)

				if visible:
					if name == 'wall':
						libtcod.console_set_char_background(con, x, y, colors.get('light_wall'), libtcod.BKGND_SET)
					elif name == 'ground':
						libtcod.console_set_char_background(con, x, y, colors.get('light_ground'), libtcod.BKGND_SET)
					elif name == 'water':
						libtcod.console_set_char_background(con, x, y, colors.get('light_water'), libtcod.BKGND_SET)
					elif name == 'tree':
						libtcod.console_set_char_background(con, x, y, colors.get('light_tree'), libtcod.BKGND_SET)
					elif name == 'exit':
						libtcod.console_set_char_background(con, x, y, libtcod.yellow, libtcod.BKGND_SET)
					game_map.tiles[x + game_map.width * y].explored = True
				elif game_map.tiles[x + game_map.width * y].explored:
					if name == 'wall':
						libtcod.console_set_char_background(con, x, y, colors.get('dark_wall'), libtcod.BKGND_SET)
					elif name == 'ground':
						libtcod.console_set_char_background(con, x, y, colors.get('dark_ground'), libtcod.BKGND_SET)
					elif name == 'water':
						libtcod.console_set_char_background(con, x, y, colors.get('dark_water'), libtcod.BKGND_SET)
					elif name == 'tree':
						libtcod.console_set_char_background(con, x, y, colors.get('dark_tree'), libtcod.BKGND_SET)
					elif name == 'exit':
						libtcod.console_set_char_background(con, x, y, libtcod.gold, libtcod.BKGND_SET)

	# Draw all entities in the list
	for entity in entities:
		draw_entity(con, entity, fov_map)

	libtcod.console_blit(con, 0, 0, screen_width, screen_height, 0, 0, 0)


def clear_all(con, entities):
	for entity in entities:
		clear_entity(con, entity)


def draw_entity(con, entity, fov_map):
	if libtcod.map_is_in_fov(fov_map, entity.x, entity.y):
		libtcod.console_set_default_foreground(con, entity.color)
		libtcod.console_put_char(con, entity.x, entity.y, entity.char, libtcod.BKGND_NONE)


def clear_entity(con, entity):
	# erase the character that represents this object
	libtcod.console_put_char(con, entity.x, entity.y, ' ', libtcod.BKGND_NONE)