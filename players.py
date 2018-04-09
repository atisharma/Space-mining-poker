"""
Players

All different player types are implemented here.
"""

import xmlrpc.client
import json
import os


class Player(object):
    """Player class for all players. Implements book-keeping, bidding and
        launching (via RPC or local strategy)."""

    def __init__(self, strategy, name='', bankroll=1000, tech=0):
        """
        Create new player with explicit strategy or delegate to RPC server.
        strategy is either a Strategy object instance, or a string indicating the
        server address and port in usual format:
        name@ip.address:port
        where the name@ part is optional and ignored.
        """
        self.bankroll = bankroll
        self.tech = tech
        self.name = name
        self.launching = False
        self.last_bid = 0
        self.stats_file = self.name + '.log'
        try:
            os.remove(self.stats_file)
        except:
            pass
        if isinstance(strategy, str):
            try:
                # this player uses a remote strategy via RPC using this server
                location = strategy.split('@')[-1]
                self.url = "http://" + location + "/"
                self.strategy = xmlrpc.client.ServerProxy(self.url)
                self.strategy.ping()
            except:
                self.remove_player()
        else:
            # assume the given strategy is a Strategy object with appropriate functions
            self.strategy = strategy

    def _get_private_information(self):
        return {
            'name': self.name,
            'tech': self.tech,
            'bankroll': self.bankroll,
            'launching': self.launching,
            'last_bid': self.last_bid
        }

    def _rpc_error(self, err):
        print("A network fault occurred for player " + self.name + \
              " at URL " + self.url)
        print("Fault code: %d" % err.faultCode)
        print("Fault string: %s" % err.faultString)

    def write_statistics(self, public_information=None):
        if self.stats_file:
            with open(self.stats_file, 'a') as stats_file:
                information = {'private': self._get_private_information(),
                               'public': public_information}
                stats_file.write(json.dumps(information))
                stats_file.write('\n')

    def bid(self, public_information):
        private_information = self._get_private_information()
        launching = False

        try:
            bid, launching = self.strategy.bid(private_information, public_information)
        except xmlrpc.client.Fault as err:
            self._rpc_error(err)
        except:
            self.remove_player()

        try:
            bid = int(bid)
        except:
            bid = 0

        self.last_bid = bid
        self.launching = bool(launching) and self.tech > 0    # you must have at least some tech to launch
        self.write_statistics(public_information)
        return bid

    def launch(self, public_information):
        if self.launching is True:
            self.write_statistics(public_information)
            return
        private_information = self._get_private_information()
        launching = False
        try:
            launching = self.strategy.join_launch(private_information, public_information)
        except xmlrpc.client.Fault as err:
            self._rpc_error(err)
        except:
            self.remove_player()

        self.launching = bool(launching)
        self.write_statistics(public_information)

    def broadcast(self, message):
        try:
            self.strategy.broadcast(message)
        except xmlrpc.client.Fault as err:
            self._rpc_error(err)
        except:
            self.remove_player()

    def next_round(self):
        """
        Dump stats to file, check player still responds to ping.
        """
        self.write_statistics()
        try:
            self.strategy.ping()
        except:
            self.remove_player()

    def buy_tech(self, tech, price):
        self.tech += tech
        self.bankroll -= price
        self.write_statistics()

    def collect_payoff(self, payoff):
        self.tech = 0
        self.bankroll += payoff
        self.write_statistics()

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

    def remove_player(self):
        # could not connect, make player bankrupt, unset strategy
        print("Could not connect to player " + self.name + ", removing.")
        self.strategy = False
