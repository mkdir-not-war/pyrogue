import tcod as libtcod

from enum import Enum

class RenderOrder(Enum):
	CORPSE = 1
	ITEM = 2
	ACTOR = 3

def render_all(con, entities, player, game_map, 
	fov_map, fov_recompute, screen_width, screen_height, colors):
	# Draw all the tiles in the game map
	if fov_recompute:
		for y in range(game_map.height):
			for x in range(game_map.width):
				visible = libtcod.map_is_in_fov(fov_map, x, y)
				name = game_map.tilename(x, y)

				if visible:
					if name == 'wall':
						libtcod.console_set_char_background(
							con, x, y, colors.get('light_wall'), libtcod.BKGND_SET)
					elif name == 'ground':
						libtcod.console_set_char_background(
							con, x, y, colors.get('light_ground'), libtcod.BKGND_SET)
					elif name == 'water':
						libtcod.console_set_char_background(
							con, x, y, colors.get('light_water'), libtcod.BKGND_SET)
					elif name == 'tree':
						libtcod.console_set_char_background(
							con, x, y, colors.get('light_tree'), libtcod.BKGND_SET)
					elif name == 'exit':
						libtcod.console_set_char_background(
							con, x, y, libtcod.yellow, libtcod.BKGND_SET)
					game_map.tiles[x + game_map.width * y].explored = True
				elif game_map.tiles[x + game_map.width * y].explored:
					if name == 'wall':
						libtcod.console_set_char_background(
							con, x, y, colors.get('dark_wall'), libtcod.BKGND_SET)
					elif name == 'ground':
						libtcod.console_set_char_background(
							con, x, y, colors.get('dark_ground'), libtcod.BKGND_SET)
					elif name == 'water':
						libtcod.console_set_char_background(
							con, x, y, colors.get('dark_water'), libtcod.BKGND_SET)
					elif name == 'tree':
						libtcod.console_set_char_background(
							con, x, y, colors.get('dark_tree'), libtcod.BKGND_SET)
					elif name == 'exit':
						libtcod.console_set_char_background(
							con, x, y, libtcod.gold, libtcod.BKGND_SET)

	# Draw all entities in the list
	entities_in_render_order = sorted(
		entities, key=lambda x: x.render_order.value)

	for entity in entities_in_render_order:
		draw_entity(con, entity, game_map, fov_map)

	libtcod.console_set_default_foreground(con, libtcod.white)
	libtcod.console_print_ex(con, 1, screen_height - 2, libtcod.BKGND_NONE,
		libtcod.LEFT, 'HP: {0:02}/{1:02}'.format(
			player.fighter.hp, player.fighter.max_hp))

	libtcod.console_blit(con, 0, 0, screen_width, screen_height, 0, 0, 0)


def clear_all(con, entities):
	for entity in entities:
		clear_entity(con, entity)


def draw_entity(con, entity, game_map, fov_map, showall=False):
	if (libtcod.map_is_in_fov(fov_map, entity.x, entity.y) or 
		(entity.door and 
		game_map.tiles[entity.x + game_map.width * entity.y].explored) or
		showall):
		libtcod.console_set_default_foreground(con, entity.color)
		libtcod.console_put_char(
			con, entity.x, entity.y, entity.char, libtcod.BKGND_NONE)

def clear_entity(con, entity):
	# erase the character that represents this object
	libtcod.console_put_char(con, entity.x, entity.y, ' ', libtcod.BKGND_NONE)