from context import *

class Log:

	def __init__(self, opponentModeller):
		self.tableCards = []
		self.context = Context()
		self.modeller = opponentModeller

	# adds a textual entry to the log file and prints it to stdout
	def log(self, string):
		# TODO: print to file, or sumthin'
		if not config['level_test']: 
			print string
	
	# logs event and updates context
	def event(self, event, value = None):
		pass # newplayer, newround & nr
		if event=="newplayer":
			self.log("New player '"+str(value)+"' joins the table")
			
		elif event=="newround":
			self.log("Round "+str(value)+" starts")
			self.context.update('potSize', 0)
			self.context.update('currentBet', 0)
			self.tableCards = []
			self.modeller.clear()
			
		elif event=="flop" or event=="river" or event=="turn":
			msg = "Card"
			if len(value)>1: msg += "s"
			msg += " delt to "+event+": "
			for card in value: msg += str(card)+" "
			self.log(msg)
			self.tableCards += value
			
		elif event=="smallblind":
			self.log(str(value[0])+" bets small blind and puts "+str(value[1])+" into the pot")
			self.context.inc('potSize', int(value[1]))
			
		elif event=="bigblind":
			self.log(str(value[0])+" bets big blind and puts "+str(value[1])+" into the pot")
			self.context.update('currentBet', int(value[1]))
			self.context.inc('potSize', int(value[1]))

		elif event=="endgame":
			self.log("Game ended")
			self.modeller.clear()
			if config['print_opponent_models']: self.modeller.printStats()
		
	# logs action and tells oponent modeller about action, context pair
	def action(self, player, action, value = None):
		if action=="fold":
			self.modeller.tell(player, self.context.getCode(), action, self.tableCards)
			self.log(str(player)+" folds and is out of the round ("+self.context.getCode()+")")
		elif action=="raise":
			self.modeller.tell(player, self.context.getCode(), action, self.tableCards)
			
			if player.chips > 0:
				self.log(str(player)+" raises bet by "+str(value[0])+" and puts "+str(value[1])+" into the pot ("+self.context.getCode()+")")
			else:
				self.log(str(player)+" goes all in with "+str(value[1])+" and raises the bet by "+str(value[0])+" ("+self.context.getCode()+")")
				
			
			self.context.inc('numRaises', 1)
			self.context.inc('currentBet', value[0])
			self.context.inc('potSize', value[1])
		elif action=="call":
			if value==0:
				self.log(str(player)+" checks ("+self.context.getCode()+")")
			elif player.chips == 0:
				self.log(str(player)+" goes all in and puts "+str(value)+" into the pot ("+self.context.getCode()+")")
			else:
				self.log(str(player)+" calls and puts "+str(value)+" into the pot ("+self.context.getCode()+")")
			self.modeller.tell(player, self.context.getCode(), action, self.tableCards)
			self.context.inc('potSize', value)
		elif action=="showdown":
			self.modeller.showdown(player, value[1])
			self.log(str(player)+" have the hand "+str(value[0]));

