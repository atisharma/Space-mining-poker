#!/usr/bin/env python3

"""
Game class implementing the game logic and rules.
"""

import numpy

from strategies import *
from players import *


class Asteroid(object):

    def __init__(self):
        p0 = int(numpy.random.lognormal() * 7)
        self.base_reward = p0

    def payoff(self, tech_spend):
        """
        reward = P0 + Pu + Pt
        where P0, Pu are random ints from uniform distribution 0 <= n <= 10
        and Pt is a function of tech spent
        """
        pu = int(numpy.random.lognormal() * 7)
        pt = int(numpy.sqrt(max(0, 1.5 * tech_spend)))
        return self.base_reward + pu + pt


class Game(object):

    # game parameters ("static" constants, must be changed before instantiating a new Game)
    INITIAL_BANKROLL = 1000
    INITIAL_TECH = 0
    BASE_PRICE = 5
    BASE_TECH = 11
    AUCTION_TECH = 11
    FAILURE_RATE = 0.1
    FAILURE_RATE_ATTENUATION = 0.98
    LAUNCH_COST = 5

    players = list()
    losers = list()
    round = 0
    public_information = {      # populate keys just so we have a list of all of them, values added during game play
        'round': None,
        'players': None,
        'last_winning_bid': None,
        'last_winning_bidders': None,
        'auction_round': None,
        'last_winning_miner': None,
        'last_mining_payoff': None,
    }

    def __init__(self, players):
        """
        Initialize a new game with the given list of players.
        Remove players with unset strategies (absent network players).
        """
        for name, strategy in players.items():
            self.players.append(Player(strategy, name, self.INITIAL_BANKROLL, self.INITIAL_TECH))
        self.players = [p for p in self.players if p.strategy]
        self.public_information['last_winning_miner'] = ''
        self.public_information['last_winning_bid'] = 0
        self.public_information['last_winning_bidders'] = list()
        self.public_information['players'] = dict()
        for player in self.players:
            self.public_information['players'][player.name] = dict()

    def remove_bankrupt_players(self):
        self.report()
        for player in self.players:
            if player.is_bankrupt():
                self.broadcast(player.name + ' is bankrupt in round {}.'.format(self.round))
                self.losers.append(player)
                player.end(self.public_information)
        # can't remove from list while iterating it
        self.players = [p for p in self.players if not p.is_bankrupt()]

    def next_round(self):
        """Start the next round of the game."""
        self.round += 1
        self.public_information['round'] = self.round
        for player in self.players:
            player.next_round()

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
            tech = numpy.random.randint(self.BASE_TECH)
            player.buy_tech(tech, self.BASE_PRICE)

    def auction(self):
        """
        Auction phase:
            all players submit bid, winners take the tech.
        """
        bids = list()
        winners = list()

        self.report()
        for player in self.players:
            """ allow players to bid with public information """
            bid = player.bid(self.public_information)
            bids.append(bid)

        winning_bid = max(bids)

        for player in self.players:
            """ winning players awarded *same* tech each """
            tech = numpy.random.randint(self.AUCTION_TECH)
            if player.last_bid == winning_bid:
                player.buy_tech(tech, winning_bid)
                winners.append(player.name)

        self.public_information['last_winning_bid'] = winning_bid
        self.public_information['last_winning_bidders'] = winners

    def launch_race(self):
        """ one player launched, now see who joins """
        self.report()
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
                player.bankroll -= self.LAUNCH_COST

        disaster = Player(strategy=None, name="Mission failure")
        disaster.tech = self.FAILURE_RATE_ATTENUATION**self.round * self.FAILURE_RATE * sum(weights)
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
        self.public_information['last_mining_payoff'] = payoff
        self.broadcast(winner.name + " mines the asteroid for %d money!" % payoff)

    def is_launching(self):
        for player in self.players:
            if player.launching is True:
                return True
        return False

    def report(self):
        """
        Populate public_information with what players should know.
        """
        for player in self.players:
            self.public_information['players'][player.name]['bankroll'] = player.bankroll

    def broadcast(self, message):
        """
        Abstraction allowing printing of game messages for each player.
        """
        print(message)
        for player in self.players:
            player.broadcast(message)

    def run(self, max_rounds=200):
        """
        Run the game and return the surviving (winning) players.
        If positive, plays at most max_rounds rounds.
        """
        self.round = 0
        self.report()
        for player in self.players:
            player.begin(self.public_information)
        while len(self.players) > 1 and (max_rounds == 0 or self.round <= max_rounds):
            self.next_round()
            self.discovery()
            self.business()
            self.remove_bankrupt_players()
            if len(self.players) > 1:
                auction_round = 0
                while True:
                    auction_round += 1
                    self.public_information['auction_round'] = auction_round
                    self.auction()
                    self.remove_bankrupt_players()
                    if self.is_launching():
                        self.launch_race()
                        break
                self.public_information['auction_round'] = None
                self.mission()
        self.report()
        for player in self.players:
            player.end(self.public_information)

        return self.players


    def show_statistics(self):
        """
        Print some statistics after a game
        """
        pass
