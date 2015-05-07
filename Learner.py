## NOTE: when we want aStar = a* = argmax_{a'} (C~(i, s', a') + V(a', s'))
## and its value vaStar = V~(i, s) = max_{a'} (C~(i, s', a') + V(a', s'))
## [where C~(i, s', a') + V(a', s') = Q~(i, s', a')] in the successor state
## s', selectNextTask() MUST examine terminal nodes (ie., a* is allowed to
## be terminal), unlike the default behavior which skips over them. However,
## to make automatic pseudo-reward learning work we need vaStar computed only
## for NON-terminal nodes (we call this value vaStarR) since a* can be equal
## to <a> and the pseudo-reward for action <a> should not be updated with its
## own terminated self-value, requiring a separate selectNextTaskEx() function
## ==> eg. if MExit has terminated and MRoot selects a*=MExit again, value of
## a* can be -1 which is greater (closer to 0) than value of a*=MGotoGoal
##
## NOTE: regarding pseudo-reward updates, action <a> is guaranteed to be
## terminal after the recursive call MAXQQ(a, s, depth + 1) returns, so we
## do not explicitely need to check this
##
## NOTE: we don't have to call evalMaxNode(a*, s') to calculate the uncontamined
## value V(a*, s') since we can just subtract the one contaminated C~(i, s', a*)
## value from vaStar = C~(i, s', a*) + V(a*, s')
##
##  a* = argmax_{a'} (C~(i, s', a') + V(a', s'))
## va* =    max_{a'} (C~(i, s', a') + V(a', s')) = max_{a'} Q~(i, s, a') = V~(i, s')

import random

def GetChar():
	import sys, tty, termios
	fd = sys.stdin.fileno()
	old_settings = termios.tcgetattr(fd)

	try:
		tty.setraw(fd)
		ch = sys.stdin.read(1)
	finally:
		termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

	if (ch == 'q'): sys.exit()
	return ch

## custom tuple-comparison function passed to
## sort(), this has to be in global namespace
def TupleCmp(t1, t2):
	v11 = t1[0]; v21 = t2[0]    ## floats (Q-values)
	v12 = t1[1]; v22 = t2[1]    ## integers (node IDs)
	e = 0.0000001               ## desired precision
	p = v11 - v21               ## t1[0] - t2[0]
	q = v12 - v22               ## t1[1] - t2[1]

	## sort in reverse (descending) order by Q-value
	if (p >  e): return -1
	if (p < -e): return  1

	## node Q-values are equal, break
	## tie by looking at their ID's
	if (q > 0): return -1
	if (q < 0): return  1

	return 0



