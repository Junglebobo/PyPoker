import string
from pokerPlayer import *

class HumanPlayer(PokerPlayer):

	def __init__(self, name, chips, num, dealer):
		PokerPlayer.__init__(self, name, chips, num, dealer)
		name = raw_input("Your name please: ")
		print # extra newline
		self.name = name
	
	def bet(self, override=False):
		# if all in, check if you can
		if self.toCall() == 0 and self.chips < 1: return 0
		
		string  = "\n"
		string += "  *** Time to bet ***\n"
		string += "  Holecards: " + str(self.holeCards[0]) + ", " + str(self.holeCards[1]) + "\n"
		string += "  Tablecards: " +  str([str(card) for card in self.dealer.tableCards()]) + "\n"
		string += "  " + str(self.handString()) + "\n"
		string += "  Chips: " + str(self.chips) + "\n\n"
		string += "  Pot: " + str(self.dealer.pot) + "\n"
		string += "  Current bet: " + str(self.dealer.currentBet) + "\n\n"
		string += "  You have in pot: " + str(self.inPot) + "\n"
		string += "  Required chips to play: " + str(self.toCall()) + "\n\n"
		string += "  What do you want to do? [f(old), c(all), int (# chips)]: \n  "
		
		if not override:	choice = raw_input(string).upper()
		else:							choice = raw_input(override).upper()
		
		if not choice: 
			choice = self.bet("  I couldn't hear that. Again please: \n  ")
		
		# if choice != "F" and choice != "C":
		# 	try:
		# 		a = int(source)
		# 	except:
		# 		choice = self.bet("  What? Again please: \n  ")
		
		if choice != "C" and choice != "F":
			if int(choice) < self.toCall() and self.chips >= self.toCall():
				choice = self.bet("\n  You can't bet under the limit if you have enough!\n  New amount please: \n  ")
			if int(choice) > self.chips:
				choice = self.bet("\n  You can't bet more than you have!\n  New amount please: \n  ")
		
		if choice == "C": 
			if self.chips > self.toCall():
				choice = str(self.toCall())
			else:
				choice = str(self.chips)
				
		print # extra newline
		return choice
