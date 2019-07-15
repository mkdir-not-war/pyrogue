import json
from random import choices, choice
# choices([list of choices], [list of probability for each choice])

from map_objects.biome import biomes
from data.colors import colors
from render_functions import RenderOrder

from components.fighter import Fighter
from components.ai import BasicMonster
from entity import Entity

'''
NOTES:
Nethack has ~50 primary levels, then endless levels after that(??) in which 
monsters stop scaling in power. This game currently has 4 sizes of floors,
so maybe 40 floors is a good goal (no need to overstay welcome) for 
the primary floors, the size of floors increasing at floors 5, 15 and 25.
Should have probably around 9 levels of monsters per species -- one for 
every 5 floors and an extra for the floors past the primary.

'''

percent_lowerlevel_spawn = 0.2
percent_currentlevel_spawn = 0.7
percent_higherlevel_spawn = 0.1

class MonsterSpawner():
	def __init__(self):
		self.monsterdata = {}
		self.loadmonsterdata()

	def loadmonsterdata(self):
		with open('data/monsters.txt') as json_file:
			data = json.load(json_file)
			self.monsterdata = data.copy()

		# split prey by comma
		for speciesname in self.monsterdata:
			species = self.monsterdata.get(speciesname)
			for level in range(10):
				if (str(level) in species):
					preystr = species.get(str(level)).get('prey')
					preylist = preystr.split(',')
					self.monsterdata.get(
						speciesname).get(
						str(level))['prey'] = preylist

		# assign color by level (also index a species by level)
		self.monsterdata['colors'] = {
			'0' : 'monster_color_0',
			'1' : 'monster_color_0',
			'2' : 'monster_color_1',
			'3' : 'monster_color_1',
			'4' : 'monster_color_2',
			'5' : 'monster_color_2',
			'6' : 'monster_color_2',
			'7' : 'monster_color_3',
			'8' : 'monster_color_3',
			'9' : 'monster_color_3'
		}

	def getbasicmonster(self, game_map, pos):
		# map variables
		floor = game_map.floor
		biomename = game_map.biomename

		# pick a species
		speciesdict = biomes.get(biomename).params.get("monsterspecies")
		speciesoptions = list(speciesdict.keys())
		speciesindex = choice(speciesoptions)
		speciesname = speciesdict.get(speciesindex)

		# pick a level
		avglevelonfloor = min(int(floor / 5), 8)
		levelspectrum = {
			max(avglevelonfloor-1, 0) : percent_lowerlevel_spawn, 
			avglevelonfloor : percent_currentlevel_spawn, 
			avglevelonfloor+1 : percent_higherlevel_spawn
		}
		levels = list(levelspectrum.keys())
		levelprobs = [levelspectrum[l] for l in levels]
		monsterlevel = str(choices(levels, levelprobs)[0])

		# get the monster's data
		species = self.monsterdata.get(speciesname)
		thismonsterdata = species.get(str(monsterlevel))
		hp = thismonsterdata.get("hp")
		defense = thismonsterdata.get("defense")
		power = thismonsterdata.get("power")
		name = thismonsterdata.get("name")
		prey = thismonsterdata.get("prey")
		char = species.get("char")
		color = colors.get(self.monsterdata.get("colors").get(monsterlevel))

		# create the monster
		fighter_component = Fighter(hp=hp, defense=defense, power=power)
		ai_component = BasicMonster(game_map, prey=prey)
		monster = Entity(pos[0], pos[1], 
			char, 
			color, 
			name, 
			blocks=True,
			render_order=RenderOrder.ACTOR,
			fighter=fighter_component, 
			ai=ai_component)
		return monster