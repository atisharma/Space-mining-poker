#!/usr/bin/env python3

"""
Space Mining Poker

A game to illustrate game-theoretic components of commercial space
exploitation.
"""

import sys
import getopt
import numpy

from strategies import *
from players import *


def run_game(player_dict):
    """
    Create a game instance and run the game.
    """

    game = Game(player_dict)

    round = 0
    while len(game.players) > 1:
        round += 1
        game.discovery()
        game.business()
        while True:
            game.auction()
            game.remove_bankrupt_players()
            if game.is_launching():
                game.broadcast('Someone is launching!')
                game.launch_race()
                break
        game.mission()
        game.broadcast(game.public_information)

    winner = game.players[0]
    game.broadcast(winner.name + " final bankroll after %d rounds: %d" % (round, winner.bankroll))


class Game(object):

    players = list()
    losers = list()
    public_information = dict()
    initial_bankroll = 1000
    initial_tech = 0
    base_price = 5
    base_tech = 11
    bid_tech = 11
    failure = 0.1
    failure_attenuation = 0.98

    def __init__(self, players):
        """Initialize a new game with the given list of players."""
        for name, strategy in players.items():
            self.players.append(Player(strategy, name))
        self.public_information['last_winning_miner'] = ''
        self.public_information['last_winning_bid'] = 0
        self.public_information['last_winning_bidders'] = list()

    def remove_bankrupt_players(self):
        for player in self.players:
            if player.is_bankrupt():
                self.broadcast(player.name + ' is bankrupt.')
                self.losers.append(player)
        # can't remove from list while iterating it
        self.players = [p for p in self.players if not p.is_bankrupt()]

    def discovery(self):
        """
        Discovery phase:
            Discover the asteroid and publish some information.
        """
        self.asteroid = Asteroid()
        self.public_information['base_reward'] = self.asteroid.base_reward
        self.broadcast("-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*")
        self.broadcast("New asteroid discovered! Base reward is %d."
              % self.asteroid.base_reward)

    def business(self):
        """
        Business phase:
            Each player has to buy some tech.
        """
        for player in self.players:
            self.broadcast(player.name + " has %d money." % player.bankroll)
            tech = numpy.random.randint(self.base_tech)
            player.buy_tech(tech, self.base_price)

    def auction(self):
        """
        Auction phase:
            all players submit bid, winners take the tech.
        """
        bids = list()
        winners = list()

        for player in self.players:
            """ allow players to bid with public information """
            bid = player.bid(self.public_information)
            bids.append(int(bid))

        winning_bid = max(bids)

        for player in self.players:
            """ winning players awarded tech """
            if player.last_bid == winning_bid:
                tech = numpy.random.randint(self.bid_tech)
                player.buy_tech(tech, winning_bid)
                winners.append(player.name)

        self.public_information['last_winning_bid'] = winning_bid
        self.public_information['last_winning_bidders'] = winners

    def launch_race(self):
        """ one player launched, now see who joins """
        for player in self.players:
            player.launch(self.public_information)

    def mission(self):
        """
        Mission phase:
            Triggered when someone has declared a launch.
            Assign payoff to winner.
        """
        launchers = list()
        weights = list()
        for player in self.players:
            """
            Calculate total tech spend.
            Determine list of participants.
            """
            if player.launching is True:
                self.broadcast(player.name + " is launching.")
                launchers.append(player)
                weights.append(float(player.tech))

        disaster = Player(strategy=None, name="Mission failure")
        disaster.tech = self.failure * sum(weights)
        self.failure *= self.failure_attenuation    # reduce failure rate over time
        launchers.append(disaster)
        weights.append(float(disaster.tech))
        s = sum(weights)
        for ix, w in enumerate(weights):
            weights[ix] = w / s

        winner = numpy.random.choice(launchers, 1, p=weights)[0]

        payoff = self.asteroid.payoff(s)
        for participant in launchers:
            if participant is winner:
                participant.collect_payoff(payoff)
            else:
                participant.collect_payoff(0)

        self.public_information['last_winning_miner'] = winner.name
        self.broadcast(winner.name + " mines the asteroid for %d money!" % payoff)

    def is_launching(self):
        for player in self.players:
            if player.launching is True:
                return True
        return False

    def broadcast(self, message):
        """
        Abstraction allowing printing of game messages for each player.
        """
        print(message)
        for player in self.players:
            player.broadcast(message)


class Asteroid(object):

    def __init__(self):
        p0 = numpy.random.randint(17)
        self.base_reward = p0

    def payoff(self, tech_spend):
        """
        reward = P0 + Pu + Pt
        where P0, Pu are random ints from uniform distribution 0 <= n <= 10
            and Pt is a function of tech spent
        """
        pu = numpy.random.randint(14)
        pt = int(numpy.sqrt(max(0, 1.5 * tech_spend)))
        return self.base_reward + pu + pt


def main(argv):
    if sys.version_info[0] < 3:
        print("Requires Python 3.")
        sys.exit(1)

    player_dict = {
        'Ati' : 'localhost:49000',
        'Alex' : 'localhost:49001',
        'Cedric' : Terminal(),
        'SpongeBob' : SpongeBob(),
        'PassiveLauncher' : PassiveLauncher()
    }
    run_game(player_dict)


if __name__ == "__main__":
   main(sys.argv[1:])

