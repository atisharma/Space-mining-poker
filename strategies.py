"""
strategies.py

Put all strategies in here and import into main file.

A strategy needs to implement .bid() and .join_launch() methods.
"""

import xmlrpc.client

class Strategy(object):
    """
    Template strategy, which specific strategies inherit.
    """
    def bid(self, public_information):
        raise Exception("you need to implement a bid strategy!")

    def join_launch(self, public_information):
        raise Exception("you need to implement a launch strategy!")

    def broadcast(self, message):
        # assume bot, so no messages necessary
        pass


class TerminalPlayer(Strategy):
    """
    Human strategy always asks for input from terminal.
    """

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

    def broadcast(self, message):
        print(message)


class SpongeBob(Strategy):
    """
    SpongeBob always bids and launches based on fixed threshold.
    """

    def bid(self, public_information):
        amount = min(self.bankroll, public_information['base_reward'])
        launching = self.tech > 10
        return int(amount), launching

    def join_launch(self, public_information):
        return self.tech > 15


class AlwaysLaunch(Strategy):
    """
    AlwaysLaunch never bids but always launches.
    """

    def bid(self, public_information):
        amount = 0
        launching = True
        return int(amount), launching

    def join_launch(self, public_information):
        return True


class PassiveLauncher(Strategy):
    """
    PassiveLauncher always lowball bids and launches when others do.
    """

    def bid(self, public_information):
        amount = min(self.bankroll, public_information['last_winning_bid'] - 1)
        launching = False
        return int(amount), launching

    def join_launch(self, public_information):
        return True


class NetworkPlayer(Strategy):
    """
    Strategy links to network server running on another machine.
    One server per network player.
    Parse ip, port in usual format,
        name@ip.address:port
    Uses xmlrpc to call code running on server.
    Server implements details of strategy.
    """

    def bid(self, public_information):
        name, location = self.name.split('@')
        url = "http://" + location + "/"
        private_information = {
            'name': name,
            'tech': self.tech,
            'bankroll': self.bankroll
        }
        bid = 0
        launching = False

        try:
            with xmlrpc.client.ServerProxy(url) as proxy:
                bid, launching = proxy.bid(
                    private_information, public_information)
        except xmlrpc.client.Fault as err:
            print("A network fault occurred for player " + name + \
                  " at location " + location)
            print("Fault code: %d" % err.faultCode)
            print("Fault string: %s" % err.faultString)

        return bid, launching

    def join_launch(self, public_information):
        name, location = self.name.split('@')
        url = "http://" + location + "/"
        private_information = {
            'name': name,
            'tech': self.tech,
            'bankroll': self.bankroll
        }
        launching = False

        try:
            with xmlrpc.client.ServerProxy(url) as proxy:
                launching = proxy.join_launch(
                    private_information, public_information)
        except xmlrpc.client.Fault as err:
            print("A network fault occurred for player " + name + \
                  " at location " + location)
            print("Fault code: %d" % err.faultCode)
            print("Fault string: %s" % err.faultString)

        return launching

    def broadcast(self, message):
        name, location = self.name.split('@')
        url = "http://" + location + "/"
        try:
            with xmlrpc.client.ServerProxy(url) as proxy:
                launching = proxy.broadcast( message)
        except xmlrpc.client.Fault as err:
            print("A network fault occurred for player " + name + \
                  " at location " + location)
            print("Fault code: %d" % err.faultCode)
            print("Fault string: %s" % err.faultString)
