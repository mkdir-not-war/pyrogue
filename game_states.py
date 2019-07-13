from enum import Enum 

class GameState(Enum):
	PLAYERS_TURN = 1
	ENEMY_TURN = 2
	OPEN_DOOR = 3