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

	def move_towards(self, target_x, target_y, game_map, entities, recalc=False):
		if (self.ai.path is False or recalc):
			self.ai.path = astar((self.x, self.y), (target_x, target_y), game_map)

		if (self.ai.path): 
			if (len(self.ai.path) > 0):
				dx, dy = self.ai.path[0]

				if not (game_map.tileblocked(dx, dy) or
					get_blocking_entities_at_location(entities, dx, dy)):
					self.move(dx, dy)
					self.ai.path.pop(0)
			else:
				self.ai.path = False


def get_blocking_entities_at_location(entities, dest_x, dest_y):
	for entity in entities:
		if entity.blocks and entity.x == dest_x and entity.y == dest_y:
			return entity
	return None