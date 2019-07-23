import random
import threading

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
		self.current_floor = -1
		self.current_room = (0, 0)
		self.currmap = None
		self.floors_rooms = [] # all floors
		self.bosses_cleared = []
		self.floor_rooms = {} # current floor's rooms
		self.next_floor_rooms = {}
		self.monsterspawner = MonsterSpawner()

		self.nextfloorgen_thread = None

	def loadfirstfloor(self, player, entities):
		self.nextfloorgen_thread = threading.Thread(
			target=self.generatenextfloorrooms, 
			args=(len(self.floors_rooms), ))
		self.nextfloorgen_thread.start()
		self.movetonextfloor(player, entities)

	def movetonextfloor(self, player, entities):
		if (self.current_floor+1 == len(self.floors_rooms)):
			self.nextfloorgen_thread.join()
			self.floors_rooms.append(self.next_floor_rooms)
			self.bosses_cleared.append(False)

		self.current_floor += 1
		self.floor_rooms = self.next_floor_rooms.copy()
		self.current_room = MIDPOINT
		self.currmap = self.floor_rooms.get(self.current_room)
		self.next_floor_rooms = {}
		self.currmap.enter(player, entities, self.monsterspawner)
		self.currmap.spawnplayer(player, entities)

		self.nextfloorgen_thread = threading.Thread(
			target=self.generatenextfloorrooms, 
			args=(len(self.floors_rooms), ))
		self.nextfloorgen_thread.start()

	def movetopreviousfloor(self, player, entities):
		if (self.current_floor <= 0):
			return

		self.current_floor -= 1
		# we want to reference the floor, not copy it
		self.floor_rooms = self.next_floors_rooms[self.current_floor]
		self.current_room = MIDPOINT
		self.currmap = self.floor_rooms.get(self.current_room)
		self.next_floor_rooms = {}
		self.currmap.enter(player, entities, self.monsterspawner)
		self.currmap.spawnplayer(player, entities)

	# random walk
	def generatenextfloorrooms(self, floor):
		walklength = getfloortier(floor)
		mapdict = {}
		resultfloor = {}
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

		# lair is always the same room as start room on a floor
		room_with_lair = MIDPOINT

		for room in mapdict.keys():
			haslair =  (room == room_with_lair)
			resultfloor[room] = GameMap(
				self.roomwidth, self.roomheight, floor)
			room_data = mapdict[room]
			resultfloor[room].generate(
					room_data[4],
					stairsdown=haslair,
					top=room_data[FROM_DIR['north']],
					bottom=room_data[FROM_DIR['south']],
					right=room_data[FROM_DIR['east']],
					left=room_data[FROM_DIR['west']],
				)
		resultfloor['lair'] = GameMap(
			self.roomwidth, self.roomheight, 0, islair=True)
		resultfloor['lair'].generatelair()

		self.next_floor_rooms = resultfloor.copy()
		

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
				self.monsterspawner, 
				entrancedir=entrancedir)
			self.current_room = (nextroomx, nextroomy)
			self.currmap = nextroom	
		elif exitdir == 'down':
			# moving into lair
			nextroom = self.floor_rooms.get('lair')
			nextroom.enter(
				player, entities,
				self.monsterspawner, 
				entrancedir=entrancedir,
				bossalive=not self.bosses_cleared[self.current_floor])
			self.currmap = nextroom
		elif exitdir == 'up':
			# moving from lair back into floor
			nextroom = self.floor_rooms.get(
				(self.current_room[0], self.current_room[1]))
			nextroom.enter(
				player, entities, 
				self.monsterspawner, 
				entrancedir=entrancedir)
			self.currmap = nextroom	