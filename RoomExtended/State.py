import random

class State:
	NUM_ROWS = 7
	NUM_COLS = 6
	WALLS = [(0, 0,  NUM_COLS, 'H'), (0, 0,  NUM_ROWS, 'V'), (NUM_ROWS, 0,  NUM_COLS, 'H'), (0, NUM_COLS,  NUM_ROWS, 'V')]
	WALLS += [(0, 4,  1, 'V'), (2, 4,  3, 'V'), (6, 4,  1, 'V')]
	## NOTE: exits are really between cols 3 and 4, not *on* col 4
	COORS = {'N': [1, 4], 'S': [5, 4], 'G': [0, 5]}


	def __init__(self, pos = [4, 2]): self.pos = pos
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

		self.pos = [row, col]
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
						bool1 = (wall[1] == col     and action == 'W')
						bool2 = (wall[1] == col + 1 and action == 'E')
						if (bool1 or bool2): return True
			return False

	## execute an action
	def doAction(self, action):
		if (action == 'N'): self.pos[0] -= 1
		if (action == 'S'): self.pos[0] += 1
		if (action == 'E'): self.pos[1] += 1
		if (action == 'W'): self.pos[1] -= 1
