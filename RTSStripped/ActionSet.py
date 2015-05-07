class ActionSet:
	ACTIONS			= ['N', 'S', 'E', 'I']
	REWARDS_LEGAL	= {'N': -10, 'S': -10, 'E': -10, 'I': -2}
	REWARDS_ILLEGAL	= {'N': -10, 'S': -10, 'E': -10, 'I': -2}

	def __init__(self):
		pass



	def getDistancePenalty(self, state):
		if (state.unitPos[1] >= (state.NUM_COLS - 2)):
			## unit has passed enemy already, no penalty
			return 0

		dcol = abs(state.unitPos[1] - state.enemyPos[1])
		drow = abs(state.unitPos[0] - state.enemyPos[0])

		if (drow + dcol == 0): return -5 * 10
		if (drow + dcol == 1): return -3 * 10
		if (drow + dcol == 2): return -1 * 10
		return 0

	## return the reward for a
	## primitive (leaf) action
	def getReward(self, state, action):
		penalty = self.getDistancePenalty(state)

		if (self.isLegal(state, action)):
			return (ActionSet.REWARDS_LEGAL[action] + penalty, True)
		else:
			return (ActionSet.REWARDS_ILLEGAL[action] + penalty, False)


	def isLegal(self, state, action):
		row = state.unitPos[0]
		col = state.unitPos[1]
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
