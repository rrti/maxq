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
	bool1 = ((state.unit1Loc != 'T') and (state.unit2Loc != 'T'))
	bool2 = (not isMaxPassEnemyTerminal(state, param))
	return (bool1 or bool2)

def isMaxNavTerminal(state, param):
	if (param == 'T'): return True
	return (state.transPos == state.COORS[param])

def isMaxPassEnemyTerminal(state, param):
	## this can become terminal more than once, if the
	## transport moves left (west) *after* moving right
	##
	## return (state.transPos[1] >= (state.NUM_COLS - 3))
	## DBG
	return True

def isPrimitiveTerminal(state, param):
	return False

###################################
## BINDING TRANSLATION PREDICATE ##
###################################
def bMNav(state, param):
	if (param == 1): return state.unit1Loc
	if (param == 2): return state.unit2Loc
	if (param == '+'): return '+'
	if (param == '-'): return '-'
	if (param == 'Z'): return 'Z'

	## should not happen
	return None

class Graph:
	## Nodes is the Module instance
	def __init__(self, Nodes, alpha, delta, useSSA):
		## Composites
		self.mRoot			= Nodes.MNode("MRoot",		0, alpha, delta, None, isMaxRootTerminal, [], None, False)
		self.mGet			= Nodes.MNode("MGet",		1, alpha, delta, None, isMaxGetTerminal, [1, 2], None, False)
		self.mPassEnemy		= Nodes.MNode("MPassEnemy",	2, alpha, delta, None, isMaxPassEnemyTerminal, ['+', '-'], None, True)
		self.mPut			= Nodes.MNode("MPut",		3, alpha, delta, None, isMaxPutTerminal, ['Z'], None, False)
		self.mNav			= Nodes.MNode("MNav",		4, alpha, delta, None, isMaxNavTerminal, [], bMNav, False)

		## Primitives
		self.mIdle			= Nodes.MNode("MIdle",		5, alpha, delta, None, isPrimitiveTerminal, [], None, False, 'I')
		self.mPickup		= Nodes.MNode("MPickup",	6, alpha, delta, None, isPrimitiveTerminal, [], None, False, 'G')
		self.mPutdown		= Nodes.MNode("MPutdown",	7, alpha, delta, None, isPrimitiveTerminal, [], None, False, 'P')
		self.mNorth			= Nodes.MNode("MNorth",		8, alpha, delta, None, isPrimitiveTerminal, [], None, False, 'N')
		self.mSouth			= Nodes.MNode("MSouth",		9, alpha, delta, None, isPrimitiveTerminal, [], None, False, 'S')
		self.mWest			= Nodes.MNode("MWest",		10, alpha, delta, None, isPrimitiveTerminal, [], None, False, 'W')
		self.mEast			= Nodes.MNode("MEast",		11, alpha, delta, None, isPrimitiveTerminal, [], None, False, 'E')

		## QNodes
		self.qIdle			= Nodes.QNode("QIdle", None, self.mIdle)
		self.qGet			= Nodes.QNode("QGet", None, self.mGet)
		self.qPut			= Nodes.QNode("QPut", None, self.mPut)
		self.qPassEnemy		= Nodes.QNode("QPassEnemy", None, self.mPassEnemy)
		self.qPickup		= Nodes.QNode("QPickup", None, self.mPickup)
		self.qPutdown		= Nodes.QNode("QPutdown", None, self.mPutdown)
		self.qNavGet		= Nodes.QNode("QNavGet", None, self.mNav)
		self.qNavPut		= Nodes.QNode("QNavPut", None, self.mNav)
		self.qNavPass		= Nodes.QNode("QNavPass", None, self.mNav)
		self.qNorth			= Nodes.QNode("QNorth", None, self.mNorth)
		self.qSouth			= Nodes.QNode("QSouth", None, self.mSouth)
		self.qWest			= Nodes.QNode("QWest", None, self.mWest)
		self.qEast			= Nodes.QNode("QEast", None, self.mEast)

		## set the QNode-children of each MaxNode
		self.mRoot.setQChildren([self.qGet, self.qPassEnemy, self.qPut])
		self.mGet.setQChildren([self.qPickup, self.qNavGet])
		self.mPassEnemy.setQChildren([self.qNavPass])
		self.mPut.setQChildren([self.qPutdown, self.qNavPut])
		self.mNav.setQChildren([self.qNorth, self.qSouth, self.qIdle, self.qWest, self.qEast])

	def reset(self, verbose):
		self.resetRec(self.mRoot, verbose)

	def resetRec(self, node, verbose):
		node.printMe(verbose)
		node.reset()

		if (node.isPrimitive()):
			return

		for child in node.getChildren():
			self.resetRec(child, verbose)

	def getRoot(self):
		return self.mRoot

