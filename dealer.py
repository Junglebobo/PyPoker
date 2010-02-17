import random
from log import *
from humanPlayer import *
from computerPlayer import *
from deck import *
from hand import *
from conf import *
from opponentModeller import *


# Class handling the flow of the game. Dealing of cards, keeping score of pot, bettings, etc
class Dealer:

	#####################################################################
	# Setup methods
	
	def __init__(self):
		oppMod = OpponentModeller()
		self.log = Log(oppMod)
		self.deck = Deck()
		self.players = []
		self.names = []
		self.loadNames()
		
		self.reset()
	
	def reset(self):
		self.smallBlind = config['small_blind']
		self.bigBlind = config['big_blind']
		
		for player in self.players:
			player.chips = config['startChips']
			player.inGame = True
			player.inRound = True
			player.inPot = 0
			player.holeCards = [None, None]
			player.allIn = False	
		
		self.roundNum = 1
		self.currentBet = 0
		self.pot = 0
		self.raiser = None
		
		self.deck.reset()
		self.flop = [None, None, None]
		self.river = None
		self.turn = None
	
	def setBigBlind(self, blind):
		self.bigBlind = blind

	def setSmallBlind(self, blind):
		self.smallBlind = blind

	def loadNames(self):
		filename = "names.txt"
		self.names = []
		f = file(filename,'rb')
		for l in f.readlines(): self.names.append(l[0:-1])
		f.close()



	#####################################################################
	# Player methods

	def addPlayer(self, type, level=2, weights=[0.0,0.0,0.0,0.0]):
		i = str(len(self.players)+1)
		if type=="human":
			player = HumanPlayer("Player "+i, config['startChips'], len(self.players)+1, self)
		elif type=="computer":
			player = ComputerPlayer(self.randomName() + " (L" + str(level) + ", "+str(len(self.players)+1)+")", config['startChips'], len(self.players)+1, self, level, weights)	
		self.players.append(player)
		self.log.event("newplayer", player.getName())
	
	def randomName(self):
		p = random.randint(0,len(self.names)-1)
		return self.names.pop(p)
	
	def kickFromGame(self, player):
		if player.inGame:
			self.log.log(str(player)+" is out of chips, and leaves the game! (" + str(player.chips) + ")")
		player.inGame = False
		player.inRound = False
		player.inPot = 0
	
	def kickFromRound(self, player):
		#if player.inRound:
		#	self.log.log(str(player)+" is out of this round.")
		player.inRound = False
		player.inPot = 0
	
	def kickBrokePlayers(self):
		for player in self.inGame():
			if player.chips < 1:
				self.kickFromGame(player)
	
	def joinGame(self, player):
		player.inGame = True
		player.inRound = True
		player.allIn = False
		player.inPot = 0
		player.chips = config['startChips']
		self.log.log("* " + str(player)+" joined the game.")
	
	def joinRound(self, player):
		if player.chips < 1:
			self.kickFromGame(player)
			return
		if player.inGame:
			player.inRound = True
			player.inPot = 0
			player.allIn = False
			self.log.log("* " + str(player)+" joined the round.")
	
	def tableCards(self):
		if self.flop[0] == None: 	return []
		if self.river == None: 		return self.flop
		if self.turn == None: 		return self.flop + [self.river]
		return self.flop + [self.river, self.turn]
	
	def inRound(self):
		r = []
		for p in self.inGame():
			if p.inRound: r.append(p)
		return r
	
	def inGame(self):
		r = []
		for p in self.players:
			if p.inGame: r.append(p)
		return r
		
	def numberInGame(self):
		return len(self.inGame())
	
	def numberInRound(self):
		return len(self.inRound())
	
	def numberAllIns(self):
		a = []
		for p in self.inRound():
			if p.allIn: a.append(p)
		return len(a)
	
	def playerNumberInRound(self, player):
		i = 0
		for p in self.inRound():
			if p == player: return i
			i += 1
		return -1	
	
	def resetPlayers(self):
		for p in self.players:
			p.reset()
			p.chips = config['startChips']
			
		
	
	#####################################################################
	# Round methods

	def play(self, rounds = 1):		
		if not config['level_test']: print
		self.log.log("Game starts with "+str(self.numberInGame())+" players, max "+str(rounds)+" rounds.")
		if not config['level_test']: print "-" * 70
		for p in self.players:
			p.reset()
			self.joinGame(p)
		
		for i in range(1,rounds+1):
			if self.numberInGame() == 1: break
			self.playRound(i)
			self.kickBrokePlayers()
			if self.numberInGame() == 1: break
			wait = raw_input("\ncontinue...\n")
		
		self.log.event("endgame")
		return self.endGame()	
	
	def endGame(self):
		for p in self.inGame():
			if p.chips < 1:
				self.kickFromGame(p)
		
		if self.numberInGame() == 1:
			winner = self.inGame()[0]
		else:
			winners = self.inGame()
			winners.sort(self.sort_players)
			winner = winners[0]
		
		self.log.log(str(winner) + " won the game with " + str(winner.chips) + " chips. Congrats!")
		
		return winner
	
	def sort_players(self, p1, p2):
		if p1.chips > p2.chips: return -1
		if p2.chips < p2.chips: return 1
		return 0
		
	def playRound(self, round):
		if config['level_test']:
			print "* round", round
			
		self.roundNum = round
		
		dealer = (round % self.numberInGame()) - 1 # minus 1 to start dealing at player 1 (first player)
		
		if not config['level_test']: print
		self.log.event("newround", round)
		if not config['level_test']: print "-" * 70
				
		self.deck.reset() # refill with cards and shuffle
		self.pot = 0 # pot starts empty
		self.flop = [None, None, None] 
		self.river = None 
		self.turn = None 
		
		# deal hole cards
		for player in self.inGame():
			self.joinRound(player)
			cards = [self.deck.pop(), self.deck.pop()]
			player.setHoleCards(cards)
		if not config['level_test']: print
		self.log.log("Dealer is "+str(self.inRound()[dealer]))
		
		
		# betting round
		winner = self.takeBets(1, dealer)
		if winner != -1: 
			self.endRound([winner])
			return
		
		# deal flop
		cards = [self.deck.pop(), self.deck.pop(), self.deck.pop()]
		self.flop = cards
		self.log.event("flop", cards)

		# betting round
		winner = self.takeBets(2, dealer)
		if winner!=-1: 
			self.endRound([winner])
			return

		# deal river
		self.river = self.deck.pop()
		self.log.event("river", [self.river])

		# betting round
		winner = self.takeBets(3, dealer)
		if winner!=-1: 
			self.endRound([winner])
			return

		# deal turn
		self.turn = self.deck.pop()
		self.log.event("turn", [self.turn])

		# betting round
		winner = self.takeBets(4, dealer)
		if winner!=-1: 
			self.endRound([winner])
			return
		
		# two or more players still in the game, time for showdown
		hands = []
		for p in self.inRound():
			hand = Hand(p.getHoleCards()+self.flop+[self.river, self.turn])
			self.log.action(p, "showdown", [hand, p.getHoleCards()])
			hands.append(hand)
		hs = Hand.winner(hands)
		winners = []
		for h in hs:
			winners.append(self.inRound()[h])
		
		self.endRound(winners)

	def endRound(self, winners):
		if not config['level_test']: 
			print "\nRound ended with pot", self.pot
			print "-" * 70
			
		for p in winners:
			win = self.pot/len(winners)
			
			# if win > p.inPot:
			# 	win = p.inPot
			# 
			# # All in under limit?
			# for loser in self.inGame():
			# 	if loser not in winners:
			# 		if loser == p: continue
			# 		if loser.inPot > win:
			# 			loser.chips += loser.inPot - win
			
			player = p
			player.winChips(win)
			result = win
			if result >= 0:
				self.log.log(str(player)+" won "+str(win-player.inPot))
			else:
				self.log.log(str(player)+" lost "+str((win-player.inPot)*-1))
			
		if not config['level_test']: 
			print "Chips:"
			for p in self.inGame(): print "* " + str(p) + ": " + str(p.countChips())
		
		for p in self.inGame():
			p.inPot = 0
			p.allIn = False
			p.inRound = True
			if p.chips < 1:
				self.kickFromGame(p)
		
		self.pot = 0	



	#####################################################################
	# Betting methods		

	def addBet(self, player, amount):
		if amount > player.chips:
			amount = player.chips
			
		player.chips -= amount
		self.pot += amount
		player.inPot += amount

	def checkBet(self, bet, chips):
		if bet < 0: raise Exception("Negative bets not allowed!")
		if bet > chips: raise Exception("Can't bet more than you have!")

	def fold(self, player):
		self.log.action(player, "fold")
		self.kickFromRound(player)
	
	def takeBlinds(self, dealer):
		if self.numberInRound() == 1:
			return 0
		
		fp = self.nextPlayer(dealer)
		sp = self.nextPlayer(fp)
		
		# smallblind
		if fp.chips < 1: self.kickFromGame(fp)
		self.currentBet = self.smallBlind
		self.addBet(fp, self.smallBlind)
		self.log.event("smallblind", [fp, self.smallBlind])
		
		# bigblind
		if sp.chips < 1: self.kickFromGame(sp)
		self.currentBet = self.bigBlind
		self.addBet(sp, self.bigBlind)
		self.log.event("bigblind", [sp, self.bigBlind])
		
		return self.nextPlayer(sp)
	
	
	def takeBets(self, round, dealer):
		try:
			dealer = self.inRound()[dealer]
		except:
			dealer = self.inRound()[0]
			
		player = self.nextPlayer(dealer)
		self.raiser = None
		
		# blinds
		if round == 1:
			player = self.takeBlinds(dealer)
		
		# normal round
		self.count = 1
		nr = self.numberInRound()
		
		# ask players
		while nr > 1 and self.count <= nr:
			self.askPlayer(player)
			player = self.nextPlayer(player)
		
		print
		
		# Winner?
		if self.numberInRound() == 1: 
			return self.inRound()[0]
		else: 
			return -1
		
	def askPlayer(self, player):
		
		# Everybody else gone?
		if self.numberInRound() == 1:
			#print "1"
			self.count += 1
			return
		
		# Player is all in?
		if player.allIn:
			#print "2"
			self.count += 1
			return
		
		# This players raise called by all?
		if self.raiser == player:
			#print "3"
			self.raiser = None
			self.count += 11
			return
		
		# Get player bet
		bet = player.bet()
		
		if config['debug']:
			print
			print str(player.name) + " bets " + str(bet) + "/" + str(player.chips) + ". " + player.handString()
		
		# Set chip variables
		to_call = player.toCall()
		chips = player.chips
		
		# Fold
		if bet == "F" and player.inRound: 
			#print "4"
			self.fold(player)
			self.count += 1
			return
		
		# Player did not fold, bet should be an int
		bet = int(bet)
		self.checkBet(bet, chips) # legal?
		
		# All in?
		if bet < to_call or bet == chips:
			
			player.allIn = True
			
			# all in below limit
			if bet < to_call and player.inRound:
				#print "5"
				if bet < chips: raise Exception("Too low")
				self.addBet(player, chips)
				self.currentBet = to_call
				self.log.action(player, "call", bet)
				self.count += 1
				return
				
			# all in at limit
			if bet == to_call and player.inRound:
				#print "6"
				self.addBet(player, bet)
				self.currentBet = to_call + player.inPot
				self.log.action(player, "call", bet)
				self.count += 1
				return
			
			# all in above limit (raise)	
			if bet > to_call and player.inRound:
				#print "7"
				self.addBet(player, bet)
				self.currentBet = bet - to_call + self.currentBet
				self.log.action(player, "raise", [bet-to_call, bet])
				self.raiser = player
				self.count = 1 # restart round on raise
				return
		
		# Checks?
		if bet == to_call and player.inRound:
			#print "8"
			self.addBet(player, bet)
			self.log.action(player, "call", bet)
			self.currentBet = self.currentBet
			self.count += 1
			return
		
		# Raise?
		if bet > to_call and player.inRound:
			#print "9"
			self.addBet(player, bet)
			self.log.action(player, "raise", [bet - to_call, bet])
			self.currentBet = bet - to_call + self.currentBet
			self.raiser = player
			self.count = 1 # restart round on raise
			return
		
		
		# We should never come this far!
		raise Exception("Unhandled bet situation", bet)
		
	
	def nextPlayer(self, player):
		if not player.inRound: return self.nextPlayer(self.prevPlayer)
		else: self.prevPlayer = player
		number = self.playerNumberInRound(player)
		number += 1
		number %= self.numberInRound()
		return self.inRound()[number]


