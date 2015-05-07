#########################
## TERMINAL PREDICATES ##
#########################
def isTerminalMRoot(g, state, param):
	## we really want to check if MExit *and* MGotoGoal
	## are terminal, but we can't because MaxExit is a
	## "terminate once" node which stores hasTerminated
	## in its instances... which is why we cannot call
	## "isTerminalMExit() and isTerminalMGotoGoal()"
	## and must rely on fixed temporal ordering of node
	## execution
	##
	## MRoot cannot terminate illegally
	return (state.pos == state.COORS['G'], True)



def isLegalTerminationMExit(s, p):
	## DBG
	## if MNav is allowed to complete and cross into right room
	## episode rewards still converge to -9, so interruption of
	## MExit can not be responsible?
	## also, pseudo-rewards are doubled again when HACK #2 is
	## enabled and even quadrupled (!) when it is not
	## return True

	## called only when node (MExit) terminates,
	## determines legality status of termination
	if (p == 'N'): return (s.pos == s.COORS['N'])
	if (p == 'S'): return (s.pos == s.COORS['S'])

## MExit has bindings 'N' and 'S'
def isTerminalMExit(g, s, p):
	#### this won't work: we might have moved back east since completing
	#### MExit, need to check hasTerminated instead (but need access to
	#### Graph instance for that)
	####
	#### if (param == 'G'): return (state.pos[1] >= state.NUM_COLS - 2)

	if (s.pos == s.COORS['N'] or s.pos == s.COORS['S']):
		return (True, isLegalTerminationMExit(s, p))
	else:
		return (False, True)



## MGotoGoal has only binding 'G' (rather silly to use [p])
def isTerminalMGotoGoal(g, s, p):
	## if MExit has not yet terminated, we may not
	## pick the MGotoGoal node (temporal restraint)
	##
	## MExit ==> MGotoGoal would be precondition, if
	## snt(MRoot) tries to select MGotoGoal it first
	## should check that MExit.hasTerminated == True
	##
	## MGotoGoal cannot terminate illegally
	b1 = (s.pos == s.COORS[p])
	b2 = (g.getMNode("MExit")).hasTerminated
	return ((b1 or not b2), True)



def isLegalTerminationMNav(s, p):
	if (p == 'N'): return (s.pos == s.COORS['N'])
	if (p == 'S'): return (s.pos == s.COORS['S'])
	if (p == 'G'): return True

def isTerminalMNav(g, s, p):
	## MNav cannot terminate illegally (technically not even true:
	## although MNav gets binding from MExit it can still end up
	## at wrong exit! however, because MExit's isLegalTermination()
	## is checked first due to checkCallStack(), the return value
	## here is irrelevant)
	##
	return (s.pos == s.COORS[p], True)
	## return (s.pos == s.COORS[p], isLegalTerminationMNav(s, p))



def isTerminalMPrim(g, s, p):
	## primitive nodes never terminate
	return (False, True)



####################################
## BINDING TRANSLATION PREDICATES ##
####################################
def navBindTransFunc(state, param):
	return param




