#!/usr/bin/env python3
import numpy


def run_game(player_dict=None):
    if player_dict is None:
        player_dict = {
            'Ati': Human,
            'Alex': Human,
            'Cedric': Human
        }
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
                print('Someone is launching!')
                game.launch_race()
                break
        game.mission()
        print(game.public_information)

    winner = game.players[0]
    print(winner.name + " final bankroll after %d rounds: %d" % (round, winner.bankroll))


class Game(object):

    players = list()
    losers = list()
    public_information = dict()
    initial_bankroll = 1000
    base_price = 5
    base_tech = 11
    bid_tech = 11
    failure = 0.1
    failure_attenuation = 0.98

    def __init__(self, players):
        for name, kind in players.items():
            self.add_player(name, kind)

    def add_player(self, name, strategy):
        player = Player(strategy=strategy(), name=name, bankroll=self.initial_bankroll)
        self.players.append(player)

    def remove_bankrupt_players(self):
        for player in self.players:
            if player.is_bankrupt():
                print(player.name + ' is bankrupt.')
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
        print("-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*")
        print("New asteroid discovered! Base reward is %d."
              % self.asteroid.base_reward)

    def business(self):
        """
        Business phase:
            Each player has to buy some tech.
        """
        for player in self.players:
            print(player.name + " has %d money." % player.bankroll)
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
            #player.display()
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
                print(player.name + " is launching.")
                launchers.append(player)
                weights.append(float(player.tech))

        disaster = Player(name="Mission failure")
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
        print(winner.name + " mines the asteroid for %d money!" % payoff)

    def is_launching(self):
        for player in self.players:
            if player.launching is True:
                return True
        return False


class Strategy:

    def bid(self, public_information):
        raise Exception("you need to implement a bid strategy!")

    def join_launch(self, public_information):
        raise Exception("you need to implement a launch strategy!")


class Player(object):

    def __init__(self, strategy=Strategy(), name=None, bankroll=1000, tech=0):
        self.strategy = strategy
        self.bankroll = bankroll
        self.tech = tech
        self.name = name
        self.launching = False
        self.last_bid = 0
        strategy.name = name

    def buy_tech(self, tech, price):
        self.tech += tech
        self.bankroll -= price

    def bid(self, public_information):
        self.share_state()
        bid, launching = self.strategy.bid(public_information)
        self.launching = launching
        self.last_bid = int(bid)
        return bid

    def launch(self, public_information):
        if self.launching is False:
            self.share_state()
            self.launching = self.strategy.join_launch(public_information)

    def collect_payoff(self, payoff):
        self.tech = 0
        self.bankroll += payoff

    def is_bankrupt(self):
        return self.bankroll < 0

    def share_state(self):
        # share private player state with strategy object
        self.strategy.tech = self.tech
        self.strategy.bankroll = self.bankroll

    def display(self):
        print(" - - - - - - - - - - -")
        print("name: " + self.name)
        print("tech: %d" % self.tech)
        print("bankroll: %d" % self.bankroll)
        print("last_bid: %d" % self.last_bid)
        print("launching: %r" % self.launching)
        print(" - - - - - - - - - - -")


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


class Human(Strategy):
    """Human strategy always asks for input"""

    def bid(self, public_information):
        print('-------------')
        print(self.name + " up.")
        print(public_information)
        print("Your tech: %d" % self.tech)
        print("Your money: %d" % self.bankroll)
        amount = input("Enter bid: ")
        if not amount.isnumeric():
            amount = 0
        launch = input("Launch? (Y/N) ")
        if launch[0].upper() == 'Y':
            launching = True
        else:
            launching = False
        return int(amount), launching

    def join_launch(self, public_information):
        print('-------------')
        print(self.name + " up.")
        print(public_information)
        print("Your tech: %d" % self.tech)
        print("Your money: %d" % self.bankroll)
        launch = input("Join launch? (Y/N) ")
        if launch[0].upper() == 'Y':
            return True
        else:
            return False


class Spongebob(Strategy):
    """Spongebob always bids and launches based on fixed threshold."""

    def bid(self, public_information):
        amount = min(self.bankroll, public_information['base_reward'])
        launching = self.tech>10
        return int(amount), launching

    def join_launch(self, public_information):
        return self.tech>15
