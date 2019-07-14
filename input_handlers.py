import tcod as libtcod

def handle_keys(key):
	# movement keys
	key_char = chr(key.c)

	if key.vk == libtcod.KEY_UP:
		return {'move': (0, -1)}
	elif key.vk == libtcod.KEY_DOWN:
		return {'move': (0, 1)}
	elif key.vk == libtcod.KEY_LEFT:
		return {'move': (-1, 0)}
	elif key.vk == libtcod.KEY_RIGHT:
		return {'move': (1, 0)}

	elif key.vk == libtcod.KEY_SPACE:
		return {'wait': True}

	elif key_char == 'y':
		return {'confirm': True}
	elif key_char == 'n':
		return {'cancel': True}

	if key.vk == libtcod.KEY_ENTER and key.lalt:
		# Alt+Enter: toggle full screen
		return {'fullscreen': True}

	elif key.vk == libtcod.KEY_ESCAPE:
		# Exit the game
		return {'exit': True}

	# No key was pressed
	return {}