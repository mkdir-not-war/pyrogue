from components.ai import astar

class Entity:
	def __init__(self, x, y, char, color, name, 
		blocks=False, fighter=None, ai=None, door=None):

		self.x = x
		self.y = y
		self.char = char
		self.color = color
		self.name = name
		self.blocks = blocks
		self.fighter = fighter
		self.ai = ai
		self.door = door

		if self.fighter:
			self.fighter.owner = self

		if self.ai:
			self.ai.owner = self

		if self.door:
			self.door.owner = self

	def move(self, dx, dy):
		self.x += dx
		self.y += dy

	def move_towards(self, game_map, entities, target, recalc=False):
		if (self.ai.path is False or recalc):
			assert(not target is None)
			self.ai.path = astar((self.x, self.y), 
				(target[0], target[1]), game_map)

		if (self.ai.path): 
			if (len(self.ai.path) > 0):
				x, y = self.ai.path[0]
				if not (game_map.tileblocked(x, y) or
					get_blocking_entities_at_location(entities, x, y)):
					self.move(x-self.x, y-self.y)
					self.ai.path.pop(0)
					return True
			else:
				self.ai.path = False
		return False


def get_blocking_entities_at_location(entities, dest_x, dest_y):
	for entity in entities:
		if entity.blocks and entity.x == dest_x and entity.y == dest_y:
			return entity
	return None