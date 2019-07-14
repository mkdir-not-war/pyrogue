from random import randint, random
import components.ai as AI
from game_messages import Message
import tcod as libtcod

class Fighter:
	def __init__(self, hp, defense, power):
		self.max_hp = hp
		self.hp = hp
		self.defense = defense
		self.power = power

	def take_damage(self, amount):
		results = []

		self.hp -= amount

		if self.hp <= 0:
			results.append({'dead': self.owner})

		return results

	def attack(self, target):
		results = []

		damage = self.power - target.fighter.defense

		# if AI attacks non-hostile AI, fight back!
		if (not target.ai is None):
			if ((target.ai.aistate != AI.AIStates.FOLLOWING) or 
				(target.ai.targetentity != self.owner)):
				target.ai.aistate = AI.AIStates.FOLLOWING
				target.ai.targetentity = self.owner

		if damage > 0:
			results.append({'message': Message(
				'%s attacks the %s for %s hit points.' % \
				(self.owner.name.capitalize(), target.name, str(damage)),
				libtcod.white)})
			results.extend(target.fighter.take_damage(damage))
		else:
			results.append({'message': Message(
				'%s attacks the %s but does no damage.' % \
				(self.owner.name.capitalize(), target.name),
				libtcod.white)})

		return results