#########################
## TERMINAL PREDICATES ##
#########################
def isMaxRootTerminal(state, param):
	return (state.unit1Loc == 'Z' and state.unit2Loc == 'Z')

def isMaxGetTerminal(state, param):
	bool = False
	if (param == 1): bool = (state.unit1Loc == 'T' or state.unit1Loc == 'Z')
	if (param == 2): bool = (state.unit2Loc == 'T' or state.unit2Loc == 'Z')
	return bool

def isMaxPutTerminal(state, param):
	return (state.unit1Loc != 'T') and (state.unit2Loc != 'T')

def isMaxNavTerminal(state, param):
	## need to filter out 'T' here because
	## selectNextTask(i, self.ss) fails in
	## MAXQQ otherwise
	if (param == 'T'): return True
	return (state.transPos == state.COORS[param])

def isPrimitiveTerminal(state, param):
	## may not return True or selectNextTask()
	## will always skip over the primitives!
	return False



###################################
## BINDING TRANSLATION PREDICATE ##
###################################
def bMNav(state, param):
	if (param == 1): return state.unit1Loc
	if (param == 2): return state.unit2Loc
	if (param == 'Z'): return 'Z'

	## PROBLEM: SHOULD NOT HAPPEN
	return None



#######################################
## SAFE STATE ABSTRACTION PREDICATES ##
#######################################

## primitives (used for MNodes only)
def ssaI(state): return str(state.transPos) + str(state.enemyPos)
def ssaN(state): return str(state.transPos) + str(state.enemyPos)
def ssaS(state): return str(state.transPos) + str(state.enemyPos)
def ssaW(state): return str(state.transPos) + str(state.enemyPos)
def ssaE(state): return str(state.transPos) + str(state.enemyPos)

def ssaG(state):
	if (state.unit1Loc == 'T'): u1 = 'None'
	else: u1 = state.COORS[state.unit1Loc]
	if (state.unit2Loc == 'T'): u2 = 'None'
	else: u2 = state.COORS[state.unit2Loc]

	tp = state.transPos

	if (u1 == tp or u2 == tp):
		return "LEG" + str(state.unit1Loc) + (state.unit2Loc)
	else:
		return "ILL" + str(state.unit1Loc) + (state.unit2Loc)

def ssaP(state):
	tp = state.transPos

	if (tp == state.COORS['Z'] and (state.unit1Loc == 'T' or state.unit2Loc == 'T')):
		return "LEG" + str(state.unit1Loc) + (state.unit2Loc)
	else:
		return "ILL" + str(state.unit1Loc) + (state.unit2Loc)

## composites (used for QNodes only)
def ssaQGet(i, s, j): return str(s.unit1Loc) + str(s.unit2Loc) + str(j)
def ssaQPut(i, s, j): return str(s.unit1Loc) + str(s.unit2Loc) + str(j)

def ssaQNavForGet(i, s, j): return str(s.unit1Loc) + str(s.unit2Loc)
def ssaQNavForPut(i, s, j): return str(s.unit1Loc) + str(s.unit2Loc)

def ssaQG(i, s, j): return str(s.unit1Loc) + str(s.unit2Loc) + str(s.transPos)
def ssaQP(i, s, j): return str(s.unit1Loc) + str(s.unit2Loc) + str(s.transPos)

def ssaQN(i, s, j): return str(i) + str(s.transPos) + str(s.enemyPos)
def ssaQS(i, s, j): return str(i) + str(s.transPos) + str(s.enemyPos)
def ssaQW(i, s, j): return str(i) + str(s.transPos) + str(s.enemyPos)
def ssaQE(i, s, j): return str(i) + str(s.transPos) + str(s.enemyPos)
def ssaQI(i, s, j): return str(i) + str(s.transPos) + str(s.enemyPos)



