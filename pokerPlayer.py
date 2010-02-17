# Parent class for all poker players. PokerAgent, HumanPlayer, etc should extend this class
from hand import *

class PokerPlayer:

	def __init__(self, name, chips, num, dealer):
		self.reset()
		self.name = name
		self.chips = chips
		self.num = num
		self.dealer = dealer

	def __str__(self):
		return self.name
	
	def reset(self):
		self.holeCards = [None, None]
		self.active = True
		self.inRound = True
		self.inGame = True
		self.inPot = 0
		self.allIn = False
		self.chips = 0
	
	def setHoleCards(self, cards):
		self.holeCards = cards

	def getHoleCards(self):
		return self.holeCards
	
	def getPlayerNumber(self):
		return self.num
	
	def betChips(self, amount):
		self.chips -= amount
    
	def winChips(self, amount):
		self.chips += amount
	
	def countChips(self):
		return self.chips
	
	def getName(self):
		return self.name
		
	def highCard(self):
		v1 = self.holeCards[0].value
		v2 = self.holeCards[1].value
		if v1 > v2: return v1
		else: return v2
			
	def hand(self):
		if self.holeCards[0] == None:
			return None
		elif len(self.dealer.tableCards()) == 0:
			return Hand(self.holeCards)
		else:
			hand = self.holeCards[:]
			hand.extend(self.dealer.tableCards())
			return Hand(hand)
	
	def handString(self):
		if self.holeCards[0] == None:
			return ""
		elif len(self.dealer.tableCards()) == 0:
			return str([str(c) for c in self.holeCards])
		else:
			hand = self.holeCards[:]
			hand.extend(self.dealer.tableCards())
			return str(Hand(hand))
	
	def toCall(self):
		if self.dealer.currentBet > self.inPot:
			return self.dealer.currentBet - self.inPot
		else:
			return 0

 
	# Ask player what action to take in betting round
	# returns F (fold), C (call) or amount (raise)
	def bet(self):
		return "F"