class Learner:
	def __init__(self, actionSelector, graph, gamma):
		self.actionSelector = actionSelector
		self.graph = graph
		self.gamma = gamma
		self.pseudoRewardActivationTime = 0

	def run(self, state, numBatches, numEpisodes, params, verbose = True):
		for batch in xrange(numBatches):
			actionSumBatch = 0
			batchStats = ""

			## prepare empty files to write
			## statistics and history into
			self.writeBatchStats(batch, "", params, "w")

			for episode in xrange(numEpisodes):
				(rewardSumEp, actionSumEp) = self.episode(state, verbose, episode)
				actionSumBatch += actionSumEp
				batchStats = (str(actionSumBatch) + '\t' + str(rewardSumEp) + '\n')

				self.actionSelector.decayEpsilon()
				self.graph.reset(False, False)

				if (verbose):
					self.writeBatchStats(batch, batchStats, params, "a")

			"""
			state.pos[0] = 4
			state.pos[1] = 2

			mnode = self.graph.getMNode("MNav")
			mnode.setActiveBinding('N')
			tup = self.selectNextTask(mnode, state, greedy=True, skipTerminals=False, verbose=True)

			print("%s" % tup)
			"""

			self.actionSelector.resetEpsilon()
			self.graph.reset(verbose, True)


	def writeBatchStats(self, batchNum, string, params, mode = "a"):
		statsID = params[0][0: len(params[0]) - 1]
		epsilon = str(params[3])
		alpha = str(params[4])
		beta = str(params[5])
		gamma = str(params[6])
		delta = str(params[7])

		if (params[8]):
			ssaState = "SSA-"
		else:
			ssaState = "NOSSA-"

		batch = str(batchNum)
		filename = ssaState + statsID + "-eps" + epsilon + "-alpha" + alpha + "-beta" + beta + "-gamma" + gamma + "-delta" + delta + "-batch" + batch + ".dat"
		f = open("./Stats/" + filename, mode)
		f.write(string)
		f = f.close()

	def episode(self, state, verbose, time):
		state.randomize()

		## TODO: make these variables locally confined to MAXQ*()
		self.DBGMQ = 0
		self.DBGSN = 0
		self.rewardSumEp = 0.0
		self.actionTrace = []
		self.sss = state.clone()
		self.retCount = 0

		self.moveCount = 0
		self.actionSumEp = self.MAXQQ(self.graph.getRoot(), 0, time, [self.graph.getRoot()], [state.clone()])

		if (verbose and time >= 19900):
			print("%s" % self.actionTrace)

		return (self.rewardSumEp, self.actionSumEp)



	def MAXQQ(self, i, depth, time, callStack, stateStack):
		## enable this for "single-step" debugging
		if (self.DBGMQ): GetChar()

		if (self.DBGMQ): print("------------------------------------------------------------")
		if (self.DBGMQ): print("(%d) %s call-stack: %s" % (depth, ('\t' * depth), callStack))
		if (self.DBGMQ): print("(%d) %s state-stack: %s" % (depth, ('\t' * depth), stateStack))
		if (self.DBGMQ): print("(%d) %s node i:  %s" % (depth, ('\t' * depth), i))

		if (i.isPrimitive()):
			## get a reference to the top of the stack
			state = stateStack[-1]
			sstate = state.clone()

			(reward, legal) = self.actionSelector.getReward(state, i.action)

			if (legal):
				sstate.doAction(i.action)

			#### HACK 4 (fails both ways)
			#### parent = callStack[-2]
			#### if (parent.name == "MNav"):
			####	if (parent.getActiveBinding() == 'N' and sstate.pos == state.COORS['S']): reward -= 100.0
			####	if (parent.getActiveBinding() == 'S' and sstate.pos == state.COORS['N']): reward -= 100.0
			####	if (parent.getActiveBinding() == 'N' and sstate.pos == state.COORS['N']): reward += 100.0
			####	if (parent.getActiveBinding() == 'S' and sstate.pos == state.COORS['S']): reward += 100.0

			v = i.getVValue(state)
			b = (1.0 - i.alpha) * v + (i.alpha * reward)
			i.setVValue(state, b)

			self.actionTrace.append((str(state), i.action, str(sstate)))
			self.rewardSumEp += reward
			self.moveCount += 1

			if (self.DBGMQ): print("(%d) %s %s is PRIMITIVE" % (depth, ('\t' * depth), i))
			if (self.DBGMQ): print("(%d) %s state s BEFORE executing %s: %s" % (depth, ('\t' * depth), i, state))
			if (self.DBGMQ): print("(%d) %s s-stack BEFORE executing %s: %s" % (depth, ('\t' * depth), i, stateStack))

			## this alters stateStack[-1] *and* <state>
			stateStack[-1].copy(sstate)

			if (self.DBGMQ): print("(%d) %s state s AFTER executing %s (legal: %d): %s" % (depth, ('\t' * depth), i, legal, sstate))
			if (self.DBGMQ): print("(%d) %s s-stack AFTER executing %s (legal: %d): %s" % (depth, ('\t' * depth), i, legal, stateStack))
			if (self.DBGMQ): print("")

			del sstate
			return 1

		else:
			if (self.DBGMQ): print("(%d) %s %s is COMPOSITE" % (depth, ('\t' * depth), i))

			actionCount = 0
			iterCount = 0

			while (True):
				## original state at this recursion depth
				s = stateStack[-1].clone()

				if (i.isTerminal(s)[0]):
					if (self.DBGMQ): print("(%d) %s [WHILE] %s IS terminal in state %s (legal: %d)" % (depth, ('\t' * depth), i, s, i.isTerminal(s)[1]))
					break

				if (self.DBGMQ): print("(%d) %s [WHILE] %s is NOT terminal in state %s" % (depth, ('\t' * depth), i, s))
				if (self.DBGMQ): print("(%d) %s [WHILE] iteration count: %d" % (depth, ('\t' * depth), iterCount))

				## <qia> is Q-node child between max-nodes i and a
				(a, _, qia, ba) = self.selectNextTask(i, s, False, True)
				a.setActiveBinding(ba)

				if (self.DBGMQ): print("(%d) %s [WHILE] selected next task <a> in state %s: %s (BINDING <ba>: %s)" % (depth, ('\t' * depth), s, a, ba))

				callStack += [a]
				stateStack += [s.clone()]

				if (self.DBGMQ): print("(%d) %s [WHILE] appended call-stack: %s" % (depth, ('\t' * depth), callStack))
				if (self.DBGMQ): print("(%d) %s [WHILE] appended state-stack: %s" % (depth, ('\t' * depth), stateStack))
				if (self.DBGMQ): print("(%d) %s [WHILE] preparing to call MAXQQ(%s,   %s,   %s)..." % (depth, ('\t' * depth), a, callStack, stateStack))
				if (self.DBGMQ): print

				iterCount += 1
				numActions = self.MAXQQ(a, depth + 1, time, callStack, stateStack)
				actionCount += numActions

				## new state ("self.ss") is at top of stack after executing <a>
				## (because the MAXQQ() call that just returned did not pop it)
				ss = stateStack[-1].clone()

				if (self.DBGMQ): print("(%d) %s [WHILE] recursive call for task %s RETURNED, new action count: %d" % (depth, ('\t' * depth), a, actionCount))
				if (self.DBGMQ): print("(%d) %s [WHILE] original state: s=%s, successor state: ss=%s" % (depth, ('\t' * depth), s, ss))

				if (self.DBGMQ): print("(%d) %s [WHILE] call-stack AFTER recursive call (BEFORE popping top): %s" % (depth, ('\t' * depth), callStack))
				if (self.DBGMQ): print("(%d) %s [WHILE] state-stack AFTER recursive call (BEFORE popping top): %s" % (depth, ('\t' * depth), stateStack))

				## caller frame cleans up
				del callStack[-1]
				del stateStack[-1]

				if (self.DBGMQ): print("(%d) %s [WHILE] call-stack AFTER recursive call (AFTER popping top): %s" % (depth, ('\t' * depth), callStack))
				if (self.DBGMQ): print("(%d) %s [WHILE] state-stack AFTER recursive call (AFTER popping top): %s" % (depth, ('\t' * depth), stateStack))

				## replace the top of the current stack
				stateStack[-1].copy(ss)

				if (self.DBGMQ): print("(%d) %s [WHILE] state-stack after replacing top with <ss=%s>: %s" % (depth, ('\t' * depth), ss, stateStack))

				## not necessary for "Room/" (in that task
				## no illegal terminations are possible)
				rc = self.checkCallStack(callStack, depth, ss)

				if (rc > 0 and self.retCount == 0):
					if (self.DBGMQ): print("(%d) %s [WHILE] ILLEGALLY terminated ancestor in call-stack %s" % (depth, ('\t' * depth), callStack))
					if (self.DBGMQ): print("(%d) %s [WHILE] ILLEGALLY terminated ancestor in state ss=%s (RETCOUNT: %d)" % (depth, ('\t' * depth), ss, rc))
					self.retCount = rc

				#### HACK 1 (works, but R~ is doubled once again
				#### if HACK 2 is also enabled at the same time)
				#### and "works" only if MExit bindings are ['N'],
				#### not ['N', 'S']
				####
				#### updateAnyway = (False and (i.name == "MNav"))

				if (self.retCount == 0):
					## if retCount is 0, we might just have returned
					## from interrupted frames deeper in stack due to
					## an illegal termination, so make sure <a> isn't
					## illegally terminal before updating values
					##
					## NOTE: when MExit illegally terminates, nothing
					## is learned for the interrupted graph branch but
					## episode is allowed to continue in RoomExtended
					## (might break things for MNav?)
					##
					if (a.isTerminal(ss)[1]):
						## HACK 2: this eliminates the doubled pseudo-rewards
						## problem, but how can using the *old* state s (from
						## before the first recursive call) cause it ITFP?
						if (depth == 0):
							s.copy(ss)


						## get the best successor action (by Q-value [qIn = cIn + vEx]) for <s'>
						(aStar, vaStar, qiaStar, baStar) = self.selectNextTask(i, ss, True, False)
						aStar.setActiveBinding(baStar)

						if (self.DBGMQ): print("(%d) %s [WHILE] selected GREEDY action <a*> = SNT(%s, %s) = %s (BINDING: %s)" % (depth, ('\t' * depth), i, ss, aStar, baStar))

						## get the recursive value [viEx = cEx + vjEx] of a* for <s>
						(_, _, v1Ex) = self.evalMaxNode(aStar, s)							## V(a*, s ) "uncontaminated" == v1Ex == C + C + ... + Vprim
