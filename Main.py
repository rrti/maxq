import sys, os

## static components (same for each task)
import Learner, ActionSelector, Nodes


def readArgs(params):
	for i in xrange(1, len(sys.argv)):
		if (i == 1):   params[i - 1] = sys.argv[i]
		elif (i == 2): params[i - 1] = int(sys.argv[i])
		elif (i == 3): params[i - 1] = int(sys.argv[i])
		elif (i == 9): params[i - 1] = int(sys.argv[i])
		else:          params[i - 1] = float(sys.argv[i])


def main(params, auto):
	## dir, batches, episodes, epsilon, alpha, beta, gamma, delta, useSSA
	defParams = ["",  1, 10000, 0.3, 0.9,  0.999, 1.0, 0.99999999, 1]
	fmtString = "usage: python Main.py <TaskDir/> [numBatches=%d, numEpisodes=%d, eps=%f, alpha=%f, beta=%f, gamma=%f, delta=%f, useSSA=%d]"

	if (not auto):
		if (len(sys.argv) > 1):
			## overwrite the default params if fed from
			## command-line and we aren't on auto-pilot
			readArgs(params)
		else:
			print(fmtString % (defParams[1], defParams[2], defParams[3], defParams[4], defParams[5], defParams[6], defParams[7], defParams[8]))
			sys.exit()

	if (len(params) == 0):
		params = defParams

	task        = params[0]
	numBatches  = params[1]
	numEpisodes = params[2]

	epsilon = params[3]
	alpha   = params[4]
	beta    = params[5]
	gamma   = params[6]
	delta   = params[7]

	useSSA = (params[8] == 1)

	if (task[len(task) - 1] != '/'):
		task += '/'

	## semi-dynamically loaded modules
	## (different per learning task)
	sys.path.append(task)
	import State, ActionSet, Graph

	actionSet      = ActionSet.ActionSet()
	actionSelector = ActionSelector.ActionSelector(epsilon, beta, actionSet)

	state = State.State()
	graph = Graph.Graph(Nodes, alpha, delta, useSSA)

	learner = Learner.Learner(actionSelector, graph, gamma)
	learner.run(state, numBatches, numEpisodes, params, True)

## for running in batch-mode (useful to find good
## combinations of parameters semi-automatically)
def batch(batches = 1, episodes = 10000, task = "RTSDefault/"):
	## exploration-rate range
	epsMin  = 0.2
	epsMax  = 0.2
	epsStep = 0.1
	## learning-rate range
	alphaMin  = 0.9
	alphaMax  = 0.9
	alphaStep = 0.1

	## epsilon-decay
	betaMin = 0.9999
	betaMax = 0.9999
	## alpha-decay
	deltaMin = 0.99999999
	deltaMax = 0.99999999

	eps   = epsMin
	alpha = alphaMin
	beta  = betaMin
	delta = deltaMin

	iMin = 8 ## number of decimals in deltaMin
	jMin = 4 ## number of decimals in betaMin

	i = iMin
	j = jMin

	while (eps <= epsMax):
		alpha = alphaMin

		while (alpha <= alphaMax):
			beta = betaMin; j = jMin

			while (beta <= betaMax):
				delta = deltaMin; i = iMin

				while (delta <= deltaMax):
					main([task, batches, episodes, eps, alpha, beta, 1.0, delta], True)

					delta = delta + (0.9 / (10 ** i)); i += 1

				beta = beta + (0.9 / (10 ** j)); j += 1

			alpha += alphaStep

		eps += epsStep


if (__name__ == "__main__"):
	main([], False)

