import random
from math import sqrt
import tcod as libtcod

from components.door import Door
from components.fighter import Fighter
from components.ai import BasicMonster, astar

from entity import Entity
from map_objects.tile import Tile

wall = Tile('wall', True)
ground = Tile('ground', False)
water = Tile('water', True, False)
tree = Tile('tree', False, True, cost=3)

max_monsters_per_room = 12

class GameMap:
	def __init__(self, width, height):
		self.width = width
		self.height = height
		self.size = width * height
		self.tiles = self.initialize_tiles() # set in generate

		# set exits in generate
		self.exits = {}
		self.exits['north'] = None
		self.exits['south'] = None
		self.exits['west'] = None
		self.exits['east'] = None

		'''
		when you return to a room,
		totally spawn all new enemy entities, (same amount as original)
		unless remaining is zero. Once you kill an enemy in 
		the room, decrement this by one
		'''
		self.nummonsters = -1
		self.remainingmonsters = None

		self.costmap = [] # set in generate

	def initialize_tiles(self):
		tiles = [Tile('wall', True) for tile in range(self.size)]
		return tiles

	def tileblocked(self, x, y):
		if (not self.inbounds(x, y) or 
			self.tiles[x + self.width * y].blocked):
			return True
		return False

	def tilename(self, x, y):
		return self.tiles[x + self.width * y].name

	def copy(self):
		newmap = GameMap(self.width, self.height)
		for i in range(self.size):
			newmap.tiles[i] = self.tiles[i]
		newmap.exits = self.exits
		return newmap

	def getcostmap(self):
		result = [self.tiles[i].cost for i in range(self.size)]
		return result

	def getcost(self, x, y):
		result = self.costmap[x + self.width * y]
		return result

	def settile(self, point, tile):
		self.tiles[point[1] * self.width + point[0]] = tile.copy()

	def getgroundtiles(self):
		result = self.gettilesbytype('ground')
		return result

	def gettilesbytype(self, tilename):
		result = []
		for i in range(self.width):
			for j in range(self.height):
				point = tuple([i, j])
				if (self.tilename(*point) == tilename):
					result.append(point)
		# order: top to bottom -> left to right
		return result

	def generate(self, top=False, bottom=False, left=False, right=False):
		self.tiles = self.cellularautomata().tiles
		self.costmap = self.getcostmap()
		self.setexits(top=top, bottom=bottom, left=left, right=right)
		# spawn monsters only when you enter the room
		self.costmap = self.getcostmap()

	# clear entity list of previous room's entities, 
	# fill with this room's entities
	def enter(self, player, entities, entrancedir=None):
		entities.clear()
		entities.append(player)
		self.spawnexits(entities)
		if (self.remainingmonsters is None or self.remainingmonsters > 0):
			self.spawnmonsters(entities)
		if (entrancedir):
			player.x, player.y = self.exits[entrancedir]

	def inbounds(self, x, y, buffer=0):
		return (x < self.width - buffer and
				x >= buffer and
				y < self.height - buffer and
				y >= buffer)

	def adjacenttile(self, point, tiletype, buffer=0):
		result = []
		x = point[0]
		y = point[1]

		if (self.inbounds(x-1, y, buffer) and
			self.tilename(x-1, y) == tiletype.name):
			result.append(tuple([x-1, y]))
		if (self.inbounds(x+1, y, buffer) and
			self.tilename(x+1, y) == tiletype.name):
			result.append(tuple([x+1, y]))
			
		if (self.inbounds(x, y-1, buffer) and
			self.tilename(x, y-1) == tiletype.name):
			result.append(tuple([x, y-1]))
		if (self.inbounds(x, y+1, buffer) and
			self.tilename(x, y+1) == tiletype.name):
			result.append(tuple([x, y+1]))
			
		if (self.inbounds(x-1, y-1, buffer) and
			self.tilename(x-1, y-1) == tiletype.name):
			result.append(tuple([x-1, y-1]))
		if (self.inbounds(x-1, y+1, buffer) and
			self.tilename(x-1, y+1) == tiletype.name):
			result.append(tuple([x-1, y+1]))
		if (self.inbounds(x+1, y-1, buffer) and
			self.tilename(x+1, y-1) == tiletype.name):
			result.append(tuple([x+1, y-1]))
		if (self.inbounds(x+1, y+1, buffer) and
			self.tilename(x+1, y+1) == tiletype.name):
			result.append(tuple([x+1, y+1]))

		return len(result)

	# just set player's position upon entering new floor
	def spawnplayer(self, player, entities):
		groundtiles = self.getgroundtiles()
		pos = random.choice(groundtiles)

		while(True):
			# if no exit possible to reach, find new spot
			if (not self.checkexit(pos)):
				pos = random.choice(groundtiles)
				continue
			# if spot already has something on it, find new spot
			if (any([entity for entity in entities 
				if entity.x == pos[0] and entity.y == pos[1]])):
				pos = random.choice(groundtiles)
				continue
			# otherwise, the spot is good for spawnining
			break

		player.x, player.y = pos

	def spawnmonsters(self, entities):
		if (self.nummonsters < 0):
			self.nummonsters = random.randint(
				0, int(max_monsters_per_room / 2)) + \
				random.randint(0, int(max_monsters_per_room / 2))
		self.remainingmonsters = self.nummonsters
		groundtiles = []
		if (self.nummonsters > 0):
			groundtiles = [tile for tile in \
				self.getgroundtiles() if \
				self.adjacenttile(tile, ground) >= 4 and \
				self.inbounds(tile[0], tile[1], buffer=4)]
		else:
			return

		for i in range(self.nummonsters):
			pos = random.choice(groundtiles)

			if not any([entity for entity in entities 
				if entity.x == pos[0] and entity.y == pos[1]]):
				monster = None
				# orcs and trolls, for now ###
				if random.randint(0, 100) < 80:
					fighter_component = Fighter(hp=10, defense=0, power=3)
					ai_component = BasicMonster(self)
					monster = Entity(pos[0], pos[1], 'o', 
						libtcod.desaturated_green, 'Orc', blocks=True,
						fighter=fighter_component, ai=ai_component)
				else:
					fighter_component = Fighter(hp=10, defense=0, power=3)
					ai_component = BasicMonster(self)
					monster = Entity(pos[0], pos[1], 't', 
						libtcod.darker_green, 'Troll', blocks=True,
						fighter=fighter_component, ai=ai_component)
				##############################
				entities.append(monster)


	def checkexit(self, exit):
		groundtiles = self.getgroundtiles()
		randomsample = random.sample(groundtiles, int(self.size/60))
		numreached = 0
		total = len(randomsample)
		for tile in randomsample:
			if (astar(exit, tile, self)):
				numreached += 1
		if (numreached >= int(total / 3)):
			return True
		else:
			return False

	def spawnexits(self, entities):
		for exit in self.exits:
			pos = self.exits[exit]
			if (pos != None):
				if (self.tileblocked(pos[0], pos[1])):
					self.settile(pos, ground)
				door = Entity(pos[0], pos[1], 
					'>', libtcod.white, 
					'Door', blocks=True, door=Door(exit))
				entities.append(door)

	def setexits(self, top=False, left=False, right=False, bottom=False):
		# draw line in direction to edge with ground tiles
		# check to make sure the exits reach most of the randomsample spots
		if top:
			xpos = random.choice(range(self.width))
			mapexit = (xpos, 0)
			self.exits['north'] = mapexit
			distfromexit = 0
			while (not self.checkexit(mapexit)):
				if (distfromexit >= 5):
					xpos = random.choice(range(self.width))
					mapexit = (xpos, 0)
					self.exits['north'] = mapexit
					distfromexit = 0
				self.settile((xpos, distfromexit), ground)
				distfromexit += 1				  
		if left:
			ypos = random.choice(range(self.height))
			mapexit = (0, ypos)
			self.exits['west'] = mapexit
			distfromexit = 0
			while (not self.checkexit(mapexit)):
				if (distfromexit >= 5):
					ypos = random.choice(range(self.height))
					mapexit = (0, ypos)
					self.exits['west'] = mapexit
					distfromexit = 0
				self.settile((distfromexit, ypos), ground) 
				distfromexit += 1
		if right:
			ypos = random.choice(range(self.height))
			mapexit = (self.width-1, ypos)
			self.exits['east'] = mapexit
			distfromexit = 0
			while (not self.checkexit(mapexit)):
				if (distfromexit >= 5):
					ypos = random.choice(range(self.height))
					mapexit = (self.width-1, ypos)
					self.exits['east'] = mapexit
					distfromexit = 0
				self.settile((self.width-1-distfromexit, ypos), ground)
				distfromexit += 1
		if bottom:
			xpos = random.choice(range(self.width))
			mapexit = (xpos, self.height-1)
			self.exits['south'] = mapexit
			distfromexit = 0
			while (not self.checkexit(mapexit)):
				if (distfromexit >= 5):
					xpos = random.choice(range(self.width))
					mapexit = (xpos, self.height-1)
					self.exits['south'] = mapexit
					distfromexit = 0
				self.settile((xpos, self.height-1-distfromexit), ground)
				distfromexit += 1
				
	def cellularautomata(self):
		newmap = GameMap(self.width, self.height)

		scalemod = self.size / 8000 

		# large rooms, decent forests, small infrequent ponds
		percentwalls=.34
		percentwalls += 0.04 * sqrt(scalemod)
		wallsize=0.9
		
		percentwater=.006
		lakesize=0.7
		
		percenttrees=.009
		forestsize=0.62

		gens = 3
		
		'''
		# cramped rooms, medium forests, smaller more frequent ponds
		percentwalls=.42
		percentwalls += 0.04 * sqrt(scalemod)
		wallsize=0.86
		
		percentwater=.02
		lakesize=0.20
		
		percenttrees=.01
		forestsize=0.60

		gens = 4
		'''

		'''
		# huge rooms, decent forests, big ponds
		percentwalls=.33
		percentwalls += 0.04 * sqrt(scalemod)
		wallsize=0.85
		
		percentwater=.5
		lakesize=0.60
		
		percenttrees=.007
		forestsize=0.62

		gens = 3
		'''

		# walls
		for i in range(1, self.width-1):
			for j in range(1, self.height-1):
				newmap.settile(tuple([i, j]), ground)
				if ((j == self.height / 2 and
					 random.random() < percentwalls * 1.5) or
					random.random() < percentwalls):
					newmap.settile(tuple([i, j]), wall)

		for g in range(gens):
			oldmap = newmap.copy()
			for i in range(1, self.width-1):
				for j in range(1, self.height-1):
					point = tuple([i, j])
					adjwalls = oldmap.adjacenttile(point, wall)
					if (adjwalls >= 4 and
						random.random() < wallsize):
						newmap.settile(point, wall)
					else:
						newmap.settile(point, ground)

		# water
		for i in range(1, self.width-1):
			for j in range(1, self.height-1):
				if (random.random() < percentwater and
					newmap.tilename(i, j) == wall.name):
					newmap.settile(tuple([i, j]), water)

		for g in range(gens):
			oldmap = newmap.copy()
			for i in range(1, self.width-1):
				for j in range(1, self.height-1):
					point = tuple([i, j])
					adjwater = oldmap.adjacenttile(point, water)
					if (adjwater > 0 and
						random.random() < lakesize and
						not oldmap.tilename(i, j) == ground.name):
						newmap.settile(point, water)

		# trees
		for i in range(1, self.width-1):
			for j in range(1, self.height-1):
				if (random.random() < percenttrees and
					newmap.tilename(i, j) == ground.name):
					newmap.settile(tuple([i, j]), tree)

		for g in range(gens):
			oldmap = newmap.copy()
			for i in range(1, self.width-1):
				for j in range(1, self.height-1):
					point = tuple([i, j])
					adjtree = oldmap.adjacenttile(point, tree) + \
						oldmap.adjacenttile(point, water)
					if (adjtree > 0 and
						random.random() < forestsize and
						oldmap.tilename(i, j) == ground.name):
						newmap.settile(point, tree)

		return newmap