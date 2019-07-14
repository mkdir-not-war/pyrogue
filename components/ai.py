from operator import itemgetter
from numpy import dot
import tcod as libtcod
from fov_functions import recompute_fov, initialize_fov
from enum import Enum
from random import choice
import entity as entityfuncs

fov_algorithm = libtcod.FOV_SHADOW
fov_light_walls = True

possible_moves = [(0, 1), (1, 0), (-1, 0), (0, -1)]

class AIStates(Enum):
	IDLE = 1
	FOLLOWING = 2
	SEARCHING = 3

class BasicMonster:
	def __init__(self, game_map, 
		attentiveness=4, fov_radius=7, prey=['Player-test']):
		self.aistate = AIStates.IDLE
		self.statefuncs = {
			AIStates.IDLE: self.take_turn_idle,
			AIStates.FOLLOWING: self.take_turn_follow,
			AIStates.SEARCHING: self.take_turn_search
		}

		self.targetentity = None # create ecosystem so player isn't only target
		self.prey = prey[:]

		self.turnssincetargetseen = -1
		self.lastknownpos = None
		self.attentiveness = attentiveness
		self.path = False

		self.fov_map = initialize_fov(game_map)
		self.fov_radius = fov_radius
		self.fov_recompute = False

	def take_turn(self, game_map, entities):
		monster = self.owner

		# recalculate field of vision
		if self.fov_recompute:
			recompute_fov(self.fov_map, monster.x, monster.y, self.fov_radius, 
				fov_light_walls, fov_algorithm)

		# call function based on state
		func = self.statefuncs[self.aistate]
		func(game_map, entities)

	def take_turn_idle(self, game_map, entities):
		monster = self.owner

		# is there any idle pathing??
		# walks around aimlessly until it sees an entity that it considers prey
		for entity in entities:
			if entity.name in self.prey:
				if libtcod.map_is_in_fov(self.fov_map, entity.x, entity.y):
					pass
		else:
			# 50% chance to move aimlessly, otherwise stand still
			if (choice([True, False]) == True):
				move = choice(possible_moves)
				dest_x, dest_y = (monster.x + move[0], monster.y + move[1])
				if (not game_map.tileblocked(dest_x, dest_y) and
					not entityfuncs.get_blocking_entities_at_location(
						entities, dest_x, dest_y)):
					monster.move(move[0], move[1])


	def take_turn_follow(self, game_map, entities):
		monster = self.owner

	def take_turn_search(self, game_map, entities):
		monster = self.owner


def manhattandist(a, b):
	result = abs(a[0] - b[0]) + abs(a[1] - b[1])
	return result

def h(start, goal):
	return manhattandist(start, goal)

def tupleequal(x, y):
	return x[0] == y[0] and x[1] == y[1]

def squaredlen(vec):
	result = 0
	for d in vec:
		result += d ** 2
	return result

def vectorsbyclosestangle(target, vecs):
	square_cos = {}
	sqlen_target = squaredlen(target)
	for v in vecs:
		dotprod = dot(v, target)
		value = (dotprod * dotprod) / (squaredlen(v) * sqlen_target)
		square_cos[v] = value
	return max(square_cos.items(), key=itemgetter(1))

def neighbors(p, worldmap, travonly=True, buffer=1):
	x = p[0]
	y = p[1]
	result = []
	if (x - 1 >= buffer):
		if (not travonly or not worldmap.tileblocked(x-1, y)):
			result.append(tuple([x-1, y]))
	if (x + 1 < worldmap.width - buffer):
		if (not travonly or not worldmap.tileblocked(x+1, y)):
			result.append(tuple([x+1, y]))
	if (y - 1 >= buffer):
		if (not travonly or not worldmap.tileblocked(x, y-1)):
			result.append(tuple([x, y-1]))
	if (y + 1 < worldmap.height - buffer):
		if (not travonly or not worldmap.tileblocked(x, y+1)):
			result.append(tuple([x, y+1]))
	return result

def reconstruct_path(cameFrom, current):
	totalpath = [] # don't include current position
	while current in cameFrom:
		current = cameFrom[current]
		totalpath.insert(0, current)
	return totalpath

def astar(start, goal, worldmap, travonly=True, costs=True):
	closedset = []
	openset = [start]
	camefrom = {}
	gScore = {}
	gScore[start] = 0
	fScore = {}
	fScore[start] = h(start, goal)

	while openset:
		currenti = 0
		for p in range(len(openset)):
			if (openset[p] in fScore):
				if (fScore[openset[p]] < currenti):
					currenti = p
		if tupleequal(openset[currenti], goal):
			return reconstruct_path(camefrom, openset[currenti])
		current = openset[currenti]
		openset = openset[:currenti] + openset[currenti+1:]
		closedset.append(current)

		for n in neighbors(current, worldmap, travonly=travonly):
			if n in closedset:
				continue
			if n not in gScore:
				gScore[n] = worldmap.size * 10
			if (costs):
				t_gScore = gScore[current] + worldmap.getcost(*n)
			else:
				t_gScore = gScore[current] + 1
			if n not in openset:
				openset.append(n)
			elif t_gScore >= gScore[n]:
				continue
			camefrom[n] = current
			gScore[n] = t_gScore
			fScore[n] = t_gScore + h(n, goal)
	return False