import random

class State:
	NUM_ROWS = 5
	NUM_COLS = 7
	WALLS = [(0, 0, NUM_COLS, 'H'), (0, 0, NUM_ROWS, 'V'), (NUM_ROWS, 0, NUM_COLS, 'H'), (0, NUM_COLS, NUM_ROWS, 'V')]
	COORS = {'R': [0, 1], 'G': [1, 0], 'B': [3, 0], 'Y': [4, 1], 'Z': [2, 6]}


	def __init__(self, unit1Loc = 'R', unit2Loc = 'G', transPos = [2, 0], enemyPos = [1, 3, 1]):
		self.unit1Loc = unit1Loc
		self.unit2Loc = unit2Loc
		self.transPos = transPos
		self.enemyPos = enemyPos

	def __repr__(self):
		return (self.unit1Loc + self.unit2Loc + str(self.transPos) + str(self.enemyPos))

	def tick(self):
		if (self.enemyPos[0] ==                  0): self.enemyPos[2] = 1
		if (self.enemyPos[0] == State.NUM_ROWS - 1): self.enemyPos[2] = -1
		self.enemyPos[0] += self.enemyPos[2]
		return

	def clone(self):
		return State(self.unit1Loc, self.unit2Loc, [self.transPos[0], self.transPos[1]], [self.enemyPos[0], self.enemyPos[1], self.enemyPos[2]])

	def randomize(self):
		"""
		self.unit1Loc = random.choice(State.COORS.keys())
		self.unit2Loc = random.choice(State.COORS.keys())
		self.transPos = [2, 0]
		self.enemyPos = [random.randint(0, State.NUM_ROWS - 1), 3, random.choice([-1, 1])]

		while ((self.unit1Loc == self.unit2Loc) or (self.unit1Loc == 'Z' or self.unit2Loc == 'Z')):
			## never allow two units to be spawned in same cell
			self.unit1Loc = random.choice(State.COORS.keys())
			self.unit2Loc = random.choice(State.COORS.keys())
		"""
		self.reset()

	def reset(self):
		self.unit1Loc = 'R'
		self.unit2Loc = 'G'
		self.transPos[0] = 2
		self.transPos[1] = 0
		self.enemyPos[0] = 1
		self.enemyPos[1] = 3
		self.enemyPos[2] = 1

	def copy(self, other):
		self.unit1Loc = other.unit1Loc
		self.unit2Loc = other.unit2Loc
		self.transPos[0] = other.transPos[0]
		self.transPos[1] = other.transPos[1]
		self.enemyPos[0] = other.enemyPos[0]
		self.enemyPos[1] = other.enemyPos[1]
		self.enemyPos[2] = other.enemyPos[2]


	def isWallInWay(self, action):
		row = self.transPos[0]
		col = self.transPos[1]

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
						bool1 = (wall[1] == col     and action == 'W')
						bool2 = (wall[1] == col + 1 and action == 'E')
						if (bool1 or bool2): return True
			return False


	## execute an action
	def doAction(self, action):
		if (action == 'N'): self.transPos[0] -= 1
		if (action == 'S'): self.transPos[0] += 1
		if (action == 'W'): self.transPos[1] -= 1
		if (action == 'E'): self.transPos[1] += 1

		if (action == 'G'):
			## prevent key errors that aren't filtered by isLegal()
			bool1 = (self.unit1Loc != 'T' and self.unit1Loc != 'Z')
			bool2 = (self.unit2Loc != 'T' and self.unit2Loc != 'Z')
			if (bool1 and self.transPos == State.COORS[self.unit1Loc]): self.unit1Loc = 'T'
			if (bool2 and self.transPos == State.COORS[self.unit2Loc]): self.unit2Loc = 'T'
		if (action == 'P'):
			if (self.unit1Loc == 'T'): self.unit1Loc = 'Z'
			if (self.unit2Loc == 'T'): self.unit2Loc = 'Z'

		if (action == 'I'): return
