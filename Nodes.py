class MNode:
	def __init__(self, graph, name, ID, alpha, delta, ssaMPredicate, terminalPredicate, termOnce, bindings, bindingPredicate, usePseudoRewards, action = ' '):
		self.graph = graph                          ## reference to the task graph this node is contained in
		self.name = name                            ## string identifier
		self.ID = ID                                ## numerical identifier
		self.bindingPredicate = bindingPredicate    ## function that converts our bindings to format suitable for child
		self.ssaMPredicate = ssaMPredicate          ## function that performs safe-state abstraction for this MNode
		self.terminalPredicate = terminalPredicate  ## function that checks whether we are (il-)legally terminal given a state
		## child Q-Nodes
		self.children = []
		## primitive action for leaf max-nodes
		self.action = action
		self.params = []
		## contains a list of the possible bindings for this maxnode
		self.bindings = bindings
		self.V = {}
		self.R = {}
		self.alpha = alpha
		self.alphaStart = alpha
		self.alphaMin = 0.05
		self.delta = delta
		self.theta = 0.1
		self.activeBinding = None
		self.usePseudoRewards = usePseudoRewards

		self.hasTerminated = False                  ## true iif this is a terminateOnce node AND we have terminated in this episode
		self.legalTermination = True                ## true iif this node terminated in a legal manner (eg. NOT running out of fuel)
		self.terminateOnce = termOnce               ## can this node start and end only once per episode?

	def __repr__(self):
		return self.name + '(' + str(self.getActiveBinding()) + ')'

	def __eq__(self, other):
		return (self.ID == other.ID and self.getActiveBinding() == other.getActiveBinding())

	def printMe(self, verbose):
		if (verbose):
			## for state, value in self.V.items(): print(str("V(%s, %s) \t= %2.1f" % (str(self), str(state), value)))
			## for key, value in self.R.items(): print(str("R~(%s) \t= %2.1f" % (str(key), value)))
			k1 = self.V.keys(); k1.sort()
			k2 = self.R.keys(); k2.sort()
			for k in k1: print("V(%s, %s) \t= %2.1f" % (self, k, self.V[k]))
			for k in k2: print("R~(%s) \t= %2.1f" % (k, self.R[k]))

	def getID(self): return self.ID

	def decayAlpha(self):
		if (self.alpha > self.alphaMin):
			self.alpha *= self.delta

	def setQChildren(self, children): self.children = children
	def getChildren(self): return self.children


	## primitive-reward setter and getter
	def setVValue(self, s, val):
		if (self.ssaMPredicate == None): key = str(s)
		else: key = self.ssaMPredicate(s)

		self.V[key] = val

	def getVValue(self, s):
		if (self.ssaMPredicate == None): key = str(s)
		else: key = self.ssaMPredicate(s)

		if (not self.V.has_key(key)):
			## do not auto-create the key
			## self.V[key] = 0.0
			return 0.0

		return self.V[key]


	def setPseudoReward(self, state, reward):
		## always execute a stochastic update
		## since the direct update is FAR too
		## aggressive
		if (self.ssaMPredicate != None):
			key = str(self) + self.ssaMPredicate(state)
		else:
			key = str(self) + str(state)

		r = self.getRValue(key)
		update1 = r + self.theta * (reward - r)
		## update2 = (1.0 - self.theta) * r + (self.theta) * reward
		## update3 = (1.0 - self.alpha) * r + (self.alpha) * reward
		self.setRValue(key, update1)

	def getPseudoReward(self, state, disabled):
		if (disabled):
			return 0.0

		if (self.ssaMPredicate != None): k = str(self) + self.ssaMPredicate(state)
		else: k = str(self) + str(state)

		return self.getRValue(k)

	def usesPseudoRewards(self):
		return self.usePseudoRewards


	## pseudo-reward setter and getter
	## used internally by *PseudoReward()
	def setRValue(self, k, v):
		self.R[k] = v

	def getRValue(self, k):
		if (not self.R.has_key(k)):
			## do not auto-create the key
			## self.R[k] = 0.0
			return 0.0

		return self.R[k]


	def setActiveBinding(self, binding):
		self.activeBinding = binding

	def getActiveBinding(self):
		if (self.activeBinding != None):
			return self.activeBinding
		else:
			return ''


	def translate(self, state, binding):
		if (self.bindingPredicate == None):
			return ''
		else:
			return self.bindingPredicate(state, binding)



	## TODO: rewrite termination predicates
	## (for all tasks except RoomExtended)
	def isTerminal(self, state):
		if (self.terminateOnce):
			if (not self.hasTerminated):
				(self.hasTerminated, self.legalTermination) = self.terminalPredicate(self.graph, state, self.getActiveBinding())
			return (self.hasTerminated, self.legalTermination)

		return (self.terminalPredicate(self.graph, state, self.getActiveBinding()))

	def isParameterized(self): return (self.bindings != [])
	def isPrimitive(self): return (self.children == [])

	## called after a (batch of) episodes completes
	def reset(self, batchReset):
		if (batchReset):
			self.V.clear()
			self.R.clear()
			self.activeBinding = None
			self.alpha = self.alphaStart
		else:
			## these have to be reset after each episode
			self.hasTerminated = False
			self.legalTermination = True



