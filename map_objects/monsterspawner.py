import json
from random import choices
# choices([list of choices], [list of probability for each choice])

from biome import biomes

from components.fighter import Fighter
from components.ai import BasicMonster, astar
from entity import Entity

class MonsterSpawner():
	def __init(self):
		self.monsterdata = {}
		self.loadmonsterdata()

	def loadmonsterdata(self):
		pass

	def getmonsters(biomename, nummonsters):
		pass