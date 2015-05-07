## TERMINAL PREDICATES
def isMaxRootTerminal(state, param):
	return (state.pos == state.COORS["G"])

def isMaxExitTerminal(state, param):
	return (state.pos[1] >= state.NUM_COLS - 2)

def isMaxGotoGoalTerminal(state, param):
	return (state.pos == state.COORS["G"] or not isMaxExitTerminal(state, param))

def isMaxNavTerminal(state, param):
	return (state.pos == state.COORS[param])

def isPrimitiveTerminal(state, param):
	return False

## BINDING TRANSLATION PREDICATES
def navBindTransFunc(state, param):
	return param



class Graph:
	def __init__(self, Nodes, alpha, delta, useSSA):
		## MNode(name, ID, alpha, delta, ssaMPredicate, terminalPredicate, bindings, bindingPredicate, usePseudoRewards, action = ' ')
		self.mRoot		= Nodes.MNode("MRoot",		0, alpha, delta, None, isMaxRootTerminal, [],			None,				False)
		self.mExit		= Nodes.MNode("MExit",		1, alpha, delta, None, isMaxExitTerminal, ["N", "S"],	None,				False)
		self.mGotoGoal	= Nodes.MNode("MGotoGoal",	2, alpha, delta, None, isMaxGotoGoalTerminal, ["G"],	None,				False)
		self.mNav		= Nodes.MNode("MNav",		6, alpha, delta, None, isMaxNavTerminal, [],			navBindTransFunc,	False)
		self.mNorth		= Nodes.MNode("MNorth",		3, alpha, delta, None, isPrimitiveTerminal, [],			None,				False, 'N')
		self.mSouth		= Nodes.MNode("MSouth",		4, alpha, delta, None, isPrimitiveTerminal, [],			None,				False, 'S')
		self.mEast		= Nodes.MNode("MEast",		5, alpha, delta, None, isPrimitiveTerminal, [],			None,				False, 'E')

		## QNode(name, ssaQPredicate, maxNode = None)
		self.qExit		= Nodes.QNode("QExit",      None, self.mExit)
		self.qGotoGoal	= Nodes.QNode("QGotoGoal",  None, self.mGotoGoal)
		self.qNavExit	= Nodes.QNode("QNavExit", 	None, self.mNav)
		self.qNavGoal	= Nodes.QNode("QNavGoal", 	None, self.mNav)
		self.qNorth		= Nodes.QNode("QNorthG",  	None, self.mNorth)
		self.qSouth		= Nodes.QNode("QSouthG",  	None, self.mSouth)
		self.qEast		= Nodes.QNode("QEastG",   	None, self.mEast)

		## set the QNode-children of each MNode
		self.mRoot.setQChildren([self.qExit, self.qGotoGoal])
		self.mExit.setQChildren([self.qNavExit])
		self.mGotoGoal.setQChildren([self.qNavGoal])
		self.mNav.setQChildren([self.qNorth, self.qSouth, self.qEast])



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
