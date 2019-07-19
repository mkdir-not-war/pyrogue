import random
from entity import Entity
from math import sqrt
from map_objects.game_map import GameMap
from map_objects.monsterspawner import MonsterSpawner
from map_objects.biome import biomes

FLOOR_HEIGHT = 8
FLOOR_WIDTH = 16
AVG_DIST = int((FLOOR_WIDTH + FLOOR_HEIGHT) / 2)


SMALL_FLOOR = 8 # avg 5 rooms, path=3
MEDIUM_FLOOR = 20 # avg 12 rooms, path=6
LARGE_FLOOR = 50 # avg 22 rooms, path=12
HUGE_FLOOR = 80 # avg 32 rooms, path=12
LABYRINTHINE_FLOOR = 150 # avg 40 rooms, path=12

FLOOR_TIERS = {
	0 : SMALL_FLOOR,
	5: MEDIUM_FLOOR,
	20: LARGE_FLOOR,
	35: HUGE_FLOOR,
	50: LABYRINTHINE_FLOOR
}

def getfloortier(floor):
	floortier = 0
	for tier in FLOOR_TIERS:
		if floor >= tier and tier > floortier:
			floortier = tier
	return FLOOR_TIERS.get(floortier)

FROM_DIR = {
	(1, 0) : 2,
	(-1, 0) : 0,
	(0, 1) : 1,
	(0, -1) : 3,
	'north' : 3,
	'south' : 1,
	'west' : 2,
	'east' : 0
}

MIN_PATH_LENGTH = 3
MIDPOINT = (int(FLOOR_WIDTH/2), int(FLOOR_HEIGHT/2))

def tupleadd(t1, t2):
	result = (t1[0]+t2[0], t1[1]+t2[1])
	return result

def inbounds(width, height, newpos):
	result = (
		newpos[0] >= 0 and
		newpos[0] < width and
		newpos[1] >= 0 and
		newpos[1] < height)
	return result

class GameWorld:
	def __init__(self, roomwidth, roomheight):
		self.roomwidth = roomwidth
		self.roomheight = roomheight
		self.current_floor = 0
		self.current_room = (0, 0)
		self.currmap = None
		self.floors_rooms = []
		self.floor_rooms = {}
		self.next_floor_rooms = {}
		self.monsterspawner = MonsterSpawner()

	def loadfirstfloor(self, player, entities):
		self.generatenextfloorrooms(self.current_floor+1)
		self.loadnextfloor(player, entities)

	# assumes you can only go down, never back up
	def loadnextfloor(self, player, entities, startroom=None):
		if (currmap.islair):
			pass
		else:
		self.current_floor += 1
		# wait for next_floor_rooms to finish generating, if it's not done yet
		self.floor_rooms = self.next_floor_rooms.copy()
		self.current_room = MIDPOINT
		self.currmap = self.floor_rooms.get(self.current_room)
		self.next_floor_rooms = {}
		self.currmap.enter(player, entities, self.monsterspawner)
		self.currmap.spawnplayer(player, entities)
		# kick off generation of next next floor in new thread

	def getnextmapdown(self, floor, islair):
		if islair:
			pass
		else:
			pass


	def floorwidth(self, floor):
		return int(sqrt(len(floor)))

	# random walk
	def generatenextfloorrooms(self, floor):
		walklength = getfloortier(floor)
		mapdict = {}
		# right, up, left, down
		possiblevecs = [(0, 1), (1, 0), (-1, 0), (0, -1)]
		fromdirection = None # 0=left, 1=down, 2=right, 3=up
		current = MIDPOINT
		biomename = random.choice(list(biomes.keys()))
		for i in range(walklength):
			if (current in mapdict and fromdirection != None):
				mapdict[current][fromdirection] = True # set exit from
			elif (not current in mapdict):
				mapdict[current] = [False, False, False, False, biomename]
				if (fromdirection != None):
					mapdict[current][fromdirection] = True # set exit from
			if (i % min(max(MIN_PATH_LENGTH, walklength/3), AVG_DIST) != 0):
				newdir = random.choice(possiblevecs)
				while (not inbounds(
					FLOOR_WIDTH, FLOOR_HEIGHT, tupleadd(current, newdir))):
					newdir = random.choice(possiblevecs)
				fromdirection = FROM_DIR[newdir]
				if (i < walklength-1):
					mapdict[current][(fromdirection+2)%4] = True # set exit to
				current = tupleadd(current, newdir)		
			else:
				biomename = random.choice(list(biomes.keys()))
				fromdirection = None
				current = MIDPOINT

		# Pick a room for the lair that isn't the start room
		lairroom = random.choice(list(mapdict.keys()))
		while (lairroom == MIDPOINT):
			lairroom = random.choice(list(mapdict.keys()))

		for room in mapdict.keys():
			haslair =  (room == lairroom)
			self.next_floor_rooms[room] = GameMap(
				self.roomwidth, self.roomheight, floor)
			room_data = mapdict[room]
			self.next_floor_rooms[room].generate(
					room_data[4],
					stairsdown=haslair,
					top=room_data[FROM_DIR['north']],
					bottom=room_data[FROM_DIR['south']],
					right=room_data[FROM_DIR['east']],
					left=room_data[FROM_DIR['west']],
				)

	def movetonextroom(self, player, entities, exitdir):
		entrancedir = None
		roomvec = None
		if (exitdir == 'north'):
			entrancedir = 'south'
			roomvec = (0, 1)
		elif (exitdir == 'south'):
			entrancedir = 'north'
			roomvec = (0, -1)
		elif (exitdir == 'west'):
			entrancedir = 'east'
			roomvec = (-1, 0)
		elif (exitdir == 'east'):
			entrancedir = 'west'
			roomvec = (1, 0)

		elif (exitdir == 'up'):
			entrancedir = 'down'
		elif (exitdir == 'down'):
			entrancedir = 'up'

		# assume that you're not going out of bounds
		if (not roomvec is None):
			nextroomx, nextroomy = tupleadd(self.current_room, roomvec)
			nextroom = self.floor_rooms.get((nextroomx, nextroomy))
			nextroom.enter(
				player, entities, 
				self.monsterspawner, entrancedir=entrancedir)
			self.current_room = (nextroomx, nextroomy)
			self.currmap = nextroom	
		else:
			# moving between floor and lair