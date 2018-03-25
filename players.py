"""
Players

All different player types are implemented here.
"""

import xmlrpc.client
from strategies import *


class Player(object):
    """Abstract base class for all players. Implements only minimal book-keeping
        while leaving bidding and launching (via RPC or local strategy) to
        derived classes."""

    def __init__(self, name='', bankroll=1000, tech=0):
        self.bankroll = bankroll
        self.tech = tech
        self.name = name
        self.launching = False
        self.last_bid = 0

    def _get_private_information(self):
        return {
            'name': self.name,
            'tech': self.tech,
            'bankroll': self.bankroll
        }

    def bid(self, public_information):
        raise Exception("you need to implement a bidding functionality!")

    def launch(self, public_information):
        raise Exception("you need to implement a launching functionality!")

    def broadcast(self, message):
        # assume bot, so no messages necessary
        pass

    def buy_tech(self, tech, price):
        self.tech += tech
        self.bankroll -= price

    def collect_payoff(self, payoff):
        self.tech = 0
        self.bankroll += payoff

    def is_bankrupt(self):
        return self.bankroll < 0

    def display(self):
        disp_str = (" - - - - - - - - - - -") + \
            ("\nname: " + self.name) + \
            ("\ntech: %d" % self.tech) + \
            ("\nbankroll: %d" % self.bankroll) + \
            ("\nlast_bid: %d" % self.last_bid) + \
            ("\nlaunching: %r" % self.launching) + \
            ("\n - - - - - - - - - - -")
        return disp_str


class LocalPlayer(Player):
    """A local player delegates all decisions on bidding and launching to a
        locally implemented strategy object."""

    def __init__(self, strategy, name='', bankroll=1000, tech=0):
        super().__init__(name, bankroll, tech)
        self.strategy = strategy

    def bid(self, public_information):
        private_information = self._get_private_information()
        bid, launching = self.strategy.bid(private_information, public_information)
        self.launching = launching
        self.last_bid = int(bid)
        return bid

    def launch(self, public_information):
        if self.launching is True:
            return
        private_information = self._get_private_information()
        self.launching = self.strategy.join_launch(private_information, public_information)

    def broadcast(self, message):
        self.strategy.broadcast(message)


class NetworkPlayer(Player):
    """A network player delegates all decisions on bidding and launching to a
        strategy object exposed over an RPC interface.

        One server per network player.
        Parse ip, port in usual format,
        name@ip.address:port
        Uses xmlrpc to call code running on server.
        Server implements details of strategy."""

    def __init__(self, server, bankroll=1000, tech=0):
        """Create new network player. Server is in name@ip.address:port format."""
        name, location = server.split('@')
        super().__init__(name, bankroll, tech)
        self.url = "http://" + location + "/"
        self.strategy = xmlrpc.client.ServerProxy(self.url)    # don't handle errors here, failure to connect is a crash (?)

    def _rpc_error(self, err):
        print("A network fault occurred for player " + self.name + \
              " at URL " + self.url)
        print("Fault code: %d" % err.faultCode)
        print("Fault string: %s" % err.faultString)

    def bid(self, public_information):
        private_information = self._get_private_information()
        bid = 0
        launching = False

        try:
            bid, launching = self.strategy.bid(private_information, public_information)
        except xmlrpc.client.Fault as err:
            self._rpc_error(err)

        self.last_bid = int(bid)
        self.launching = launching
        return bid

    def launch(self, public_information):
        if self.launching is True:
            return
        private_information = self._get_private_information()

        try:
            self.launching = self.strategy.join_launch(private_information, public_information)
        except xmlrpc.client.Fault as err:
            self._rpc_error(err)

    def broadcast(self, message):
        try:
            self.strategy.broadcast(message)
        except xmlrpc.client.Fault as err:
            self._rpc_error(err)

