from conf import *

class Context:

	# Context contstants
	LOW = FEW = SMALL = 0
	HIGH = MANY = BIG = 1
	
	# create new context with default values
	def __init__(self, fields = {}):
		# Detailed information about the current context
		self.detailed = {'numRaises':0, # number of rises in this round
					'potSize':0, # number of chips in the pot
					'currentBet':0}
				
		self.context = {'numRaises':0,
					'potSize':0,
					'currentBet':0}
		for key, value in fields.iteritems():
			self.update(key, value)

	# return a code identifying the context
	def getCode(self):
		code = "C"
		for _,val in self.context.iteritems():
			code += str(val)
		return code

	def get(self, key):
		return self.detailed[key]

	# set a new value to field
	# ex: context.update("pot", 0) when starting new round
	def update(self, key, value):
		# TODO: whine if unknown key is given
		self.detailed[key] = value
		self.updateContext()		
		
	# increment field by value
	# ex: context.inc("bet", 100) when player raises by 100
	def inc(self, key, value):
		# TODO: whine if unknown key is given
		self.detailed[key] += value
		self.updateContext()

	def updateContext(self):
		if self.detailed['numRaises'] > config['context_raises_threshold']:
			self.context['numRaises'] = self.MANY
		else:
			self.context['numRaises'] = self.FEW
			
		if self.detailed['potSize'] > config['context_pot_threshold']:
			self.context['potSize'] = self.BIG
		else:
			self.context['potSize'] =  self.SMALL
			
		if self.detailed['currentBet'] > config['context_bet_threshold']:
			self.context['currentBet'] = self.HIGH
		else:
			self.context['currentBet'] = self.LOW
