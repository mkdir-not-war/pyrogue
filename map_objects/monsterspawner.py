import json
from random import choices, choice
# choices([list of choices], [list of probability for each choice])

from map_objects.biome import biomes
from data.colors import colors
from render_functions import RenderOrder

from components.attack import Attack, attacktype
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

percent_bottomlevel_spawn = 0.05
percent_lowerlevel_spawn = 0.2
percent_currentlevel_spawn = 0.6
percent_higherlevel_spawn = 0.12
percent_toplevel_spawn = 0.03

max_monster_level = 8

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
		avglevelonfloor = min(int(floor / 5), max_monster_level)
		levelspectrum = {
			max(avglevelonfloor-1, 0) : percent_bottomlevel_spawn, 
			max(avglevelonfloor-1, 0) : percent_lowerlevel_spawn, 
			avglevelonfloor : percent_currentlevel_spawn, 
			min(avglevelonfloor+1, max_monster_level) : percent_higherlevel_spawn,
			min(avglevelonfloor+1, max_monster_level) : percent_toplevel_spawn
		}
		levels = list(levelspectrum.keys())
		levelprobs = [levelspectrum[l] for l in levels]
		monsterlevel = str(choices(levels, levelprobs)[0])

		# get the monster's data
		species = self.monsterdata.get(speciesname)
		thismonsterdata = species.get(str(monsterlevel))
		fov_radius = thismonsterdata.get("fov_radius")
		attentiveness = thismonsterdata.get("attentiveness")
		truesight = (thismonsterdata.get("truesight") == "True")
		hp = thismonsterdata.get("hp")
		defense = thismonsterdata.get("defense")
		spdefense = thismonsterdata.get("spdefense")
		attack = thismonsterdata.get("attack")
		spattack = thismonsterdata.get("spattack")
		speed = thismonsterdata.get("speed")
		name = thismonsterdata.get("name")
		prey = thismonsterdata.get("prey")
		swim = (thismonsterdata.get("swim") == "True")
		char = species.get("char")
		color = colors.get(self.monsterdata.get("colors").get(monsterlevel))

		# create the monster
		attacks = []
		for atkparams in thismonsterdata.get("attacks").values():
			newatk = Attack(
				name=atkparams.get('name'),
				atk_power=int(atkparams.get('atk_power')),
				min_range=int(atkparams.get('min_range')),
				max_range=int(atkparams.get('max_range')),
				atk_type=attacktype(atkparams.get('atk_type')))
			attacks.append(newatk)

		fighter_component = Fighter(
			hp=hp, 
			defense=defense, 
			spdefense=spdefense, 
			attack=attack, 
			spattack=spattack, 
			speed=speed,
			attacks=attacks)
		ai_component = BasicMonster(game_map, 
			prey=prey, 
			swim=swim, 
			truesight=truesight, 
			fov_radius=fov_radius,
			attentiveness=attentiveness)
		monster = Entity(pos[0], pos[1], 
			char, 
			color, 
			name, 
			blocks=True,
			render_order=RenderOrder.ACTOR,
			fighter=fighter_component, 
			ai=ai_component)
		return monster