class Entity:
	def __init__(self, x, y, char, color, name, blocks=False, door=None):
		self.x = x
		self.y = y
		self.char = char
		self.color = color
		self.name = name
		self.blocks = blocks

		self.door = door

		if self.door:
			self.door.owner = self

	def move(self, dx, dy):
		self.x += dx
		self.y += dy

def get_blocking_entities_at_location(entities, dest_x, dest_y):
	for entity in entities:
		if entity.blocks and entity.x == dest_x and entity.y == dest_y:
			return entity
	return None