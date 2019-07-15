import json

class Biome:
	def __init__(self, name):
		self.name = name
		self.params = {}
		self.load_map_params()

	def load_map_params(self):
		with open('data/biomes.txt') as json_file:
			data = json.load(json_file)
			self.params = data[self.name]

# TODO: why not continue to use one big dict instead of a bunch of objects?
biomes = {
	'MEDROOM_MEDFOREST_SMLWATER' : Biome('MEDROOM_MEDFOREST_SMLWATER'),
	'SMLROOM_MEDFOREST_MEDWATER' : Biome('SMLROOM_MEDFOREST_MEDWATER'),
	'LRGROOM_LRGFOREST_LRGWATER' : Biome('LRGROOM_LRGFOREST_LRGWATER')
}