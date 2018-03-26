#!/usr/bin/env python3

"""
Space Mining Poker

A game to illustrate game-theoretic components of commercial space
exploitation.
"""

def main(argv):
    if sys.version_info[0] < 3:
        print("Requires Python 3.")
        sys.exit(1)

    from players_rc import player_dict
    game = Game(player_dict)
    winner = game.run()
    if winner is None:
        game.broadcast("All players went bankrupt")
    else:
        game.broadcast("After {} rounds the winner is {} with a bankroll of {}.".format(game.round, winner.name, winner.bankroll))


if __name__ == "__main__":
   main(sys.argv[1:])
