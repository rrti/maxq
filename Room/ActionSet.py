class ActionSet:
	ACTIONS			= ['N', 'S', 'E']
	REWARDS_LEGAL	= {'N': -1, 'S': -1, 'E': -1}
	REWARDS_ILLEGAL	= {'N': -1, 'S': -1, 'E': -1}

	def __init__(self):
		pass


	## return the reward for a primitive (leaf) action
	def getReward(self, state, action):
		if (self.isLegal(state, action)):
			return (ActionSet.REWARDS_LEGAL[action], True)
		else:
			return (ActionSet.REWARDS_ILLEGAL[action], False)

	def isLegal(self, state, action):
		row = state.pos[0]
		col = state.pos[1]
		rowMax = state.NUM_ROWS
		colMax = state.NUM_COLS

		if (action == 'N' or action == 'S'):
			## vertical moves (North/South)
			bool1 = (action == 'N' and row >          0)
			bool2 = (action == 'S' and row < rowMax - 1)
			bool3 = False

			if (bool1 or bool2):
				bool3 = state.isWallInWay(action)

			return ((bool1 and not bool3) or (bool2 and not bool3))

		if (action == 'E'):
			## horizontal moves (East only)
			bool1 = (col < colMax - 1)
			bool2 = False

			if (bool1):
				bool2 = state.isWallInWay(action)

			return (bool1 and not bool2)
