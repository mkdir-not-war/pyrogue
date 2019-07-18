height = 10
width = 15

fromdirdict = {
	(1, 0) : 2,
	(-1, 0) : 0,
	(0, 1) : 1,
	(0, -1) : 3
}

from random import choice

def tupleadd(t1, t2):
	result = (t1[0]+t2[0], t1[1]+t2[1])
	return result

def inbounds(newpos):
	result = (
		newpos[0] >= 0 and
		newpos[0] < width and
		newpos[1] >= 0 and
		newpos[1] < height)
	return result

def randomwalk(length):
	mapdict = {}
	midpoint = (int(width/2), int(height/2))
	# right, up, left, down
	possiblevecs = [(0, 1), (1, 0), (-1, 0), (0, -1)]
	fromdirection = None # 0=left, 1=down, 2=right, 3=up
	current = midpoint
	for i in range(length):
		if (current in mapdict and fromdirection != None):
			mapdict[current][fromdirection] = True # set exit from
		else:
			mapdict[current] = [False, False, False, False]
			if (fromdirection != None):
				mapdict[current][fromdirection] = True # set exit from
		if (i % 100 != 0):
			newdir = choice(possiblevecs)
			while (not inbounds(tupleadd(current, newdir))):
				newdir = choice(possiblevecs)
			fromdirection = fromdirdict[newdir]
			mapdict[current][(fromdirection+2)%4] = True # set exit to
			current = tupleadd(current, newdir)		
		else:
			fromdirection = None
			current = midpoint
	return mapdict

def printmap(mapdict):
	print("MAP: ")
	for y in range(height):
		topexitrow = []
		row = []
		botexitrow = []

		for x in range(width):
			if ((x,y) in mapdict):
				exits = mapdict[(x, y)]
				if (exits[1]):
					topexitrow.append('  ^  ')
				else:
					topexitrow.append('     ')
				if (exits[3]):
					botexitrow.append('  v  ')
				else:
					botexitrow.append('     ')
				if (exits[0]):
					if (exits[2]):
						row.append(' <.> ')
					else:
						row.append('  .> ')
				else:
					if (exits[2]):
						row.append(' <.  ')
					else:
						row.append('  .  ')
			else:
				topexitrow.append('     ')
				row.append('     ')
				botexitrow.append('     ')


		print(''.join(topexitrow))
		print(''.join(row))
		print(''.join(botexitrow))
		print()
	print()

def main():
	while(1):
		length = int(input('length: '))
		mapdict = randomwalk(length)
		printmap(mapdict)

if __name__=='__main__':
	main()