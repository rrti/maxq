import random

class State:
	NUM_ROWS = 7
	NUM_COLS = 6
	WALLS = [(0, 0,  NUM_COLS, 'H'), (0, 0,  NUM_ROWS, 'V'), (NUM_ROWS, 0,  NUM_COLS, 'H'), (0, NUM_COLS,  NUM_ROWS, 'V')]
	WALLS += [(0, 4,  1, 'V'), (2, 4,  3, 'V'), (6, 4,  1, 'V')]
	## NOTE: exits are really between cols 3 and 4, not *on* col 4
	COORS = {'N': [1, 4], 'S': [5, 4], 'G': [0, 5]}


	## set default start-pos to [4, 2] for consistency with Dietterich scenario
	def __init__(self, pos = [4, 2]):
		self.pos = pos
	def __repr__(self): return str(self.pos)
	def tick(self): return
	def clone(self): return State([self.pos[0], self.pos[1]])
	def reset(self):
		self.pos[0] = 4
		self.pos[1] = 2
	def copy(self, other):
		self.pos[0] = other.pos[0]
		self.pos[1] = other.pos[1]

	def randomize(self):
		"""
		row = 0; col = 0

		while (row == col):
			## always start in left room
			row = random.choice(range(0, State.NUM_ROWS    ))
			col = random.choice(range(0, State.NUM_COLS - 2))

		self.pos[0] = row
		self.pos[1] = col
		"""
		self.reset()


	def isWallInWay(self, action):
		row = self.pos[0]
		col = self.pos[1]

		if (action == 'N' or action == 'S'):
			for wall in State.WALLS:
				if (wall[3] == 'H'):
					if (col >= wall[1] and col < (wall[1] + wall[2])):
						bool1 = (wall[0] == row     and action == 'N')
						bool2 = (wall[0] == row + 1 and action == 'S')
						if (bool1 or bool2): return True
			return False

		else:
			for wall in State.WALLS:
				if (wall[3] == 'V'):
					if (row >= wall[0] and row < (wall[0] + wall[2])):
						bool = (wall[1] == col + 1 and action == 'E')
						if (bool): return True
			return False


	## execute an action
	def doAction(self, action):
		if (action == 'N'): self.pos[0] -= 1
		if (action == 'S'): self.pos[0] += 1
		if (action == 'E'): self.pos[1] += 1

	def printMe(self):
		s = ''

		for row in xrange(State.NUM_ROWS):
			h1 = ''
			h2 = ''

			for col in xrange(State.NUM_COLS):
				hwall1 = self.getWallType(row, col, 'H')
				vwall = self.getWallType(row, col, 'V')
				cell = self.getCell(row, col)
				h1 += ('+' + hwall1)
				h2 += (vwall + cell)

			h1 += '+\n'
			h2 += self.getWallType(row, State.NUM_COLS, 'V') + '\n'
			s += h1 + h2

		h = ''
		hwall1 = self.getWallType(State.NUM_ROWS, State.NUM_COLS - 1, 'H')

		for col in xrange(State.NUM_COLS):
			h += '+' + hwall1

		s += h + '+\n'
		print("%s" % s)

	def getWallType(self, row, col, dir):
		s = ''

		for wall in State.WALLS:
			if (dir == 'V'):
				if (wall[3] == 'V'):
					if (row >= wall[0] and row < (wall[0] + wall[2])):
						if (col == wall[1]):
							s = '# '
			else:
				if (wall[3] == 'H'):
					if (col >= wall[1] and col < (wall[1] + wall[2])):
						if (row == wall[0]):
							s = '==='
		if (s == ''):
			if (dir == 'V'):
				return '| '
			else:
				return '---'
		return s

	def getCell(self, row, col):
		if (State.COORS['N'][0] == row and State.COORS['N'][1] == col): return 'N '
		elif (State.COORS['S'][0] == row and State.COORS['S'][1] == col): return 'S '
		elif (State.COORS['G'][0] == row and State.COORS['G'][1] == col): return 'G '
		elif (self.pos[0] == row and self.pos[1] == col): return 'T '
		else: return '  '
