import random
from entity import Entity
from math import sqrt
from map_objects.game_map import GameMap

SMALL_FLOOR = 4 * 1
MEDIUM_FLOOR = 4 * 4
LARGE_FLOOR = 4 * 9

class GameWorld:
	def __init__(self, roomwidth, roomheight):
		self.roomwidth = roomwidth
		self.roomheight = roomheight
		self.current_floor = 0
		self.current_room = (0, 0)
		self.currmap = None
		self.floor_rooms = []
		self.next_floor_rooms = []

	def loadfirstfloor(self, player, entities):
		self.generatefloorrooms(SMALL_FLOOR)
		self.loadnextfloor(player, entities)

	def loadnextfloor(self, player, entities):
		self.current_floor += 1
		# wait for next_floor_rooms to finish generating, if it's not done yet
		self.floor_rooms = self.next_floor_rooms[:]
		self.current_room = (0, 0)
		self.currmap = self.floor_rooms[0]
		self.next_floor_rooms = []
		self.currmap.enter(player, entities)
		self.currmap.spawnplayer(player, entities)
		# set boss lair entrance in same room as player
		# kick off generation of next next floor in new thread

	def floorwidth(self, floor):
		return int(sqrt(len(floor)))

	# fill tiles and exits in size # of gamemaps in floor list of gamemaps
	def generatefloorrooms(self, size):
		floor = []
		for roomnum in range(size):
			floor.append(GameMap(self.roomwidth, self.roomheight))
		width = int(sqrt(size))
		height = width # floors are a square of rooms, width = height
		for y in range(height):
			for x in range(width):
				# pick a biome
				biomename = 'MEDROOM_MEDFOREST_SMLWATER'

				topexit = False
				if (x==0):
					topexit = True
				elif (y%2==0):
					topexit = True
				elif (x>y):
					topexit = True
				if (y==height-1):
					topexit = False

				botexit = False
				if (x==0 and y>0):
					botexit = True
				elif (y%2==1):
					botexit = True
				elif (x>0 and y>0 and x>=y):
					botexit = True

				rightexit = False
				if (y==0):
					rightexit = True
				elif (x%2==0):
					rightexit = True
				elif (y>x):
					rightexit = True
				if (x==width-1):
					rightexit = False

				leftexit = False
				if (y==0 and x>0):
					leftexit = True
				elif (x%2==1):
					leftexit = True
				elif (x>0 and y>0 and y>=x):
					leftexit = True

				floor[x + width * y].generate(biomename,
					top=topexit, bottom=botexit, right=rightexit, left=leftexit)
		self.next_floor_rooms = floor[:]

	def movetonextroom(self, player, entities, exitdir):
		entrancedir = None
		roomvec = None
		if (exitdir == 'north'):
			entrancedir = 'south'
			roomvec = (0, -1)
		elif (exitdir == 'south'):
			entrancedir = 'north'
			roomvec = (0, 1)
		elif (exitdir == 'west'):
			entrancedir = 'east'
			roomvec = (-1, 0)
		elif (exitdir == 'east'):
			entrancedir = 'west'
			roomvec = (1, 0)
		# assume that you're not going out of bounds
		nextroomx = self.current_room[0] + roomvec[0]
		nextroomy = self.current_room[1] + roomvec[1]
		nextroom = self.floor_rooms[nextroomx + \
			self.floorwidth(self.floor_rooms) * nextroomy]
		nextroom.enter(player, entities, entrancedir)
		self.current_room = (nextroomx, nextroomy)
		self.currmap = nextroom	