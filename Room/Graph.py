def isTerminalMRoot(g, state, param):
	return (state.pos == state.COORS['G'], True)

def isTerminalMExit(g, s, p):
	if (s.pos == s.COORS['N'] or s.pos == s.COORS['S']):
		return (True, True)
	else:
		return (False, True)

def isTerminalMGotoGoal(g, s, p):
	b1 = (s.pos == s.COORS['G'])
	b2 = (g.getMNode("MExit")).hasTerminated
	return ((b1 or not b2), True)

def isTerminalMPrim(g, s, p):
	return (False, True)



"""
def isMaxRootTerminal(g, state, param):
	return (isMaxExitTerminal(g, state, param)[0] and isMaxGotoGoalTerminal(g, state, param)[0], True)

def isMaxExitTerminal(g, state, param):
	return ((state.pos[1] >= state.NUM_COLS - 2), True)

def isMaxGotoGoalTerminal(g, state, param):
	## if MExit is not yet terminal, we may not pick MGotoGoal from root in SNT()
	return (not isMaxExitTerminal(g, state, param)[0] or state.pos == state.COORS["Goal"], True)

def isPrimitiveTerminal(g, state, param):
	return (False, True)
"""



class Graph:
	def __init__(self, Nodes, alpha, delta, useSSA):
		## QNode(name, ssaQPredicate)
		self.qExit		= Nodes.QNode("QExit",      None)
		self.qGotoGoal	= Nodes.QNode("QGotoGoal",  None)

		self.qExitNorth	= Nodes.QNode("QExitNorth", None)
		self.qExitSouth	= Nodes.QNode("QExitSouth", None)
		self.qExitEast	= Nodes.QNode("QExitEast",  None)
		self.qNorthG	= Nodes.QNode("QNorthG",    None)
		self.qSouthG	= Nodes.QNode("QSouthG",    None)
		self.qEastG		= Nodes.QNode("QEastG",     None)

		## MNode(name, ID, alpha, delta, ssaMPredicate, terminalPredicate, termOnce, bindings, bindingPredicate, usePseudoRewards, action = ' ')
		self.mRoot		= Nodes.MNode(self, "MRoot",		0, alpha, delta, None, isTerminalMRoot,		True,  [], None, False)
		self.mExit		= Nodes.MNode(self, "MExit",		1, alpha, delta, None, isTerminalMExit,		True,  [], None, True)
		self.mGotoGoal	= Nodes.MNode(self, "MGotoGoal",	2, alpha, delta, None, isTerminalMGotoGoal,	False, [], None, False)
		self.mNorth		= Nodes.MNode(self, "MNorth",		3, alpha, delta, None, isTerminalMPrim,		False, [], None, False, 'N')
		self.mSouth		= Nodes.MNode(self, "MSouth",		4, alpha, delta, None, isTerminalMPrim,		False, [], None, False, 'S')
		self.mEast		= Nodes.MNode(self, "MEast",		5, alpha, delta, None, isTerminalMPrim,		False, [], None, False, 'E')


		## set the MNode-children of each QNode
		self.qExit.setMChild(self.mExit)
		self.qGotoGoal.setMChild(self.mGotoGoal)

		self.qExitNorth.setMChild(self.mNorth)
		self.qExitSouth.setMChild(self.mSouth)
		self.qExitEast.setMChild(self.mEast)
		self.qNorthG.setMChild(self.mNorth)
		self.qSouthG.setMChild(self.mSouth)
		self.qEastG.setMChild(self.mEast)


		## set the QNode-children of each MNode
		self.mRoot.setQChildren([self.qExit, self.qGotoGoal])
		self.mExit.setQChildren([self.qExitNorth, self.qExitSouth, self.qExitEast])
		self.mGotoGoal.setQChildren([self.qNorthG, self.qSouthG, self.qEastG])

		self.MNodesLst = [self.mRoot, self.mExit]
		self.MNodesMap = {
			"MRoot": self.mRoot, "MExit": self.mExit, "MGotoGoal": self.mGotoGoal,
			"MNorth": self.mNorth, "MSouth": self.mSouth, "MEast": self.mEast}

	def getMNode(self, name):
		return self.MNodesMap[name]


	def reset(self, verbose, batchReset):
		self.resetRec(self.mRoot, verbose, batchReset)

	def resetRec(self, node, verbose, batchReset):
		node.printMe(verbose)
		node.reset(batchReset)

		if (node.isPrimitive()):
			return
		else:
			for child in node.getChildren():
				self.resetRec(child, verbose, batchReset)

	def getRoot(self):
		return self.mRoot
