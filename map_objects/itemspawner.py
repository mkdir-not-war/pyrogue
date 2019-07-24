import json
from random import choices, choice
# choices([list of choices], [list of probability for each choice])

from map_objects.biome import biomes
from data.colors import colors
from render_functions import RenderOrder

from entity import Entity
from components.item import Item

class ItemSpawner():
	def __init__(self):
		self.itemdata = {}
		self.loaditemdata()

	def loaditemdata(self):
		with open('data/items.txt') as json_file:
			data = json.load(json_file)
			self.itemdata = data.copy()

		# assign color by level (also index a species by level)
		self.itemdata['colors'] = {
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