##						(_, _, v2Ex) = self.evalMaxNode(aStar, ss)							## V(a*, s') "uncontaminated" == v2Ex == C + C + ... + Vprim

						if (self.DBGMQ): print("(%d) %s [WHILE] value of <a*> in old state <s> = EMN(%s, %s) = %f" % (depth, ('\t' * depth), aStar, s, v1Ex))

						## note: <a> and <a*> can be the same node (pointer)
						a.setActiveBinding(ba)
						cInt = qia.getCIntValue(i, s, a)									## C~(i, s, a)
						cExt = qia.getCExtValue(i, s, a)									## C(i, s, a)

						aStar.setActiveBinding(baStar)
						cIntGreedy = qiaStar.getCIntValue(i, ss, aStar)						## C~(i, s', a*)
						cExtGreedy = qiaStar.getCExtValue(i, ss, aStar)						## C(i, s', a*)

						v2Ex = vaStar - cIntGreedy											## V(a*, s') = V(i, s') - C~(i, s', a*)
						a.setActiveBinding(ba)

						Ri = self.getUpdatePseudoReward(i, a, time, ss)

						cIntBackup = (1.0 - i.alpha) * cInt + i.alpha * (Ri + cIntGreedy + v1Ex)
						cExtBackup = (1.0 - i.alpha) * cExt + i.alpha * (     cExtGreedy + v2Ex)

						#### HACK 3 (works iif MExit bindings are ['N'],
						#### promotes MNav's legal termination states)
						#### if (i.ID == 3):
						####	if (i.getActiveBinding() == 'N' and ss.pos == [1, 4]): cIntBackup += 100
						####	if (i.getActiveBinding() == 'S' and ss.pos == [5, 4]): cIntBackup += 100

						if (self.DBGMQ): print("(%d) %s [WHILE] pseudo-reward Ri = R(i=%s, ss=%s) = %f" % (depth, ('\t' * depth), i, ss, Ri))
						if (self.DBGMQ): print("(%d) %s [WHILE] internal C-backup Cin(i=%s, s=%s, a=%s) = %f" % (depth, ('\t' * depth), i, s, a, cIntBackup))
						if (self.DBGMQ): print("(%d) %s [WHILE] external C-backup Cex(i=%s, s=%s, a=%s) = %f" % (depth, ('\t' * depth), i, s, a, cExtBackup))
						if (self.DBGMQ): print("")

						## update C~(i, s, a) and C(i, s, a)
						qia.setCIntValue(i, s, a, cIntBackup)
						qia.setCExtValue(i, s, a, cExtBackup)

						i.decayAlpha()
						del s; del ss
				else:
					## break out the while-loop at this stackframe, no C-value updates
					## (the special case where "i invoked j and j is terminal, update
					## C(i, s, j)" is automatically handled since after node j returns
					## i is the last node on the stack (so retCount == 0) and the next
					## loop-iteration will see that i.isTerminal(s))
					if (self.DBGMQ): print("(%d) %s [WHILE] self.retCount %d > 0, TERMINATING iteration %d" % (depth, ('\t' * depth), self.retCount, iterCount))
					if (self.DBGMQ): print("")
					del s; del ss
					break


			if (self.retCount > 0):
				self.retCount -= 1

			return actionCount




	## get the pseudo-reward for node <i>, and at
	## the same time update the reward for node <j>
	##
	def getUpdatePseudoReward(self, i, j, time, ss):
		## online pseudo-reward learning extension as
		## discussed on page 298 of Dietterich's paper
		## NOTE: vaStar is also needed when <j> uses
		## state abstractions, so always pass it along
		##
		if (time >= self.pseudoRewardActivationTime):
			## force this to zero to disable use of pseudo-rewards
			## (making MAXQQ algorithmically equivalent to MAXQ0)
			## Ri = 0.0
			Ri = i.getPseudoReward(ss, disabled = False)

			if (j.usesPseudoRewards()):
				## <j> was the child of <i> using pseudo-rewards
				## (ex. MExit underneath MRoot) and <j> has now
				## terminated (because called from <i>'s frame),
				## vaStarR would then be the value of MGotoGoal
				## in either [1, 4] or [5, 4]

				## do we actually need selectNextTaskEx()? <j>
				## (plus its binding) is terminal so is skipped
				## already because skipTerminals = True
				(_, vaStarR, _, _) = self.selectNextTask(i, ss, True, True, False)
				## (_, vaStarR, _, _) = self.selectNextTaskEx(i, ss, True, a, True)

				## print("[getUpdatePseudoReward(), time %d] i=%s, j=%s, ss=%s, vaStarR=%f" % (time, i, j, ss, vaStarR))

				## NOTE: does not seem to matter whether vaStar
				## is calculated with or without skipping node
				## <j> (even if j == j*) for Room, does however
				## influence RoomW and possibly other tasks
				j.setPseudoReward(ss, vaStarR)
		else:
			Ri = 0.0

		return Ri


	def checkCallStack(self, stack, depth, ss):
		## how many nodes need to be interrupted (popped)
		retCount = 0

		if (self.retCount == 0):
			## at <depth> d, stack has size <d + 1>
			stackSize = len(stack)
			assert(stackSize == depth + 1)

			## only check the stack if we are not already busy
			## interrupting MAXQQ execution (unwinding), stack
			## at this point contains nodes [MRoot, ..., <i>]
			## so skip the last node since MAXQQ() takes care
			## of that check in its while-loop
			##
			## note: should isTerminal() use <ss> or <s>?
			##
			for idx in xrange(stackSize - 1):
				node = stack[idx]
				term = node.isTerminal(ss)

				if (term[0] and not term[1]):
					retCount = stackSize - idx
					## print("%s [CheckCallStack] node %s illegally terminated in ss=%s, retCnt %d" % (('\t' * depth), node, ss, retCount))

		return retCount



	## computes the value-sum of each possible path from
	## maxNode i through the graph recursively and returns
	## the cumulative value (C + C + ... + V) corresponding
	## to the best path, also returns the child action j of
	## i that lies on this best path
	##
	## for MAXQQ the "best" path is decided by the internal
	## C~ values, but the cumulative value returned at the
	## top of the recursion is composed of external C-values
	## which are uncontaminated
	def evalMaxNode(self, i, s, verbose = False):
		if (i.isPrimitive()):
			return (i, i.getVValue(s), i.getVValue(s))

		else:
			viInBest = -999999.0
			viExBest = 0.0

			jBest = None

			for QNodej in i.children:
				j = QNodej.maxNode
				bjOld = j.getActiveBinding()

				if (i.isParameterized()):
					## j must get a copy of i's binding (eg. MGet ==> MNav)
					bi = i.getActiveBinding()
					bj = j.translate(s, bi)
					j.setActiveBinding(bj)

					(_jRec, vjIn, vjEx) = self.evalMaxNode(j, s, verbose)
					cIn = QNodej.getCIntValue(i, s, j)
					cEx = QNodej.getCExtValue(i, s, j)
					viIn = cIn + vjIn
					viEx = cEx + vjEx

					if (viIn > viInBest):
						viInBest = viIn
						viExBest = viEx
						jBest = j

					j.setActiveBinding(bjOld)

				elif (j.isParameterized()):
					## all possible concrete instances
					## of node j must be evaluated (eg.
					## MRoot ==> MGet)
					for bj in j.bindings:
						j.setActiveBinding(bj)

						(_jRec, vjIn, vjEx) = self.evalMaxNode(j, s, verbose)
						cIn = QNodej.getCIntValue(i, s, j)
						cEx = QNodej.getCExtValue(i, s, j)
						viIn = cIn + vjIn
						viEx = cEx + vjEx

						if (viIn > viInBest):
							viInBest = viIn
							viExBest = viEx
							jBest = j

						j.setActiveBinding(bjOld)

				else:
					## evaluate node j directly (eg. MRoot ==> MIdle)
					(_jRec, vjIn, vjEx) = self.evalMaxNode(j, s, verbose)
					cIn = QNodej.getCIntValue(i, s, j)
					cEx = QNodej.getCExtValue(i, s, j)
					viIn = cIn + vjIn
					viEx = cEx + vjEx

					if (viIn > viInBest):
						viInBest = viIn
						viExBest = viEx
						jBest = j

			return (jBest, viInBest, viExBest)



	## chooses an action <a> according to the current
	## ordered GLIE epsilon-greedy exploration policy
	##
	## for MAXQQ this uses a contaminated (internal)
	## value C~(i, s, a') for each possible child a'
	## of i rather than an uncontaminated (external)
	## one
	def selectNextTask(self, i, s, greedy = False, skipTerminals = True, verbose = False):
		r = random.random()
		l = []

		## loop through the QNode-children of MaxNode i
		for QNodej in i.getChildren():
			## retrieve the MaxNode j
			j = QNodej.maxNode
			bjOld = j.getActiveBinding()

			## case 1: MaxNode i is parameterized,
			## so j must receive translated binding
			if (i.isParameterized()):
				if (verbose):
					print("\t[SNT][CASE1] i=%s, j=%s" % (i, j))

				bi = i.getActiveBinding()
				bj = j.translate(s, bi)
				j.setActiveBinding(bj)

				## if j=MNav uses pseudorewards, R~ is always 0
				## because (greedy and skipTerminals) == False
				## and (not j.isTerminal(s)[0]) == False (the
				## node HAS terminated, i=MExit)

				## terminal MaxNodes may never be chosen
				## (except when we want the greedy action
				## a* in s')
				if ((greedy and (not skipTerminals)) or (not j.isTerminal(s)[0])):
					cIn = QNodej.getCIntValue(i, s, j)

					(_, _vIn, vEx) = self.evalMaxNode(j, s)
					qIn = (cIn + vEx)

					if (verbose):
						print("\t\t[SNT] C~(%s, %s, %s)=%f, Vex(%s, %s)=%f" % (i, s, j, cIn, j, s, vEx))

					l.append((qIn, j.getID(), QNodej, j, bj))

				j.setActiveBinding(bjOld)

			## case 2: MaxNode i is concrete but
			## j is parameterized, so j must pick
			## the best of its possible bindings
			elif (j.isParameterized()):
				if (verbose):
					print("\t[SNT][CASE2] i=%s, j=%s" % (i, j))

				for bj in j.bindings:
					j.setActiveBinding(bj)

					## terminal MaxNodes may never be chosen
					## (except when we want the greedy action
					## a* in s')
					if ((greedy and (not skipTerminals)) or (not j.isTerminal(s)[0])):
						cIn = QNodej.getCIntValue(i, s, j)

						(_, _vIn, vEx) = self.evalMaxNode(j, s)
						qIn = (cIn + vEx)

						if (verbose):
							print("\t\t[SNT] C~(%s, %s, %s)=%f, Vex(%s, %s)=%f" % (i, s, j, cIn, j, s, vEx))

						l.append((qIn, j.getID(), QNodej, j, bj))

					j.setActiveBinding(bjOld)

			## case 3: MaxNodes i and j both are concrete
			## so nothing has to be done regarding bindings
			else:
				if (verbose):
					print("\t[SNT][CASE3] i=%s, j=%s" % (i, j))

				## terminal MaxNodes may never be chosen
				## (except when we want the greedy action
				## a* in s')
				if ((greedy and (not skipTerminals)) or (not j.isTerminal(s)[0])):
					cIn = QNodej.getCIntValue(i, s, j)

					(_, _vIn, vEx) = self.evalMaxNode(j, s, True)
					qIn = cIn + vEx

					if (verbose):
						print("\t\t[SNT] C~(%s, %s, %s)=%f, Vex(%s, %s)=%f" % (i, s, j, cIn, j, s, vEx))

					l.append((qIn, j.getID(), QNodej, j, None))


		## sort list by first element of every
		## tuple (C-value) in descending order
		## and by second (so as to satisfy the
		## ordered GLIE policy requirement)
		##
		## l.sort(reverse = True)
		assert(len(l) > 0)
		l.sort(TupleCmp)

		if (verbose):
			if (i.name == "MNav" and i.getActiveBinding() == 'N'): print("\t[SNT] MNav bound to NORTH (state %s): %s" % (s, l))
			if (i.name == "MNav" and i.getActiveBinding() == 'S'): print("\t[SNT] MNav bound to SOUTH (state %s): %s" % (s, l))


		## calling function makes bindings active now
		if (greedy or (r > self.actionSelector.epsilon) or len(l) == 1):
			return (l[0][3], l[0][0], l[0][2], l[0][4])

		## note: assumes len(l) >= 2
		idx = random.randint(1, len(l) - 1)
		return (l[idx][3], l[idx][0], l[idx][2], l[idx][4])



	## same as selectNextTask(), but skips child
	## <nodeToSkip> of node <i> (used for getting
	## the pseudo-reward update vaStarR only)
	##
	## FIXME: compares node pointers, but should
	## compare concrete node instances (bindings
	## etc)
	def selectNextTaskEx(self, i, s, greedy, nodeToSkip, verbose = False):
		if (self.DBGSN): print("")
		if (self.DBGSN): print("[selectNextTaskEx(), i=%s, a=nodeToSkip=%s, s=%s]" % (i, nodeToSkip, s))
		r = random.random()
		l = []

		for QNodej in i.getChildren():
			j = QNodej.maxNode
			## if <j> points to same node as <nodeToSkip>, assigning
			## <bj> to <j> would affect <nodeToSkip> instance as well
			## (defeating the point of the "j != n" check); therefore
			## compare ID's to verify nodes are different
			eq = (j.ID == nodeToSkip.ID)
			bjOld = j.getActiveBinding()

			if (i.isParameterized()):
				if (self.DBGSN): print("[selectNextTaskEx(), case 1] j=%s" % j)
				bi = i.getActiveBinding()
				bj = j.translate(s, bi)
				j.setActiveBinding(bj)

				## if (greedy and (j != nodeToSkip)):
				if (greedy and (not eq or bj != bjOld)):
					cIn = QNodej.getCIntValue(i, s, j)

					(_, _vIn, vEx) = self.evalMaxNode(j, s)
					qIn = (cIn + vEx)
					l.append((qIn, j.getID(), QNodej, j, bj))

				j.setActiveBinding(bjOld)

			elif (j.isParameterized()):
				if (self.DBGSN): print("[selectNextTaskEx(), case 2] j=%s" % j)
				for bj in j.bindings:
					j.setActiveBinding(bj)

					## if (greedy and (j != nodeToSkip)):
					if (greedy and (not eq or bj != bjOld)):
						cIn = QNodej.getCIntValue(i, s, j)

						(_, _vIn, vEx) = self.evalMaxNode(j, s)
						qIn = (cIn + vEx)
						l.append((qIn, j.getID(), QNodej, j, bj))

					j.setActiveBinding(bjOld)

			else:
				if (self.DBGSN): print("[selectNextTaskEx(), case 3] j=%s" % j)
				## if (greedy and (j != nodeToSkip)):
				if (greedy and (not eq)):
					cIn = QNodej.getCIntValue(i, s, j)

					(_, _vIn, vEx) = self.evalMaxNode(j, s, True)
					qIn = cIn + vEx

					if (self.DBGSN): print("\t[selectNextTaskEx()] possible next task in state %s is %s" % (s, j))
					if (self.DBGSN): print("\t[selectNextTaskEx()] Cin(%s, %s, %s) = %f" % (i, s, j, cIn))
					if (self.DBGSN): print("\t[selectNextTaskEx()] vEx = EMN(%s, %s) = %f" % (j, s, vEx))
					if (self.DBGSN): print("\t[selectNextTaskEx()] qIn = cIn + vEx = %f" % (qIn))

					l.append((qIn, j.getID(), QNodej, j, None))


		assert(len(l) > 0)
		l.sort(TupleCmp)

		if (greedy or (r > self.actionSelector.epsilon) or len(l) == 1):
			return (l[0][3], l[0][0], l[0][2], l[0][4])

		idx = random.randint(1, len(l) - 1)
		return (l[idx][3], l[idx][0], l[idx][2], l[idx][4])