class Graph:
	def __init__(self, Nodes, alpha, delta, useSSA):
		## MNode(name, ID, alpha, delta, ssaMPredicate, terminalPredicate, termOnce, bindings, bindingPredicate, usePseudoRewards, action = ' ')
		self.mRoot     = Nodes.MNode(self, "MRoot",     0, alpha, delta, None, isTerminalMRoot,     True, [],         None,             False)
	##	self.mExit     = Nodes.MNode(self, "MExit",     1, alpha, delta, None, isTerminalMExit,     True,  ['N', 'S'], None,             False)      ## [N, S] without R~
		self.mExit     = Nodes.MNode(self, "MExit",     1, alpha, delta, None, isTerminalMExit,     True,  ['N', 'S'], None,             True)       ## [N, S] with R~    ==> SHOULD learn to always pick N [-7]
	##	self.mExit     = Nodes.MNode(self, "MExit",     1, alpha, delta, None, isTerminalMExit,     True,  ['N'],      None,             False)      ## [N   ] without R~ ==> SHOULD learn to always pick N [-7]
	##	self.mExit     = Nodes.MNode(self, "MExit",     1, alpha, delta, None, isTerminalMExit,     True,  ['N'],      None,             True)       ## [N   ] with R~
	##	self.mExit     = Nodes.MNode(self, "MExit",     1, alpha, delta, None, isTerminalMExit,     True,  ['S'],      None,             False)      ## [S   ] without R~ ==> SHOULD learn to always pick S [-9]

		self.mGotoGoal = Nodes.MNode(self, "MGotoGoal", 2, alpha, delta, None, isTerminalMGotoGoal, False, ['G'],      None,             False)
		self.mNav      = Nodes.MNode(self, "MNav",      3, alpha, delta, None, isTerminalMNav,      False, [],         navBindTransFunc, False)      ## MNav is recursively optimal without R~ ==> MExit(N) always fails? doesn't work, MExit only has MNav child
		self.mNorth    = Nodes.MNode(self, "MNorth",    4, alpha, delta, None, isTerminalMPrim,     False, [],         None,             False, 'N')
		self.mSouth    = Nodes.MNode(self, "MSouth",    5, alpha, delta, None, isTerminalMPrim,     False, [],         None,             False, 'S')
		self.mEast     = Nodes.MNode(self, "MEast",     6, alpha, delta, None, isTerminalMPrim,     False, [],         None,             False, 'E')
		self.mWest     = Nodes.MNode(self, "MWest",     7, alpha, delta, None, isTerminalMPrim,     False, [],         None,             False, 'W')


		## QNode(name, ssaQPredicate, maxNode = None)
		self.qExit		= Nodes.QNode("QExit",      None, self.mExit)
		self.qGotoGoal	= Nodes.QNode("QGotoGoal",  None, self.mGotoGoal)
		self.qNavExit	= Nodes.QNode("QNavExit", 	None, self.mNav)
		self.qNavGoal	= Nodes.QNode("QNavGoal", 	None, self.mNav)
		self.qNorth		= Nodes.QNode("QNorthG",  	None, self.mNorth)
		self.qSouth		= Nodes.QNode("QSouthG",  	None, self.mSouth)
		self.qEast		= Nodes.QNode("QEastG",   	None, self.mEast)
		self.qWest		= Nodes.QNode("QWestG",   	None, self.mWest)

		## set the QNode-children of each MNode
		self.mRoot.setQChildren([self.qExit, self.qGotoGoal])
		self.mExit.setQChildren([self.qNavExit])
		self.mGotoGoal.setQChildren([self.qNavGoal])
		self.mNav.setQChildren([self.qNorth, self.qSouth, self.qEast, self.qWest])

		## MNodes that have the terminateOnce (per episode) property
		##
		## NOTE: strictly speaking MGotoGoal should be in here too,
		## but we don't want this (when MExit illegally terminates
		## eg. because MNav has explored to eg. 'S' while binding
		## was 'N' and stack is interrupted, Root cannot then pick
		## MGotoGoal since MGotoGoal.isTerminal() will have been
		## called earlier and set MGotoGoal.hasTerminated to true
		## (this is why we need *proper* preconditions)
		##
		## NOTE: should MExit or MNav use pseudo-rewards here? (when
		## MExit uses them, R~ values stay at 0.0 so this points to
		## a bug)
		##
		self.MNodesLst = [self.mRoot, self.mExit]
		self.MNodesMap = {
			"MRoot": self.mRoot, "MExit": self.mExit, "MGotoGoal": self.mGotoGoal, "MNav": self.mNav,
			"MNorth": self.mNorth, "MSouth": self.mSouth, "MEast": self.mEast, "MWest": self.mWest}

	def getMNode(self, name):
		return self.MNodesMap[name]


	def reset(self, verbose, batchReset):
		if (batchReset):
			self.resetRec(self.mRoot, verbose, True)
		else:
			for n in self.MNodesLst:
				n.reset(False)

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
