import numpy


def run_game():
    player_dict = {
        'Ati': Human,
        'Alex': Human,
        'Cedric': Human
    }
    game = Game(player_dict)
    while len(game.players) > 1:
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


class Game(object):

    self.players = list()
    self.public_information = dict()
    self.base_price = 10
    self.failure = 0.1

    def __init__(self, players):
        for name, kind in players.items():
            self.add_player(name, kind)

    def add_player(self, name, kind):
        player = kind(name=name)
        self.players.append(player)

    def remove_bankrupt_players(self):
        for player in self.players:
            if player.is_bankrupt():
                print(player.name + ' is bankrupt.')
                self.players.remove(player)

    def discovery(self):
        """
        Discovery phase:
            Discover the asteroid and publish some information.
        """
        self.asteroid = Asteroid()
        self.public_information['base_reward'] = self.asteroid.base_reward

    def business(self):
        """
        Business phase:
            Each player has to buy some tech.
        """
        for player in self.players:
            player.buy_tech(self.base_price)

    def auction(self):
        """
        Auction phase:
            all players submit bid, winners take the tech.
        """
        bids = list()
        winners = list()

        for player in self.players:
            """ allow players to bid with public information """
            player.bid(self.public_information)
            bids.append(int(player.bid))

        winning_bid = max(bids)

        for player in self.players:
            """ winning players awarded tech """
            if player.bid == winning_bid:
                player.buy_tech(winning_bid)
                winners.append(player.name)

        self.public_information['last_winning_bid'] = winning_bid
        self.public_information['last_winning_players'] = winners

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
                launchers.append(player)
                weights.append(float(player.tech)

        disaster = Player()
        disaster.tech = self.failure * sum(weights)
        launchers.append(disaster)
        weights.append(float(disaster.tech)
        weights /= sum(weights)

        winner = numpy.random.choice(launchers, 1, p=weights)

        for participant in launchers:
            if participant is winner:
                winner.collect_payoff(self.asteroid.payoff(tech))
            else:
                winner.collect_payoff(0)

        self.public_information['last_winning_miner'] = winner.name

    def is_launching(self):
        for player in self.players:
            if player.launch is True:
                return True
        return False



class Player(object):

    def __init__(self, name=None, bankroll=1000, tech=0):
        self.bankroll = bankroll
        self.tech = tech
        self.name = name
        self.launching = False

    def buy_tech(self, price):
        tech = int(numpy.log10(numpy.randint(1001)))
        self.tech += tech
        self.bankroll -= price

    def bid(self, public_information):
        # insert bid and launch trigger logic here
        self.launch = True
        bid = 0
        return bid

    def launch(self, public_information):
        # decide whether to launch based on public information
        self.launching = True

    def collect_payoff(self, payoff):
        self.tech = 0
        self.bankroll += payoff

    def is_bankrupt(self):
        return self.bankroll < 0


class Asteroid(object):

    def __init__(self):
        p0 = numpy.random.randint(11)
        self.base_reward = p0

    def payoff(self, tech_spend):
        """
        reward = P0 + Pu + Pt
        where P0, Pu are random ints from uniform distribution 0 <= n <= 10
            and Pt is a function of tech spent
        """
        pu = numpy.random.randint(11)
        pt = int(numpy.sqrt(max(0, tech_spend)))
        return self.base_reward + pu + pt


class Human(Player):
    def bid(self, public_information):
        print('-------------')
        print(self.name)
        print(public_information)
        amount = input("Bid?")
        self.launch = input("Launch?")
        return amount