class QNode:
	def __init__(self, name, ssaQPredicate, maxNode = None):
		self.name = name
		self.ssaQPredicate = ssaQPredicate
		## child Max-Node
		self.maxNode = maxNode
		## each QNode with parent i and child a stores
		## C_i(s, a) for each state s in S_i, where
		## C_i(s, a) is expected cumulative reward of
		## completing task M_i following policy pi after
		## executing 'action' (task) a in state s
		self.CInt = {}
		self.CExt = {}

	def __repr__(self):
		return self.name

	def printMe(self, verbose):
		if (verbose):
			## for key, value in self.CExt.items(): print(str("Ce(%s) \t= %2.1f" % (key, value)))
			## for key, value in self.CInt.items(): print(str("Ci(%s) \t= %2.1f" % (key, value)))
			k1 = self.CExt.keys(); k1.sort()
			k2 = self.CInt.keys(); k2.sort()
			for k in k1: print("Ce(%s) \t= %2.1f" % (k, self.CExt[k]))
			for k in k2: print("Ci(%s) \t= %2.1f" % (k, self.CInt[k]))


	def setCIntValue(self, i, s, j, val):
		if (self.ssaQPredicate == None):
			## non-abstracted CInt key
			key = str(i) + str(s) + str(j)
		else:
			## abstracted CInt key
			key = self.ssaQPredicate(i, s, j)

		self.CInt[key] = val

	def getCIntValue(self, i, s, j):
		if (self.ssaQPredicate == None):
			## non-abstracted CInt key
			key = str(i) + str(s) + str(j)
		else:
			## abstracted CInt key
			key = self.ssaQPredicate(i, s, j)

		if (not self.CInt.has_key(key)):
			## do not auto-create the key
			## self.CInt[key] = 0.0
			return 0.0

		return self.CInt[key]


	def setCExtValue(self, i, s, j, val):
		if (self.ssaQPredicate == None):
			## non-abstracted CExt key
			key = str(i) + str(s) + str(j)
		else:
			## abstracted CExt key
			key = self.ssaQPredicate(i, s, j)

		self.CExt[key] = val

	def getCExtValue(self, i, s, j):
		if (self.ssaQPredicate == None):
			## non-abstracted CExt key
			key = str(i) + str(s) + str(j)
		else:
			## abstracted CExt key
			key = self.ssaQPredicate(i, s, j)

		if (not self.CExt.has_key(key)):
			## do not auto-create the key
			## self.CExt[key] = 0.0
			return 0.0

		return self.CExt[key]


	## QNode always has a single child
	def setMChild(self, maxNode): self.maxNode = maxNode
	## this function must be named the
	## same as MNode::getChildren() so
	## we can do a recursive walk when
	## resetting the graph
	def getChildren(self): return [self.maxNode]


	def isPrimitive(self):
		return False

	def reset(self, batchReset):
		if (batchReset):
			self.CInt.clear()
			self.CExt.clear()
