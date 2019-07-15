from random import randint, random
import components.ai as AI
from game_messages import Message
import tcod as libtcod
from components.attack import Attack, default_attack, AttackType

class Fighter:
	def __init__(self, hp=1, 
		defense=1, spdefense=1, 
		attack=1, spattack=1, 
		speed=1, 
		attacks=None):

		self.max_hp = hp
		self.hp = hp
		self.defense = defense
		self.spdefense = spdefense
		self.attack = attack
		self.spattack = spattack
		self.speed = speed
		
		if (attacks is None):
			attacks = [default_attack]
		self.attacks = attacks[:]

	def take_damage(self, amount):
		results = []

		self.hp -= amount

		if self.hp <= 0:
			results.append({'dead': self.owner})

		return results

	def attacktarget(self, target, attack):
		results = []

		# determine if it's even a hit, otherwise, damage is zero.
		lowlevel_equalizer = 2
		speed_calc = float(self.speed + lowlevel_equalizer) / \
			float(target.fighter.speed + lowlevel_equalizer)
		dodge_chance = speed_calc-0.5
		dodged = False
		critical = False
		if (dodge_chance >= 1.0):
			dodged = True
		elif (dodge_chance <= 0.0):
			dodged = False
			critical = True
		else:
			dodged = (random() >= dodge_chance)

		damage = 0
		if (not dodged):
			# pokemon damage calc
			dmg_mod = (random() * 0.15) + 0.85 # [0.85,1.0)
			if (critical):
				dmg_mod *= 1.5
			effective_atkdef = 0
			assert(attack.atk_type == AttackType.PHYSICAL or
				attack.atk_type == AttackType.SPECIAL)
			if (attack.atk_type == AttackType.PHYSICAL):
				effective_atkdef = float(
					self.attack) / float(target.fighter.defense)
			elif (attack.atk_type == AttackType.SPECIAL):
				effective_atkdef = float(
					self.spattack) / float(target.fighter.spdefense)
			damage = int(
				float(attack.atk_power) * effective_atkdef * dmg_mod * 0.5) + 1

		# if AI attacks non-hostile AI, fight back!
		if (not target.ai is None):
			if ((target.ai.aistate != AI.AIStates.FOLLOWING) or 
				(target.ai.targetentity != self.owner)):
				target.ai.aistate = AI.AIStates.FOLLOWING
				target.ai.targetentity = self.owner

		if damage > 0:
			if (critical):
				results.append({'message': Message(
					'%s uses its %s attack on the %s for %s hit points. It\'s a critical hit!' % \
					(self.owner.name, attack.name, target.name, str(damage)),
					libtcod.white)})
			else:
				results.append({'message': Message(
					'%s uses its %s attack on the %s for %s hit points.' % \
					(self.owner.name, attack.name, target.name, str(damage)),
					libtcod.white)})
			results.extend(target.fighter.take_damage(damage))
		elif (dodged):
			results.append({'message': Message(
				'%s uses its %s attack, but the %s completely dodges it.' % \
				(self.owner.name, attack.name, target.name),
				libtcod.white)})
		else:
			results.append({'message': Message(
				'%s uses its %s attack on the %s, but does no damage.' % \
				(self.owner.name, attack.name, target.name),
				libtcod.white)})

		return results