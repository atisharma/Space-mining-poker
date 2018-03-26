# Space Mining Poker

## Rules

The game is played with N players. Each player has M money and T tech. The M attribute is public, the T attribute is private.
Each player starts with M=1000 and T=0.

A game has many repeated rounds, over which each player tries to maximise their bankroll M. Each round of the game has various phases, as follows.

### 0) Discovery phase:
In this phase, the asteroid is found and analysed. The game assigns a fixed reward P0 (from some distribution DP) and an unknown reward Pu (same distribution).

### 1) Business phase:
In this phase, each player has to buy 1 random tech (drawn from some distribution DT) at a fixed price of 10.
Players who go bankrupt are removed from the game.

### 2) Auction phase:
In this phase, an auction is held for an unknown tech, which will be drawn from DT.

The rules of the auction are as follows. Each player submits a bid (blind of the others) for the new tech. The highest bidder is awarded the tech (adding to their total) and their bid is subtracted from their bankroll. In the case of a tie, the bid is awarded to both tied bids (both players buy the tech at that price). The tech awarded, the winning player and the winning bid are all announced at the point of the award.

Repeated auctions are held until one or more players announce that they will launch.

### 3) Mission phase:
This phase corresponds to the launch of a mission to mine the asteroid.
Once a player announces a launch, the race is on. Each player has the option to either compete in the launch or to sit it out. A player who sits out the launch preserves their tech total T for the next round and takes no further part in this round.
A player who joins the launch has a chance of mining the asteroid.
Launching players spend all their tech on the launch.
A winner is chosen for the round at random, where the Probability of a win for each player is

p(player n wins) = Tn / (sum(Ti) + F).

F plays the role of allowing the possibility of no winner where the asteroid is not successfully mined. F can be modelled to reduce over repeated games.

The payoff to the winning player for mining the asteroid is

payoff = P0 + Pu + Pt.
This is all made public information at this point.

Pt is an extraction efficiency reward which depends on the average tech spent by all players over past 10 rounds.


## How to play
At the moment, it is required to modify the player names and strategies in the `players_rc.py` file.
Network players use their network name/IP address and port as a string instead of a strategy, and will need
to separately run `strategy_server.py` with the port to use (or an offset to the base port 49000) as the
command line argument on their machine. Network players can set their strategy by editing
`strategy_server.py` accordingly.


## Possible extensions:
- Borrowing money at interest (payable per turn).
- Limit number of bidding rounds but reveal more information about asteroid in each round (similar to flop & river in poker).
