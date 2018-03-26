"""
Players

All different player types are implemented here.
"""

import xmlrpc.client


class Player(object):
    """Player class for all players. Implements book-keeping, bidding and
        launching (via RPC or local strategy)."""

    def __init__(self, strategy, name='', bankroll=1000, tech=0):
        """Create new player with explicit strategy or delegated to RPC server.
            strategy is either a Strategy object, or a string indicating the
            server address and port in usual format:
            name@ip.address:port
            where the name@ part is optional and ignored."""
        if isinstance(strategy, str):
            # this player uses a remote strategy via RPC using this server
            location = strategy.split('@')[-1]
            self.url = "http://" + location + "/"
            self.strategy = xmlrpc.client.ServerProxy(self.url)    # don't handle errors here, failure to connect is a crash (?)
        else:
            # assume the given strategy is a Strategy object with appropriate functions
            self.strategy = strategy
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
