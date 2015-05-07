import random

class ActionSelector:
	def __init__(self, epsilon, beta, actionSet):
		self.epsilon = epsilon
		self.initEpsilon = epsilon
		self.beta = beta
		self.actionSet = actionSet
		self.epsilonMin = 0.00001

	"""
	## return a tuple containing the highest
	## action-value given a state s and the
	## corresponding action
	def getActionValMaxTuple(self, state, QObj):
		actionMax = self.actionSet.ACTIONS[0]
		actionValMax = QObj.getQValue(state, actionMax)

		for action in self.actionSet.ACTIONS[1:]:
			actionVal = QObj.getQValue(state, action)

			if (actionVal > actionValMax):
				actionValMax = actionVal
				actionMax = action

		return (actionMax, actionValMax)

	def select(self, state, QObj):
		if (random.random() > self.epsilon):
			## exploit, choose action that has best
			## Q(s, a) value of possible actions <a>
			maxActionValTuple = self.getActionValMaxTuple(state, QObj)
			maxAction = maxActionValTuple[0]
			return maxAction
		else:
			## explore, choose random action
			return random.choice(self.actionSet.ACTIONS)
	"""

	def getReward(self, state, action):
		return self.actionSet.getReward(state, action)

	def decayEpsilon(self):
		if (self.epsilon > self.epsilonMin):
			self.epsilon *= self.beta
	
	def resetEpsilon(self):
		self.epsilon = self.initEpsilon