class Graph:
	def __init__(self, Nodes, alpha, delta, useSSA = False):
		## QNode(name, ssaQPredicate)
		if (useSSA):
			self.qIdle		= Nodes.QNode("QIdle",      ssaQI)
			self.qGet		= Nodes.QNode("QGet",       ssaQGet)
			self.qPut		= Nodes.QNode("QPut",       ssaQPut)
			self.qPickup	= Nodes.QNode("QPickup",    ssaQG)
			self.qPutdown	= Nodes.QNode("QPutdown",   ssaQP)
			self.qNavForGet	= Nodes.QNode("QNavForGet", ssaQNavForGet)
			self.qNavForPut	= Nodes.QNode("QNavForPut", ssaQNavForPut)
			self.qNorth		= Nodes.QNode("QNorth",     ssaQN)
			self.qSouth		= Nodes.QNode("QSouth",     ssaQS)
			self.qWest		= Nodes.QNode("QWest",      ssaQW)
			self.qEast		= Nodes.QNode("QEast",      ssaQE)
		else:
			self.qIdle		= Nodes.QNode("QIdle",      None)
			self.qGet		= Nodes.QNode("QGet",       None)
			self.qPut		= Nodes.QNode("QPut",       None)
			self.qPickup	= Nodes.QNode("QPickup",    None)
			self.qPutdown	= Nodes.QNode("QPutdown",   None)
			self.qNavForGet	= Nodes.QNode("QNavForGet", None)
			self.qNavForPut	= Nodes.QNode("QNavForPut", None)
			self.qNorth		= Nodes.QNode("QNorth",     None)
			self.qSouth		= Nodes.QNode("QSouth",     None)
			self.qWest		= Nodes.QNode("QWest",      None)
			self.qEast		= Nodes.QNode("QEast",      None)

		## MNode(name, ID, alpha, delta, ssaMPredicate, terminalPredicate, bindings, binder, usePseudoRewards, action = ' '):
		self.mRoot		= Nodes.MNode("MRoot",		 0, alpha, delta, None, isMaxRootTerminal, [], None, False)
		self.mGet		= Nodes.MNode("MGet",		 1, alpha, delta, None, isMaxGetTerminal, [1, 2], None, False)
		self.mPut		= Nodes.MNode("MPut",		 2, alpha, delta, None, isMaxPutTerminal, ['Z'], None, False)
		self.mNav		= Nodes.MNode("MNav",		 3, alpha, delta, None, isMaxNavTerminal, [], bMNav, False)
		if (useSSA):
			## set the abstraction functions for the primitive MNodes
			self.mIdle		= Nodes.MNode("MIdle",		 4, alpha, delta, ssaI, isPrimitiveTerminal, [], None, False, 'I')
			self.mPickup	= Nodes.MNode("MPickup",	 5, alpha, delta, ssaG, isPrimitiveTerminal, [], None, False, 'G')
			self.mPutdown	= Nodes.MNode("MPutdown",	 6, alpha, delta, ssaP, isPrimitiveTerminal, [], None, False, 'P')
			self.mNorth		= Nodes.MNode("MNorth",		 7, alpha, delta, ssaN, isPrimitiveTerminal, [], None, False, 'N')
			self.mSouth		= Nodes.MNode("MSouth",		 8, alpha, delta, ssaS, isPrimitiveTerminal, [], None, False, 'S')
			self.mWest		= Nodes.MNode("MWest",		 9, alpha, delta, ssaW, isPrimitiveTerminal, [], None, False, 'W')
			self.mEast		= Nodes.MNode("MEast",		10, alpha, delta, ssaE, isPrimitiveTerminal, [], None, False, 'E')
		else:
			self.mIdle		= Nodes.MNode("MIdle",		 4, alpha, delta, None, isPrimitiveTerminal, [], None, False, 'I')
			self.mPickup	= Nodes.MNode("MPickup",	 5, alpha, delta, None, isPrimitiveTerminal, [], None, False, 'G')
			self.mPutdown	= Nodes.MNode("MPutdown",	 6, alpha, delta, None, isPrimitiveTerminal, [], None, False, 'P')
			self.mNorth		= Nodes.MNode("MNorth",		 7, alpha, delta, None, isPrimitiveTerminal, [], None, False, 'N')
			self.mSouth		= Nodes.MNode("MSouth",		 8, alpha, delta, None, isPrimitiveTerminal, [], None, False, 'S')
			self.mWest		= Nodes.MNode("MWest",		 9, alpha, delta, None, isPrimitiveTerminal, [], None, False, 'W')
			self.mEast		= Nodes.MNode("MEast",		10, alpha, delta, None, isPrimitiveTerminal, [], None, False, 'E')

		## set each MaxNode-child of each QNodes
		self.qIdle.setMChild(self.mIdle)
		self.qGet.setMChild(self.mGet)
		self.qPut.setMChild(self.mPut)
		self.qPickup.setMChild(self.mPickup)
		self.qPutdown.setMChild(self.mPutdown)
		self.qNavForGet.setMChild(self.mNav)
		self.qNavForPut.setMChild(self.mNav)
		self.qNorth.setMChild(self.mNorth)
		self.qSouth.setMChild(self.mSouth)
		self.qWest.setMChild(self.mWest)
		self.qEast.setMChild(self.mEast)

		## set the QNode-children of each MaxNode
		self.mRoot.setQChildren([self.qGet, self.qPut])
		self.mGet.setQChildren([self.qPickup, self.qNavForGet])
		self.mPut.setQChildren([self.qPutdown, self.qNavForPut])
		self.mNav.setQChildren([self.qNorth, self.qSouth, self.qWest, self.qEast, self.qIdle])


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
