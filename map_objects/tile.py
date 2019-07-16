class Tile:
	def __init__(self, name, blocked, block_sight=None, cost=None):
		self.blocked = blocked
		self.name = name

		# by default, if a tile is blocked, it also blocks sight
		if block_sight is None:
			block_sight = blocked
		# by default, cost of a tile is 1 if not blocked, 0 if it is
		if cost is None:
			if blocked:
				cost = 0
			else:
				cost = 1

		self.cost = cost
		self.block_sight = block_sight

	def copy(self):
		newtile = Tile(self.name, self.blocked, self.block_sight)
		return newtile