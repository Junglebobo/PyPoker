_card_value_names_ = [2,3,4,5,6,7,8,9,10,'jack','queen','king','ace']
_card_suits_ = {'S':'Spade','H':'Heart','C':'Club','D':'Diamond'} # A dictionary

class Card:

	def __init__(self, suit, value):
		self.value = value
		self.suit = suit
	
	# returns value name, 'king' etc
	def value_name(self):
		return _card_value_names_[self.value-2]
		
	# returns suit name, 'Heart' etc 
	def suit_name(self):
		return _card_suits_[self.suit]
	
	def is_jack(self): 	return self.value == 11
	def is_queen(self): return self.value == 12
	def is_king(self): 	return self.value == 13
	def is_ace(self): 	return self.value == 14
	
	# Check if two cards are equal. c1.equals(c2)
	def equals(self, card):
		return self.suit == card.suit and self.value == card.value
	
	# returns a copy of a card
	def copy(self):
		return Card(self.suit, self.value)
	
	# returns all suits a card can have
	@staticmethod
	def all_suits():
		return _card_suits_.keys()
	
	# returns all values a card can have
	@staticmethod
	def all_values():
		return range(2,15)
	
	# copy array of cards
	@staticmethod
	def copy_cards(cards):
		return [c.copy() for c in cards]

	# print card object
	def __str__(self):
		return self.suit + str(self.value)

