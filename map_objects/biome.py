import json

class Biome:
	def __init__(self, name):
		self.name = name
		self.map_params = {}

	def load_map_params(self):
		with open('data/biomes.txt') as json_file:
			data = json.load(json_file)
			self.map_params = data[self.name]