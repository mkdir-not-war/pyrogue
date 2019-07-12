class Tile:
	def __init__(self, name, blocked, block_sight=None):
		self.blocked = blocked
		self.name = name
		self.explored = False
		# by default, if a tile is blocked, it also blocks sight
		if block_sight is None:
			block_sight = blocked

		self.block_sight = block_sight

	def copy(self):
		newtile = Tile(self.name, self.blocked, self.block_sight)
		return newtile