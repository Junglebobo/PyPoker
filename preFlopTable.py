import pickle
from card import *
from simulator import *

class PreFlopTable:
	
	def __init__(self):
		self.filename = 'preFlopTable.txt'
		self.simulator = Simulator()
		#self.populate_table() # Takes time!
		self.load_table_from_file()
	
	# Ask table for entry with holecards and number of players
	# returns [wins ties losses] in percentages
	def ask(self, holecards, players):
		# ask a dictionary, where the key is: "lowcardvalue.highcardvalue"
		# => gets a dict with keys 'suited' and 'unsuited'
		# => then gets an array with 9 values (2 to 10 players)
		
		c1 = holecards[0]
		c2 = holecards[1]
		v1 = c1.value
		v2 = c2.value
		s1 = c1.suit
		s2 = c2.suit
		
		if v1 < v2: value_key = str(v1) +'.'+ str(v2)
		else: value_key = str(v2) +'.'+ str(v1)
		
		if s1 == s2: suit_key = 'suited'
		else: suit_key = 'unsuited'
		
		players_index = players-2 # array index
		
		return self.table[value_key][suit_key][players_index]
		
	# Populate preflop table with results and save results to file
	def populate_table(self):
		min_players = 2 # 2
		max_players = 10 # 10
		simulations_per_case = 1
		
		self.table = {}
		
		for x in range(2,15): # card value 1
			for y in range(2,15): # card value 2
				if x > y: key = str(y) + '.' + str(x)
				else:     key = str(x) + '.' + str(y)
				
				if not key in self.table: # ignore equal cases
					print "Simulating", key
					
					self.table[key] = {}
					cards = {}
					cards['suited']   = [Card('S',x),Card('S',y)] 
					cards['unsuited'] = [Card('H',x),Card('D',y)] # random suits perhaps?
					
					for suit_status in ['suited','unsuited']:
						players = []
						for number_of_players in range(min_players, max_players+1):
							#print "Simulating:", key, suit_status, "-", number_of_players, "players"
							players.append(self.simulator.do_simulation(number_of_players, cards[suit_status], [], simulations_per_case))
						self.table[key][suit_status] = players[:]
						
		self.save_table_to_file()
	
	# Pickle self.table, save to preFlopTable.txt
	def save_table_to_file(self):
		try:
			file = open(self.filename, 'w')
			pickle.dump(self.table, file)
			file.close()
		except Exception:
			raise Exception('preFlopTable.txt file missing. Please create it!')

	# Unpickle self.table from preFlopTable.txt
	def load_table_from_file(self):
		try:
			file = open(self.filename, 'r')
			self.table = pickle.load(file)
			file.close()
		except Exception: 
			raise Exception('preFlopTable.txt file missing. Run simulation first!')


# pft = PreFlopTable()
# #pft.populate_table()
# #print pft.table
# print pft.ask([Card('H',2),Card('S',7)], 10)
