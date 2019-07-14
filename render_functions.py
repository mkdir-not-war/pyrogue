import tcod as libtcod

from enum import Enum

class RenderOrder(Enum):
	CORPSE = 1
	ITEM = 2
	ACTOR = 3

def bar_color(value, max_value):
	GREEN_THRESHOLD = 0.5
	YELLOW_THRESHOLD = 0.2
	RED_THRESHOLD = 0.0

	percent_health = float(value) / float(max_value)
	color = None

	if (percent_health > GREEN_THRESHOLD):
		color = libtcod.chartreuse
	elif (percent_health > YELLOW_THRESHOLD):
		color = libtcod.gold
	elif (percent_health > RED_THRESHOLD):
		color = libtcod.flame

	return color

def render_bar(panel, x, y, total_width, name, value, maximum, 
	bar_color, back_color):
	bar_width = int(float(value) / maximum * total_width)

	libtcod.console_set_default_background(panel, back_color)
	libtcod.console_rect(panel, x, y, total_width, 
		1, False, libtcod.BKGND_SET)

	libtcod.console_set_default_background(panel, bar_color)
	if bar_width > 0:
		libtcod.console_rect(panel, x, y, bar_width, 
			1, False, libtcod.BKGND_SET)

	libtcod.console_set_default_foreground(panel, libtcod.black)
	libtcod.console_print_ex(panel, int(x + total_width / 2), y, 
		libtcod.BKGND_NONE, libtcod.CENTER,
		'{0}: {1}/{2}'.format(name, value, maximum))

def render_all(con, panel, entities, player, game_map, 
	fov_map, fov_recompute, screen_width, screen_height, 
	bar_width, panel_height, panel_y, colors):
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

	libtcod.console_blit(con, 0, 0, screen_width, screen_height, 0, 0, 0)

	libtcod.console_set_default_background(panel, libtcod.black)
	libtcod.console_clear(panel)

	render_bar(panel, 1, 1, bar_width, 'HP', 
		player.fighter.hp, player.fighter.max_hp,
		bar_color(player.fighter.hp, player.fighter.max_hp), 
		libtcod.grey)

	libtcod.console_blit(panel, 0, 0, screen_width, panel_height, 0, 0, panel_y)


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