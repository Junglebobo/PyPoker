from card import *
from deck import *
from operator import itemgetter

_hand_power_names_ = {1:'High card', 2:'One pair', 3:'Two pair', 4:'Three of a kind', 
	5:'Straight', 6:'Flush', 7:'Full house', 8:'Four of a kind', 9:'Straight flush'}

class Hand:
	
	def __init__(self, cards):
		if len(cards) < 2 or len(cards) > 7:
			raise Exception('Too few or too many cards in hand', cards)
		self.cards = cards

	# This is the most important function in this file.  It takes a set of cards and computes
	# their power rating, which is a list of integers, the first of which indicates the type of
	# hand: 9 - straight flush, 8 - 4 of a kind, 7 - full house, 6 - flush, 5 - straight, 4 - 3 of  kind
	# 3 - two pair, 2 - one pair, 1 - high card.  The remaining integers are tie-breaker information
	# required in cases where, for example, two players both have a full house.
	def power(self, target_len = 5):
		def has_len (length, items): return length == len(items)
		
		vgroups = self.gen_value_groups()
		flush = self.find_flush(self.cards, target_len = target_len)
		if flush:
			str_in_flush = self.find_straight(flush)
		if flush and str_in_flush:
			return self.calc_straight_flush_power(str_in_flush)
		elif has_len(4, vgroups[0]):
			return self.calc_4_kind_power(vgroups)
		elif has_len(3, vgroups[0]) and len(vgroups) > 1 and has_len(2,vgroups[1]):
			return self.calc_full_house_power(vgroups)
		elif flush:
			return self.calc_simple_flush_power(flush)
		else:
			straight = self.find_straight(self.cards)
			if straight:
				return self.calc_straight_power(straight)
			elif has_len(3,vgroups[0]):
				return self.calc_3_kind_power(vgroups)
			elif has_len(2,vgroups[0]):
				if len(vgroups) > 1 and has_len(2,vgroups[1]):
					return self.calc_2_pair_power(vgroups)
				else: return self.calc_pair_power(vgroups)
			else: return self.calc_high_card_power(self.cards)

	# Group a set of cards by value
	def gen_value_groups(self):
		new_cards = Card.copy_cards(self.cards)
		return self.sorted_partition(new_cards,elem_prop = (lambda c: c.value))
	
	def card_value(self, card):
		return card.value
		
	def card_suit(self, card):
		return card.suit
	
	# This partitions elements and then sorts the groups by the subset_prop function, which defaults to group size.
	# Thus, using the defaults, the largest groups would be at the beginning of the sorted partition.
	def sorted_partition(self, elems,elem_prop = (lambda x:x), subset_prop = (lambda ss: len(ss)), eq_func = (lambda x,y: x ==y), dir = "decrease"):
		p = self.partition(elems,prop_func = elem_prop, eq_func = eq_func)
		self.kd_sort(p,prop_func = subset_prop,dir = dir)
		return p
	
	def sort_cards(self, cards, prop_func = (lambda c: c.value), dir = 'decrease'):
		self.kd_sort(cards,prop_func=prop_func,dir=dir)

	# Group a set of cards by suit
	def gen_suit_groups(self):
		new_cards = Card.copy_cards(self.cards)
		return self.sorted_partition(new_cards,elem_prop = (lambda c: c.suit))
	
	# Sort a set of cards in ascending or descending order, based on the card value (e.g. 3,7,queen,ace, etc.)
	def gen_ordered_cards(self, cards, dir = 'increase'):
		new_cards = Card.copy_cards(cards)
		self.kd_sort(new_cards,prop_func=(lambda c: c.value),dir = dir)
		return new_cards
	
	# This groups a set of elements by shared values of a specified property (which is determined by
	# prop_func), where the equality of two values is determined by eq_func.  For example, this might
	# be used to group a set of cards by card-value.  Then all the 5's would be returned as one group, all
	# the queens as another, etc.
	def partition(self, elems, prop_func = (lambda x:x), eq_func = (lambda x,y: x == y)):
		self.kd_sort(elems,prop_func=prop_func)
		partition = []
		subset = False
		last_key = False
		counter = 0
		for elem in elems:
			new_key = apply(prop_func, [elem])
			if not(subset) or not(apply(eq_func,[last_key,new_key])):
				if subset: partition.append(subset)
				subset = [elem]
				last_key = new_key
			else: subset.append(elem)
		if subset: partition.append(subset)
		return partition
	
	def find_list_item(self,L,item,key=(lambda x: x)):
		for x in L:
			if item == key(x):
				return x

	def kd_sort(self, elems, prop_func = (lambda x: x), dir = 'increase'):
		elems.sort(key=prop_func) # default of the sort func is increasing order
		if dir =='decrease' or dir =='decr':
			elems.reverse()	

	# Functions for finding flushes and straights in a set of cards (of any length)
	def find_flush(self, cards, target_len = 5):
	  sgroups = self.gen_suit_groups()
	  if len(sgroups[0]) >= target_len:
			return sgroups[0]
	  else: return False

	def find_straight(self, cards, target_len = 5):
		ace = self.find_list_item(cards,14,key=(lambda c: c.value))
		scards = self.gen_ordered_cards(cards, dir = 'decrease')

		def scan(cards, straight):
			if len(straight) == target_len:
				return straight
			elif ace and 2 == straight[0].value and len(straight) == target_len - 1:
				return [ace] + straight
			elif not(cards):
				return False # null check is late since variable 'cards not involved in 1st 2 cases

			c = cards.pop(0)
			if c.value == straight[0].value - 1:
				return scan(cards,[c] + straight)
			elif c.value == straight[0].value:
				return scan(cards,straight)
			else: # Broken straight, so start again with the current card
				return scan(cards,[c])

		top_card = scards.pop(0)
		return scan(scards,[top_card])
	
	# Simple auxiliary function for finding and sorting all card values in a set of card groups, and then returning
	# the largest 'count of them.
	def max_group_vals(self, groups, count):
		vals = [g[0].value for g in groups]
		self.kd_sort(vals,dir='decrease')
		return vals[0:count]
  
	# Straights are presumably sorted in ASCENDING order
	def calc_straight_flush_power(self, straight):
		return [9,straight[-1].value]

	def calc_4_kind_power(self, value_groups):
		return [8,value_groups[0][0].value]

	def calc_full_house_power(self, value_groups):
		return [7] + [vg[0].value for vg in value_groups[0:2]]

	def calc_simple_flush_power(self, flush, target_len = 5):
	  new_flush = Card.copy_cards(flush)
	  self.sort_cards(new_flush)
	  return [6] + [c.value for c in new_flush[0:target_len]]

	def calc_straight_power(self, straight):
		return [5, straight[-1].value]

	def calc_3_kind_power(self, value_groups):
		return [4, value_groups[0][0].value] # Assuming a standard 52-card deck, no other tie-breaker data is needed.

	def calc_2_pair_power(self, value_groups):
		return [3, value_groups[0][0].value, value_groups[1][0].value] + self.max_group_vals(value_groups[2:],1)

	def calc_pair_power(self, value_groups):
		return [2,value_groups[0][0].value] + self.max_group_vals(value_groups[1:],3)

	def calc_high_card_power(self, cards):
		ocards = self.gen_ordered_cards(cards,dir='decrease')
		return [1] + [c.value for c in ocards][0:5]

	def power_name(self):
		return _hand_power_names_[self.power()[0]]
	
	def __str__(self):
		return str([str(card) for card in self.cards])+" ("+str(self.power_name())+")"
	
	@staticmethod
	def pad_array(array, length):
		if len(array) >= length: return array
		for _ in range(0,(length-len(array))): array.append(0)
		return array
	
	@staticmethod
	def compare_two_hands(h1,h2): 
		p1 = h1.power()
		p2 = h2.power()
		p1 = Hand.pad_array(p1,6)
		p2 = Hand.pad_array(p2,6)
		return cmp(p2[0], p1[0]) or cmp(p2[1],p1[1]) or cmp(p2[2],p1[2]) or cmp(p2[3],p1[3]) or cmp(p2[4],p1[4]) or cmp(p2[5],p1[5])

	@staticmethod
	def compare(hands):
		hands.sort(Hand.compare_two_hands)
		return hands[0]

	
	# Checks if two hands have the same power
	# 1: self wins
	# 0: equal hands (tie)
	# -1: hand2 wins
	def power_equals(self, hand2):
		return Hand.compare_two_hands(hand2, self)
		
	# Checks if two hands are the same hand
	def equals(self, hand2):
		if len(self.cards) != len(hand2.cards): return False
		for i in range(0, len(self.cards)):
			if not self.cards[i].equals(hand2.cards[i]):
				return False
		return True
	
	# Finds the winning hand in a set of hands. Returns the index of the winning hand,
	# or an array of indices for the winnings hands if the result is a tie.
	@staticmethod
	def winner(hands):
		original = hands[:] # copy array for later use
		hands.sort(Hand.compare_two_hands)
		
		if hands[0].power_equals(hands[1]) > 0:
			winner = hands[0]
			for i in range(0,len(original)):
				if winner.equals(original[i]):
					return [i]
		
		ties = []
		for i in range(0,len(hands)):
			if original[i].power_equals(hands[0]) == 0: 
				ties.append(i)
		return ties

