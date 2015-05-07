import random

class State:
	NUM_ROWS = 7
	NUM_COLS = 7

	## wall-format is (start-row, start-col, length, direction)
	## where start-row and start-col are the top-left corner of
	## cell at (row, col)
	WALLS = [(0, 0,  NUM_COLS, 'H'), (0, 0,  NUM_ROWS, 'V'), (NUM_ROWS, 0,  NUM_COLS, 'H'), (0, NUM_COLS,  NUM_ROWS, 'V')]
	WALLS += [(0, 5,  1, 'V'), (2, 5,  4, 'V')]

	UNIT_START_POSITION_ROWS = [4, 5]
	UNIT_START_POSITION_COLS = [0, 1, 2]
	ENEMY_START_POSITION_ROWS = range(NUM_ROWS)
	ENEMY_START_POSITION_COLS = [4]
	ENEMY_START_DIRECTIONS = [0, 1]

	## uncomment these to effectively disable randomize
	## UNIT_START_POSITION_ROWS = [4]
	## UNIT_START_POSITION_COLS = [0]
	## ENEMY_START_DIRECTIONS = [0]
	## ENEMY_START_POSITION_ROWS = [0]

	## coordinate-format is (row, col), both are zero-based
	## note: exits are between cols 4 and 5, not *on* col 5
	COORS = {"ExitN": [1, 5], "ExitS": [6, 5], "Goal": [0, 6]}


	def __init__(self, unitPos = [0, 0], enemyPos = [0, 0, 0]):
		self.unitPos = unitPos
		self.enemyPos = enemyPos
	def __repr__(self):
		return ("%s-%s" % (self.unitPos, self.enemyPos))

	def tick(self):
		## move the enemy one cell
		if (self.enemyPos[0] ==                  0): self.enemyPos[2] =  1
		if (self.enemyPos[0] == State.NUM_ROWS - 1): self.enemyPos[2] = -1
		self.enemyPos[0] += self.enemyPos[2]

	def clone(self):
		return State([self.unitPos[0], self.unitPos[1]], [self.enemyPos[0], self.enemyPos[1], self.enemyPos[2]])

	def reset(self):
		self.unitPos[0] = 0
		self.unitPos[1] = 0
		self.enemyPos[0] = 0
		self.enemyPos[1] = 0
		self.enemyPos[2] = 1

	def copy(self, other):
		self.unitPos[0] = other.unitPos[0]
		self.unitPos[1] = other.unitPos[1]
		self.enemyPos[0] = other.enemyPos[0]
		self.enemyPos[1] = other.enemyPos[1]
		self.enemyPos[2] = other.enemyPos[2]

	def randomize(self):
		"""
		self.unitPos[0] = random.choice(State.UNIT_START_POSITION_ROWS)
		self.unitPos[1] = random.choice(State.UNIT_START_POSITION_COLS)
		self.enemyPos[0] = random.choice(State.ENEMY_START_POSITION_ROWS)
		self.enemyPos[1] = random.choice(State.ENEMY_START_POSITION_COLS)
		self.enemyPos[2] = random.choice(State.ENEMY_START_DIRECTIONS)
		"""
		self.reset()

	def isWallInWay(self, action):
		row = self.unitPos[0]
		col = self.unitPos[1]

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
		if (action == 'N'): self.unitPos[0] -= 1
		if (action == 'S'): self.unitPos[0] += 1
		if (action == 'E'): self.unitPos[1] += 1


	def printMe(self):
		s = ''

		for row in xrange(State.NUM_ROWS):
			h1 = ''
			h2 = ''

			for col in xrange(State.NUM_COLS):
				hwall1 = self.getWallType(row, col, 'H')
				vwall = self.getWallType(row, col, 'V')
				cell = self.getCellChar(row, col)
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


	def getWallType(self, row, col, direc):
		s = ''

		for wall in State.WALLS:
			if (direc == 'V'):
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
			if (direc == 'V'):
				return '| '
			else:
				return '---'

		return s


	def getCellChar(self, row, col):
		if (State.COORS["ExitN"][0] == row and State.COORS["ExitN"][1] == col): return 'N '
		elif (State.COORS["ExitS"][0] == row and State.COORS["ExitS"][1] == col): return 'S '
		elif (State.COORS["Goal"][0] == row and State.COORS["Goal"][1] == col): return 'G '
		elif (self.unitPos[0] == row and self.unitPos[1] == col): return 'U '
		elif (self.enemyPos[0] == row and self.enemyPos[1] == col): return 'E '
		else: return '  '
