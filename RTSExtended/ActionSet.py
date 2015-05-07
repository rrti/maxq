class ActionSet:
	ACTIONS			= ['N', 'S', 'W', 'E',   'G', 'P', 'I']
	REWARDS_LEGAL	= {'N': -1, 'S': -1, 'W': -1, 'E': -1,   'G': -1, 'P': 20, 'I': -2}
	REWARDS_ILLEGAL	= {'N': -1, 'S': -1, 'W': -1, 'E': -1,   'G': -10, 'P': -10, 'I': -2}

	def __init__(self):
		pass


	## auxiliary function for getReward()
	def getEnemyDist(self, state):
		dx = state.transPos[1] - state.enemyPos[1]
		dy = state.transPos[0] - state.enemyPos[0]
		return (dx * dx + dy * dy)

	## return reward for a primitive (leaf-node) action
	## which partially depends on distance to the enemy
	def getReward(self, state, action):
		distSq = self.getEnemyDist(state)

		if (distSq > 2):
			penalty = 0
		else:
			penalty = -10 / (distSq + 1)
			penalty = 0 ## DBG

		if (self.isLegal(state, action)):
			reward = ActionSet.REWARDS_LEGAL[action]
			if (state.unit1Loc == 'T' and state.unit2Loc == 'T'):
				reward *= 2
			return (reward + penalty, True)
		else:
			return ((ActionSet.REWARDS_ILLEGAL[action] + penalty, False))


	def isLegal(self, state, action):
		row = state.transPos[0]
		col = state.transPos[1]
		rowMax = state.NUM_ROWS
		colMax = state.NUM_COLS

		if (action == 'I'): return True

		if (action == 'N' or action == 'S'):
			## vertical moves (North/South)
			bool1 = (action == 'N' and row >          0)
			bool2 = (action == 'S' and row < rowMax - 1)
			bool3 = False

			if (bool1 or bool2):
				bool3 = state.isWallInWay(action)

			return ((bool1 and not bool3) or (bool2 and not bool3))

		if (action == 'W' or action == 'E'):
			## horizontal moves (East/West)
			bool1 = (action == 'E' and col < colMax - 1)
			bool2 = (action == 'W' and col >          0)
			bool3 = False

			if (bool1 or bool2):
				bool3 = state.isWallInWay(action)

			return ((bool1 and not bool3) or (bool2 and not bool3))

		if (action == 'G' or action == 'P'):
			if (action == 'G'):
				## units may not be in transport or already at dropzone
				bool1 = (state.unit1Loc != 'T' and state.unit1Loc != 'Z')
				bool2 = (state.unit2Loc != 'T' and state.unit2Loc != 'Z')
				bool3 = (bool1 and state.transPos == state.COORS[state.unit1Loc])
				bool4 = (bool2 and state.transPos == state.COORS[state.unit2Loc])
			if (action == 'P'):
				bool3 = (state.unit1Loc == 'T' and state.transPos == state.COORS['Z'])
				bool4 = (state.unit2Loc == 'T' and state.transPos == state.COORS['Z'])

			return (bool3 or bool4)
