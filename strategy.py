import random
import math
from simulator import *
from preFlopTable import *
from conf import *
from opponentModeller import *
#from poker import *


class Strategy():
		
	def __init__(self, player):
		self.player = player
		self.dealer = player.dealer
		self.modeller = player.dealer.log.modeller # yeah, yeah :p
		self.online_sims = 1000
		self.simulator = Simulator()
		self.preFlopTable = PreFlopTable()
		self.setEdgeBets()
		self.lastHandString = ""
		self.lastWins = 0.0

	# Returns action from selected strategy
	# 
	# Level 0: Random action strategy
	# Level 1: Action is always 'call'
	# Level 2: Main simulation and modelling strategy
	# 
	# Weights for parameters in the simulation strategy: 
	# [0]: Simulation estimation
	# [1]: Potodds estimation
	# [2]: Opponent modelling
	# [3]: Bluffing percentage		
	def decide(self, level=5, weights=[0.4, 0.35, 0.2, 0.05]):
		self.level = level
		self.weights = weights
		self.setEdgeBets()
		self.setVars()
		bet = 0
		
		# phase 1
		if level == 0: bet = self.strategyRandom()
		if level == 1: bet = self.strategyAlwaysCall()
		if level == 2: bet = self.strategyHandPower()
		
		# phase 2
		if level == 3: bet = self.strategyHandStrength()
		if level == 4: bet = self.strategyHandStrengthAndHandPower()
		
		# phase 3
		if level > 4: bet = self.mainStrategy()
		
		return self.bet(bet)


	#####################################################################
	# Phase 1 strategies
	
	def strategyRandom(self):
		actions = ['F',0,5,10,15,20,50,100,500,self.min_bet,self.max_bet]
		random.shuffle(actions)
		return actions[0]

	def strategyAlwaysCall(self):
		return self.bet(self.min_bet)
	
	def strategyHandPower(self):
		return self.feel_to_bet(self.updateFeelHand())
	
	
	#####################################################################
	# Phase 2 strategies

	def strategyHandStrength(self):
		feel = self.updateFeelWins(0.5, 1.0)
		return self.feel_to_bet(feel)	

	def strategyHandStrengthAndHandPower(self):
		feel = self.updateFeelHand()
		feel = self.updateFeelWins(feel, 0.4)
		return self.feel_to_bet(feel)
	
	
	#####################################################################
	# Phase 3 strategy with weights
	
	def mainStrategy(self):
		
		wWins  = self.weights[0]
		wOdds  = self.weights[1]
		wCards = self.weights[2]
		wBluff = self.weights[3]
		
		feel = self.updateFeelHand()
		#print "** hand", feel
		feel = self.updateFeelWins(feel, wWins)
		#print "** wins", feel
		feel = self.updateFeelPotOdds(feel, wOdds)
		#print "** odds", feel
		feel = self.updateFeelOpponentCards(feel, wCards)
		#print "** cards", feel
		feel = self.updateFeelBluff(feel, wBluff)
		
		if not config['level_test'] and config['debug']:
			print
			print "  " + self.player.handString()
			print "  pot:",self.pot
			print "  toCall:",self.toCall
			print "  wins:",self.wins()
			print "  odds:",self.potodds
			print "  feel:",feel
			print "  =", self.feel_to_bet(feel)
			print
		
		return self.feel_to_bet(feel)
		
	
	#####################################################################
	# Feel update methods
	
	def updateFeelHand(self):
		f = 0.5
		if self.preflop:
			f = 0.4
		else:
			p = self.player.hand().power()[0]
			if p == self.tableHandPower(): p = 1
			if p < 2: f = 0.1
			if p == 2: f = 0.3
			if p == 3: f = 0.7
			if p == 4: f = 0.8
			if p > 4: f = 1.0
		return f
	
	def updateFeelWins(self, feel, w):
		wins = self.wins()
		field = feel
		if self.preflop:
			if wins > 0.5: 
				field *= 1.3
			if wins > 0.3:
				field *= 1.1
		else:
			field = wins
			
		return self.normal(feel, w, self.wins())
	
	def updateFeelPotOdds(self, feel, w):
		field = feel + (self.wins() - self.potodds)
		
		if self.potodds == 0.0: 
			field = feel
		elif self.preflop and self.potodds > 0.2: 
			field *= 0.4
		elif self.potodds > 0.2 and field < 0.6: 
			field *= 0.5
		
		return self.normal(feel,w,field)
	
	def updateFeelOpponentCards(self, feel, w):
		field = feel
		required_observations = 20
		estimate = self.modeller.getEstOpponentCardPowers()
		
		other_hands = []
		for player_id in estimate:
			if player_id != self.player.getPlayerNumber():
				possible_power = estimate[player_id][0]
				observations = estimate[player_id][1]
			
				if observations > required_observations-1:
					if possible_power > self.player.hand().power()[0]:
						field *= 0.8
		
		return self.normal(feel,w,field)
	
	def updateFeelBluff(self, feel, w):
		if w > random.random() and not self.preflop:
			if config['debug']:
				print str(self.player), "is bluffing!"
			
			feel = feel * 2.0
			if feel > 1.0: feel = 1.0
		return feel
	
	def normal(self, feel, w, field):
		return feel*(1-w) + w*field
	
	
	#####################################################################
	# Common functions
	
	# converts a feel value to the desired action
	def feel_to_bet(self, feel):
	  if feel < 0.35: return 'F' # fold
	  if feel < 0.6: return self.toCall # call
	  if feel < 0.8: return self.toCall + (feel - 0.3) * self.chips # raise
	  return self.chips # all in
		
	# checks if final bet value is legal
	def bet(self, bet):
		if bet == 'F' and self.min_bet == 0: return 0
		if bet == 'F': return bet
		
		bet = int(bet)
		if bet < self.min_bet: return self.min_bet
		if bet > self.max_bet: return self.max_bet
		if bet > self.player.chips: return self.player.chips
		if bet < 0: return 0
		return bet
	
	# sets min and max bets
	def setEdgeBets(self):
		self.max_bet = self.player.chips
		self.min_bet = self.player.toCall()		
		if self.min_bet > self.player.chips: 
			self.min_bet = self.player.chips

		if self.max_bet < 0: self.max_bet = 0
		if self.min_bet < 0: self.min_bet = 0
	
	# sets different values based on the pot and how much the player has contributed
	def setVars(self):
		chips  	= self.chips 		= self.player.chips
		pot 	 	= self.pot 			= self.dealer.pot
		inPot  	= self.inPot 		= self.player.inPot
		toCall 	= self.toCall 	= self.player.toCall()
		preflop = self.preflop	= self.dealer.flop[0] == None
		
		if toCall == 0: self.potodds = 0.0
		else: self.potodds = float(toCall) / (float(pot) + float(toCall))
	
	# returns the power of the hand made by only tablecards
	def tableHandPower(self):
		if not self.dealer.tableCards(): return []
		return Hand(self.dealer.tableCards()).power()[0]
	
	# returns percentages from either preflop table or simulator
	def percentages(self):
		if len(self.dealer.tableCards()) == 0: 
			return self.simulationOffline()
		else: 
			return self.simulationOnline()
	
	def wins(self):
		if self.lastHandString == self.player.handString():
			return self.lastWins
		
		self.lastWins = self.percentages()[0]
		self.lastHandString = self.player.handString()
		return self.lastWins

	# runs online simulation and returns percentages
	def simulationOnline(self):
		return self.simulator.simulate(self.dealer.numberInRound(), self.player.holeCards, self.dealer.tableCards(), self.online_sims)

	# looks up holecards and playercount in preflop table, returns percentages
	def simulationOffline(self):
		return self.preFlopTable.ask(self.player.holeCards, self.dealer.numberInRound())
