import random
from math import sqrt
import tcod as libtcod

from components.door import Door
from components.stairs import Stairs
from components.fighter import Fighter
from components.ai import BasicMonster, astar

from entity import Entity
from map_objects.tile import Tile
from map_objects.biome import biomes

wall = Tile('wall', True)
ground = Tile('ground', False)
water = Tile('water', True, False, cost=6)
tree = Tile('tree', False, True, cost=3)

min_monsters_per_room = 0
max_monsters_per_room = 10

lair_radius = 9

class GameMap:
	def __init__(self, width, height, floor, islair=False):
		self.width = width
		self.height = height
		self.size = width * height
		self.floor = floor
		self.tiles = self.initialize_tiles() # set in generate

		# set exits in generate
		self.exits = {}
		self.exits['north'] = None
		self.exits['south'] = None
		self.exits['west'] = None
		self.exits['east'] = None
		self.exits['up'] = None
		self.exits['down'] = None

		# tuple lair position if this map holds the lair
		self.islair = islair
		self.stairs = {}
		self.stairs['up'] = None
		self.stairs['down'] = None

		# includes corpses as well as live monsters
		self.monsters = None

		self.items = None

		self.biomename = None
		self.costmap = [] # set in generate
		self.exploredmap = [] # set in generate

	def initialize_tiles(self):
		tiles = [wall] * self.size
		return tiles

	def clearentities(self):
		self.monsters = None
		self.items = None

	def tileblocked(self, x, y):
		if (not self.inbounds(x, y) or 
			self.tiles[x + self.width * y].blocked):
			return True
		return False

	def tilename(self, x, y):
		return self.tiles[x + self.width * y].name

	def copy(self):
		newmap = GameMap(self.width, self.height, self.floor)
		for i in range(self.size):
			newmap.tiles[i] = self.tiles[i]
		newmap.exits = self.exits.copy()
		newmap.stairs = self.stairs.copy()
		newmap.exploredmap = self.exploredmap[:]
		newmap.islair = self.islair
		newmap.costmap = self.costmap[:]
		return newmap

	def getcostmap(self):
		result = [self.tiles[i].cost for i in range(self.size)]
		return result

	def getcost(self, x, y, wallszero=True, canswim=False):
		result = self.costmap[x + self.width * y]
		if (not wallszero):
			if (result == 0):
				# walls are finite but super big cost
				result = self.size
		if (not canswim):
			if (result == water.cost):
				result = self.size
		return result

	def settile(self, point, tile):
		self.tiles[point[1] * self.width + point[0]] = tile

	def getgroundtiles(self):
		result = self.gettilesbytype('ground')
		return result

	def gettilesbytype(self, *tilenames):
		result = []
		for i in range(self.width):
			for j in range(self.height):
				point = tuple([i, j])
				if (self.tilename(*point) in tilenames):
					result.append(point)
		# order: top to bottom -> left to right
		return result

	def generate(self, 
		biomename, 
		stairsdown=False,
		top=False, bottom=False, left=False, right=False):

		self.biomename = biomename
		self.tiles = self.cellularautomata().tiles
		self.costmap = self.getcostmap()
		self.exploredmap = [False] * self.size
		self.setexits(top=top, bottom=bottom, left=left, right=right)
		self.setstairs(False, stairsdown)
		self.costmap = self.getcostmap()

	def generatelair(self):
		self.tiles = self.lairtiles().tiles
		self.costmap = self.getcostmap()
		self.exploredmap = [False] * self.size
		self.setstairs(True, True)
		self.costmap = self.getcostmap()

	# clear entity list of previous room's entities, 
	# fill with this room's entities
	def enter(self, 
		player, entities, 
		monsterspawner, 
		entrancedir=None, 
		fromlowerfloor=False,
		bossalive=True):

		entities.clear()
		entities.append(player)

		# spawn monsters when first enter a room (only sets self.monsters)
		if (self.monsters is None):
			self.spawnmonsters(
				entities, monsterspawner, bossalive=bossalive)

		# spawn items
		if (self.items is None):
			self.items = [] ##############################

		# place stairs, doors, enemies and items into entities list
		entities.extend(self.spawnexits())
		livemonsters = [1 for monster in self.monsters if monster.char != '%']
		if (not self.stairs['down'] is None and len(livemonsters) == 0):
			entities.extend(self.spawnstairsdown())
		if (not self.stairs['up'] is None):
			entities.extend(self.spawnstairsup())
		entities.extend(self.monsters)
		entities.extend(self.items)

		if (entrancedir):
			player.x, player.y = self.exits[entrancedir]
		elif (fromlowerfloor):
			player.x, player.y = self.stairs['down']

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
		if (not self.stairs['up'] is None):
			# already been to this floor
			player.x, player.y = self.stairs['up']
			return

		candidatetiles = self.gettilesbytype('ground', 'tree')
		assert(len(candidatetiles) > 0)

		pos = random.choice(candidatetiles)

		while(True):
			# if no exit possible to reach, find new spot
			if (not self.check_can_reach_exit(pos)):
				pos = random.choice(candidatetiles)
				continue
			# if spot already has something on it, find new spot
			if (any([entity for entity in entities 
				if entity.x == pos[0] and entity.y == pos[1]])):
				pos = random.choice(candidatetiles)
				continue
			# otherwise, the spot is good for spawning
			break

		# hole dropped player here, therefore, the way back up is here
		if (self.floor > 1):
			self.stairs['up'] = pos
			self.settile(pos, ground)
		player.x, player.y = pos

	def spawnmonsters(self, entities, spawner, bossalive=True):
		self.monsters = []

		if (self.islair and bossalive):
			roomcenter = (int(self.width / 2), int(self.height / 2))
			monster = spawner.getbossmonster(self, roomcenter)
			self.monsters.append(monster)
		else:
			nummonsters = random.randint(min_monsters_per_room,
				int(max_monsters_per_room / 2)) + \
				random.randint(0, int(max_monsters_per_room / 2))
			#nummonsters = 0 ############################################
			groundtiles = []
			if (nummonsters > 0):
				groundtiles = [tile for tile in \
					self.getgroundtiles() if \
					self.adjacenttile(tile, ground) >= 4 and \
					self.inbounds(tile[0], tile[1], buffer=4)]
			else:
				return

			for i in range(nummonsters):
				pos = random.choice(groundtiles)

				if not any([entity for entity in entities 
					if entity.x == pos[0] and entity.y == pos[1]]):
					monster = spawner.getbasicmonster(self, pos)
					self.monsters.append(monster)

	def check_can_reach_exit(self, pos):
		for e in self.exits.values():
			path = False
			if (not e is None):
				path = astar(pos, e, self, travonly=True, buffer=0)
			if path:
				return True
		return False

	# must first have generated tiles and set exits
	# if lair, set in specific positons
	def setstairs(self, up, down):
		if (down == True):
			if (self.islair):
				pos = (int(self.width / 2), 
					int(self.height / 2) - lair_radius)
				self.stairs['down'] = pos
				self.settile(pos, ground)
			else:
				# assume no swimming
				tiles = self.gettilesbytype('ground', 'tree') 
				
				# make sure all adjacent tiles are traversable
				tiles = [t for t in tiles 
					if (self.adjacenttile(t, ground) + \
						self.adjacenttile(t, tree)) >= 8]

				# make sure no stairs overlapping doors
				pos = random.choice(tiles)
				while(1):
					for e in self.exits.values():
						if e == pos:
							pos = random.choice(tiles)
							continue
					break

				# stairs down into a lair are actually an exit/door
				self.exits['down'] = pos
				self.settile(pos, ground)

				# make sure stairs are reachable
				roomcenter = (int(self.width / 2), int(self.height / 2))
				path = astar(
					pos, roomcenter, self, travonly=False, 
					costs=True, buffer=0)
				for tile in path:
					# only change walls (assumes player can swim)
					if (self.tilename(tile[0], tile[1]) == 'wall'):
						self.settile(tile, ground)
					# change water too (if player can't swim)
					if (self.tilename(tile[0], tile[1]) == 'water'):
						self.settile(tile, tree)

		if (up == True):
			if (self.islair):
				pos = (int(self.width / 2), 
					int(self.height / 2) + lair_radius)
				# stairs up in a lair are actually an exit/door
				self.exits['up'] = pos
				self.settile(pos, ground)

	def spawnstairsup(self):
		result = []
		if (not self.stairs['up'] is None):
			stairs_comp = Stairs()

			# doesn't block because you have to use rope to go back up
			stairs_up = Entity(
				self.stairs['up'][0], self.stairs['up'][1], 
				'*', libtcod.white, 
				'Light filtering from above', blocks=False, 
				stairs=stairs_comp)
			result.append(stairs_up)
		return result

	# only spawn stairs down in lair once boss is dead
	def spawnstairsdown(self):
		result = []
		if (not self.stairs['down'] is None):
			stairs_comp = Stairs()

			stairs_down = Entity(
				self.stairs['down'][0], self.stairs['down'][1], 
				'X', libtcod.white, 
				'Deep hole', blocks=True, 
				stairs=stairs_comp)
			result.append(stairs_down)
		return result

	def spawnexits(self):
		result = []
		for exit in self.exits:
			pos = self.exits[exit]

			name = 'Door'
			if (exit == 'up'):
				name = 'Lair Exit'
			elif (exit == 'down'):
				name = 'Lair Entrance'

			if (pos != None):
				if (self.tileblocked(pos[0], pos[1])):
					self.settile(pos, ground)
				door = Entity(pos[0], pos[1], 
					'>', libtcod.white, 
					name, blocks=True, door=Door(exit))
				result.append(door)
		return result

	def setexits(self, top=False, left=False, right=False, bottom=False):
		newexits = []

		if top:
			xpos = random.choice(range(self.width))
			mapexit = (xpos, 0)
			self.exits['north'] = mapexit
			newexits.append(mapexit)	  
		if left:
			ypos = random.choice(range(self.height))
			mapexit = (0, ypos)
			self.exits['west'] = mapexit
			newexits.append(mapexit)
		if right:
			ypos = random.choice(range(self.height))
			mapexit = (self.width-1, ypos)
			self.exits['east'] = mapexit
			newexits.append(mapexit)
		if bottom:
			xpos = random.choice(range(self.width))
			mapexit = (xpos, self.height-1)
			self.exits['south'] = mapexit
			newexits.append(mapexit)

		# find path (through walls!) from each exit to another exit, 
		# make each tile along the path ground if it's a wall
		roomcenter = (int(self.width / 2), int(self.height / 2))
		centertile = self.tilename(*roomcenter)
		if (centertile == 'wall' or centertile == 'water'):
			self.settile(roomcenter, ground)
		for e in newexits:
			path = astar(
				e, roomcenter, self, travonly=False, costs=True, buffer=0)
			for pos in path:
				# only change walls (assumes player can swim)
				if (self.tilename(pos[0], pos[1]) == 'wall'):
					self.settile(pos, ground)
				# change water too (if player can't swim)
				if (self.tilename(pos[0], pos[1]) == 'water'):
					self.settile(pos, tree)

	def lairtiles(self):
		newmap = GameMap(self.width, self.height, self.floor)
		roomcenter = (int(self.width / 2), int(self.height / 2))
		for i in range(1, self.width-1):
			for j in range(1, self.height-1):
				newmap.settile(tuple([i, j]), wall)
				if (((roomcenter[0]-i)**2 + \
					(roomcenter[1]-j)**2) < \
					(lair_radius**2)):
					newmap.settile(tuple([i, j]), ground)
		return newmap

	def cellularautomata(self):
		newmap = GameMap(self.width, self.height, self.floor)

		scalemod = self.size / 8000 

		biome = biomes.get(self.biomename)

		percentwalls = biome.params['percentwalls']
		wallscalemod = biome.params['wallscalemod']
		percentwalls += wallscalemod * sqrt(scalemod)
		wallsize = biome.params['wallsize']
		
		percentwater = biome.params['percentwater']
		lakesize = biome.params['lakesize']
		
		percenttrees = biome.params['percenttrees']
		forestsize = biome.params['forestsize']

		gens = biome.params['gens']

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