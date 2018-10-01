#!/usr/bin/env python3

"""
Space Mining Poker

A game to illustrate game-theoretic components of commercial space
exploitation.
"""

import sys
from game import Game

def main(argv):
    if sys.version_info[0] < 3:
        print("Requires Python 3.")
        sys.exit(1)

    from players_rc import player_dict
    game = Game(player_dict)
    winners = game.run()
    if len(winners) == 0:
        game.broadcast("All players went bankrupt")
    else:
        top = winners[0]
        for winner in winners:
            game.broadcast("After {} rounds player {} has a bankroll of {}.".format(game.round, winner.name, winner.bankroll))
            if winner.bankroll > top.bankroll: top = winner
        game.broadcast("Top player at end of game: {}".format(top.name))

if __name__ == "__main__":
   main(sys.argv[1:])
