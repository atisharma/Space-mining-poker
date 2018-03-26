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
        self.stats_file = False

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

    def open_statistics_file(self):
        if self.stats_file:
            self.stats_file.close()
        self.stats_file = open(self.name+'.log', 'w')

    def bid(self, public_information):
        private_information = self._get_private_information()
        launching = False

        try:
            bid, launching = self.strategy.bid(private_information, public_information)
        except xmlrpc.client.Fault as err:
            self._rpc_error(err)

        try:
            bid = int(bid)
        except:
            bid = 0

        self.last_bid = bid
        self.launching = bool(launching) and self.tech > 0    # you must have at least some tech to launch
        if self.stats_file:
            self.stats_file.write("bid: {} {}\n".format(bid, launching))
        return bid

    def launch(self, public_information):
        if self.launching is True:
            if self.stats_file:
                self.stats_file.write("launching: {}\n".format(self.launching))
            return
        private_information = self._get_private_information()
        launching = False
        try:
            launching = self.strategy.join_launch(private_information, public_information)
        except xmlrpc.client.Fault as err:
            self._rpc_error(err)

        self.launching = bool(launching)
        if self.stats_file:
            self.stats_file.write("launching: {}\n".format(self.launching))

    def broadcast(self, message):
        try:
            self.strategy.broadcast(message)
        except xmlrpc.client.Fault as err:
            self._rpc_error(err)

    def next_round(self):
        if self.stats_file:
            self.stats_file.write("nextround: {} {}\n".format(self.tech, self.bankroll))

    def buy_tech(self, tech, price):
        self.tech += tech
        self.bankroll -= price
        if self.stats_file:
            self.stats_file.write("buy: {} {}\n".format(tech, price))

    def collect_payoff(self, payoff):
        self.tech = 0
        self.bankroll += payoff
        if self.stats_file:
            self.stats_file.write("payoff: {}\n".format(payoff))

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
