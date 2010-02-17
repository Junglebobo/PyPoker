import random
from pokerPlayer import *
from preFlopTable import *
from simulator import *
from log import *
from strategy import *

class ComputerPlayer(PokerPlayer):
	
	def __init__(self, name, chips, num, dealer, level, weights):
		PokerPlayer.__init__(self, name, chips, num, dealer)
		self.online_sims = 100 # more takes time
		self.simulator = Simulator()
		self.preFlopTable = PreFlopTable()
		self.level = level
		self.weights = weights
		self.strategy = Strategy(self)
	
	def bet(self):
		if self.chips < 1: return self.chips # trivial all in case
		return self.strategy.decide(self.level, self.weights)

