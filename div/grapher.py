wins = [4, 4, 2, 3, 3, 4, 3, 1, 4, 4, 3, 4, 4, 3, 4, 2, 3, 3, 1, 4, 3, 2, 2, 3, 4, 1, 2, 1, 1, 3, 3, 2, 4, 1, 1, 2, 3, 3, 3, 4, 2, 4, 3, 2, 3, 3, 2, 2, 2, 3, 4, 2, 2, 3, 3, 2, 3, 2, 2, 1, 3, 3, 1, 1, 4, 2, 2, 3, 4, 2, 4, 1, 3, 2, 3, 1, 1, 1, 3, 2, 2, 4, 3, 4, 4, 4, 2, 4, 3, 3, 2, 2, 3, 3, 2, 2, 1, 3, 4, 4, 3, 1, 3]

# Total wins:
# * Player 1 (Strat: Hand power): 16
# * Player 2 (Strat: Hand power + simulation): 28
# * Player 3 (Strat: All but bluff): 35
# * Player 4 (Strat: All with bluff): 24

sums = {}
sums[1] = sums[2] = sums[3] = sums[4] = 0

for e in wins:
	sums[e] += 1
		
	for s in sums:
		print str(sums[s]) + "	",
	print
	
