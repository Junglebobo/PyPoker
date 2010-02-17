#######################################################################
# 
#	Poker.py
# 
# Poker program for hosting and playing poker games.
# See conf.py for configuration settings.
# 
# To play against the bot, set 'level_test' to False.
# To see which strategies the computer players can
# use, see strategies.py.
# 
#######################################################################

from dealer import *
from conf import *


if not config['level_test']:
	
	for i in range(0,1):
		d = Dealer()
		#d.addPlayer("human",0)
		
		d.addPlayer("human", 3, [])
		
		d.addPlayer("computer", 6, [0.4, 0.35, 0.2, 0.05])
		d.addPlayer("computer", 6, [0.2, 0.5, 0.15, 0.15])
		d.addPlayer("computer", 6, [0.4, 0.4, 0, 0.2])
		
		# d.addPlayer("computer", 0)
		# d.addPlayer("computer", 0)
		# d.addPlayer("computer", 0)
		
		d.play(20)


else:
	
	#####################################################################
	# Test cases
	
	# Phase 1 tests
	if config['test_run'] == 1:
		add = [
			["computer",0,[]],
			["computer",1,[]],
			["computer",2,[]],
			["computer",2,[]]
		]
		strats = [
			"Random",
			"Always call",
			"Hand power",
			"Hand power"
		]
	
	# Phase 2 tests
	if config['test_run'] == 2:
		add = [
			["computer",3,[]],
			["computer",3,[]],
			["computer",4,[]],
			["computer",4,[]]
		]
		strats = [
			"Hand power",
			"Hand power",
			"Hand power + simulations",
			"Hand power + simulations"
		]
	
	# Phase 3 tests
	if config['test_run'] == 3:
		add = [
			["computer",3,[]],
			["computer",4,[]],
			["computer",5,[0.4, 0.4, 0.2, 0.0]],
			["computer",6,[0.5, 0.3, 0.1, 0.1]]
		]
		strats = [
			"Hand power",
			"Hand power + simulation",
			"All but bluff",
			"All with bluff"
		]
	
	
	#####################################################################
	# Test Case Simulation
	
	d = Dealer()
	for p in add:
		d.addPlayer(p[0], p[1], p[2])
	
	i = 0
	game = 1
	rounds = config['test_rounds']
	winners = []
	while(i < rounds+1):
		
		print "Game",game, "(" + str(i) + " rounds so far)"
		d.reset()
		random.shuffle(d.players)
		winner = d.play(10)
		
		print "Game " + str(game) + " won by player " + str(winner.getPlayerNumber()) + " after " + str(d.roundNum) + " rounds."
		print
		winners.append(winner.getPlayerNumber())
		i += d.roundNum
		game += 1
	
	print winners
	total = [0] * len(add)
	for l in winners: total[l-1] += 1
	print
	print "Total wins:"
	
	i = 1
	for t in total:
		print "* Player " + str(i) + " (Strat: "+ str(strats[i-1]) +"): " + str(t)
		i += 1
	