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

	def loadfirstfloor(self, entities):
		self.generatefloorrooms(self.floor_rooms, SMALL_FLOOR)
		self.loadnextfloor(entities)

	def loadnextfloor(self, entities):
		self.current_floor += 1
		# wait for next_floor_rooms to finish generating, if it's not done yet
		self.floor_rooms = self.next_floor_rooms[:]
		self.current_room = (0, 0)
		self.currmap = self.floor_rooms[0]
		self.next_floor_rooms = []
		self.currmap.spawnplayer(entities)
		# set boss lair entrance in same room as player

	def floorwidth(self, floor):
		return int(sqrt(len(floor)))

	# fill tiles and exits in size # of gamemaps in floor list of gamemaps
	def generatefloorrooms(self, floor, size):
		floor = [GameMap(self.roomwidth, self.roomheight)] * size
		width = int(sqrt(size))
		height = width # floors are a square of rooms, width = height
		for y in range(height):
			for x in range(width):
				topexit = (x == 0 or
					y % 2 == 0 or
					(y % 2 == 1 and x > y))
				botexit = ((x == 0 and y > 0) or
					y % 2 == 1 or
					(y % 2 == 0 and x >= y))
				rightexit = (y == 0 or
					x % 2 == 0 or
					(x % 2 == 1 and y > x))
				leftexit = ((y == 0 and x > 0) or
					x % 2 == 1 or
					(x % 2 == 0 and y >= x))
				floor[x + width * y].generate(
					top=topexit, bottom=botexit, right=rightexit, left=leftexit)

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
		self.current_room = (nextroomx, nextroomy)
		nextroom.enter(player, entities, entrancedir)

