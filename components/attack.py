from enum import Enum

class AttackType(Enum):
	PHYSICAL = 1
	SPECIAL = 2

def attacktype(typename):
	if (typename == 'physical'):
		return AttackType.PHYSICAL
	elif (typename == 'special'):
		return AttackType.SPECIAL

class Attack():
	def __init__(self, name, atk_power, atk_type, max_range, min_range):
		self.name = name
		assert(atk_power > 0)
		self.atk_power = atk_power
		assert(max_range > 0)
		assert(min_range > 0)
		self.max_range = max_range
		self.min_range = min_range
		self.atk_type = atk_type

default_attack = Attack("Punch", 1, AttackType.PHYSICAL, 1, 1)
