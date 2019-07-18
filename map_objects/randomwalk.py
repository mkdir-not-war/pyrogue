height = 40
width = 45

fromdirdict = {
	(1, 0) : 0,
	(-1, 0) : 2,
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
			mapdict[current][3 - fromdirection] = True # set exit to
			current = tupleadd(current, newdir)		
		else:
			fromdirection = None
			current = midpoint
	return mapdict

def printmap(mapdict):
	print("MAP: ")
	for y in range(height):
		row = ['.' if (x, y) in mapdict.keys() else '#' for x in range(width)]
		print(''.join(row))
	print()

def main():
	while(1):
		length = int(input('length: '))
		mapdict = randomwalk(length)
		printmap(mapdict)

if __name__=='__main__':
	main()