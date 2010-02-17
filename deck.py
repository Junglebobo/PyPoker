import random
from card import *

class Deck:
	
	def __init__(self):
		self.cards = []
		self.generate_cards()
		self.original = self.cards[:]
		self.shuffle()
	
	# create new cards in the deck and shuffle
	def reset(self):
		self.cards = self.original[:]
		self.shuffle()
		
	# 52 new cards, sorted
	def generate_cards(self):
		self.cards = []
		for suit in Card.all_suits():
				for value in Card.all_values():
						self.cards.append(Card(suit,value))
	
	# randomized shuffle, one time
	def shuffle(self):
		random.shuffle(self.cards)
	
	# removes and returns top card in deck
	def pop(self):
		return self.cards.pop(0)
	
	# print deck object
	def __str__(self):
		return str([str(card) for card in self.cards])
	
	# removes and returns card by suit, value
	def remove_card(self, suit, value):
		for i in range(0,len(self.cards)):
			c = self.cards[i]
			if c.suit == suit and c.value == value:
				return self.cards.pop(i)

