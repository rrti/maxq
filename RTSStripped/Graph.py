def isMaxRootTerminal(state, param):
	return (isMaxPassEnemyTerminal(state, param) and isMaxGotoGoalTerminal(state, param))

def isMaxPassEnemyTerminal(state, param):
	return (state.unitPos[1] >= (state.NUM_COLS - 2))

def isMaxGotoGoalTerminal(state, param):
	## if isMaxPassEnemyTerminal is not yet terminal, we may not pick MGotoGoal from root in SNT()
	return (not isMaxPassEnemyTerminal(state, param) or state.unitPos == state.COORS["Goal"])

def isPrimitiveTerminal(state, param):
	return False

## TODO: state abstraction funcs as in RTSDefault
## (doesn't matter where enemy is for MGotoGoal)
def ssaQGotoGoal(i, s, j): return str(s.unitPos)

class Graph:
	def __init__(self, Nodes, alpha, delta, useSSA = False):
		## QNode(name, ssaQPredicate)
		if (useSSA):
			self.qGotoGoal		= Nodes.QNode("QGotoGoal", ssaQGotoGoal)
		else:
			self.qGotoGoal		= Nodes.QNode("QGotoGoal", None)

		self.qPassEnemy			= Nodes.QNode("QPassEnemy",      None)
		self.qPassEnemyNorth	= Nodes.QNode("QPassEnemyNorth", None)
		self.qPassEnemySouth	= Nodes.QNode("QPassEnemySouth", None)
		self.qPassEnemyEast		= Nodes.QNode("QPassEnemyEast",  None)
		self.qPassEnemyIdle		= Nodes.QNode("QPassEnemyIdle",  None)
		self.qGotoGoalNorth		= Nodes.QNode("QGotoGoalNorth",  None)
		self.qGotoGoalEast		= Nodes.QNode("QGotoGoalEast",   None)
		self.qGotoGoalSouth		= Nodes.QNode("QGotoGoalSouth",  None)

		## MNode(name, ID, alpha, delta, ssaMPredicate, terminalPredicate, bindings, bindTranslateFunc, usePseudoRewards, action = ' '):
		self.mRoot		= Nodes.MNode("MRoot",		0, alpha, delta, None, isMaxRootTerminal,		[], None, False)
		self.mPassEnemy	= Nodes.MNode("MPassEnemy",	1, alpha, delta, None, isMaxPassEnemyTerminal,	[], None, True)
		self.mGotoGoal	= Nodes.MNode("MGotoGoal",	2, alpha, delta, None, isMaxGotoGoalTerminal,	[], None, False)
		self.mNorth		= Nodes.MNode("MNorth",		3, alpha, delta, None, isPrimitiveTerminal,		[], None, False, 'N')
		self.mSouth		= Nodes.MNode("MSouth",		4, alpha, delta, None, isPrimitiveTerminal,		[], None, False, 'S')
		self.mEast		= Nodes.MNode("MEast",		5, alpha, delta, None, isPrimitiveTerminal,		[], None, False, 'E')
		self.mIdle		= Nodes.MNode("MIdle",		6, alpha, delta, None, isPrimitiveTerminal,		[], None, False, 'I')


		## set the MNode-children of each QNode
		self.qPassEnemy.setMChild(self.mPassEnemy)
		self.qGotoGoal.setMChild(self.mGotoGoal)

		self.qPassEnemyNorth.setMChild(self.mNorth)
		self.qPassEnemySouth.setMChild(self.mSouth)
		self.qPassEnemyEast.setMChild(self.mEast)
		self.qPassEnemyIdle.setMChild(self.mIdle)
		self.qGotoGoalNorth.setMChild(self.mNorth)
		self.qGotoGoalEast.setMChild(self.mEast)
		self.qGotoGoalSouth.setMChild(self.mSouth)


		## set the QNode-children of each MNode
		self.mRoot.setQChildren([self.qPassEnemy, self.qGotoGoal])
		self.mPassEnemy.setQChildren([self.qPassEnemyNorth, self.qPassEnemySouth, self.qPassEnemyEast, self.qPassEnemyIdle])
		self.mGotoGoal.setQChildren([self.qGotoGoalNorth, self.qGotoGoalEast, self.qGotoGoalSouth])



	def reset(self, verbose):
		self.resetRec(self.mRoot, verbose)

	def resetRec(self, node, verbose):
		node.printMe(verbose)
		node.reset()

		if (node.isPrimitive()):
			return
		else:
			for child in node.getChildren():
				self.resetRec(child, verbose)

	def getRoot(self):
		return self.mRoot
