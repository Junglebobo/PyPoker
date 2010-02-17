from hand import *

class OpponentModeller:

	# create new instance of the modeller
	def __init__(self):
		self.stack = {} # stack of player, action, context for use in the possible showdown
		self.playerTable = {}
		
	# ask how good cards can be expected from a given player in a given context when he does a action
	# return [avgCardStrength, observations]
	def ask(self, player, context, action):
		return self.getPlayerContextAction(player, context, action)
	
	# let the modeller know about something someone did, and in what context they did it
	def tell(self, player, context, action, tableCards):
		pnr = player.getPlayerNumber()
		if (pnr not in self.stack):
			self.stack[pnr] = []
		self.stack[pnr].append([context, action, tableCards])
	
	# Returns a dictionary with keys player-numbers, and values tuples of estimated 
	# hand-strength at the moment (based on the last action they did this round) 
	# and the number of observations supporting this average. 
	# {pnr:(estimatedHandPower, numberOfObservations), ...}
	def getEstOpponentCardPowers(self):
		ret = {}
		for pnr, list in self.stack.iteritems():
			if not list: continue # player haven't done anything yet this round
			context = list[-1][0]
			action = list[-1][1]
			ret[pnr] = self.getPlayerContextAction(pnr, context, action)
		return ret
	
	# Use information about a players hand to update the estimates
	# by looking at what he did this round.
	def showdown(self, player, cards):
		pnr = player.getPlayerNumber()
		list = self.stack[pnr]
		# learn what we can from the stack of actions
		for situation in list:
			context = situation[0]
			action = situation[1]
			tcards = situation[2]
			if not tcards:
				continue # we do not use the preflop hands..
			hand = Hand(tcards + cards)
			pow = hand.power()[0]
			(oldAvg, numObs) = self.getPlayerContextAction(player, context, action)
			if numObs == 0:
				newAvg = pow
			else:
				newAvg = self._expMovAvg(oldAvg, numObs, pow, 0.3)
			self.setPlayerContextAction(player, context, action, (newAvg, numObs+1))
	
	# empty stack, i.e a new round have begun
	def clear(self):
		for i in self.stack:
			self.stack[i] = []
	
	def getPlayerContextAction(self, player, context, action):
		if isinstance(player,int):
			pnr = player			
		else:
			pnr = player.getPlayerNumber()
		if pnr not in self.playerTable:
			self.playerTable[pnr] = {}
		if context not in self.playerTable[pnr]:
			self.playerTable[pnr][context] = {}
		if action not in self.playerTable[pnr][context]:
			self.playerTable[pnr][context][action] = (None, 0)			
		avg = self.playerTable[pnr][context][action][0]
		obs = self.playerTable[pnr][context][action][1]
		return (avg, obs)
		
	def setPlayerContextAction(self, player, context, action, (avg, obs)):
		self.playerTable[player.getPlayerNumber()][context][action] = (avg, obs)
	
	# returns [avg, numObs+1] calculated by exponential moving weighted average
	def _expMovAvg(self, avg, numObs, newObs, alpha):
		return alpha*newObs + (1-alpha)*avg
		
	def printStats(self):
		for pnr, d in self.playerTable.iteritems():
			print str(pnr) + ": " + str(d)
