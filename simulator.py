from deck import *
from hand import *
from decimal import *

class Simulator:
	
	def __init__(self):
		self.deck = Deck()
	
	def simulate(self, players, holecards, tablecards = [], simulations = 100):
		return self.do_simulation(players, holecards, tablecards, simulations)
	
	# returns percentages of results of simulations 
	# [wins, ties, losses]
	def do_simulation(self, players, holecards, tablecards = [], simulations = 100):
		if players < 2 or len(holecards) != 2 or len(tablecards) > 5 or simulations < 1:
			raise Exception("Bad input to simulator!")

		wins,ties,losses = 0,0,0
		
		for i in range(0,simulations):
			self.deck.reset()
			holes = [[self.deck.pop(), self.deck.pop()] for _ in range(1, players)]
			holes.append(holecards)
			community_cards = [self.deck.pop() for _ in range(0,5)]
			
			original_hand = community_cards[:]
			original_hand.extend(holecards)
			original_hand = Hand(original_hand)
			
			hands = []
			for pair in holes:
				cards = community_cards[:]
				cards.extend(pair)
				hand = Hand(cards)
				hands.append(hand)
				cards = []
			
			winner = Hand.winner(hands[:])
			if len(winner) == 1:
				if hands[winner[0]].equals(original_hand): wins += 1
				else: losses += 1
			else: ties += 1
		
		# percentages in floats
		sf = float(simulations)
		wins_p 		= float(wins) / sf
		ties_p 		= float(ties) / sf
		losses_p 	= float(losses) / sf
		
		# TODO: Find poker numbers to check the accuracy!
		return [wins_p, ties_p, losses_p]
