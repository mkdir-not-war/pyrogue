import json
from random import choices
# choices([list of choices], [list of probability for each choice])

from biome import biomes
from data.colors import colors

from components.fighter import Fighter
from components.ai import BasicMonster
from entity import Entity

class MonsterSpawner():
	def __init(self):
		self.monsterdata = {}
		self.loadmonsterdata()

	def loadmonsterdata(self):
		pass

	def getmonster(self, pos, biomename, floor):
		pass