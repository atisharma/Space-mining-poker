"""
strategies.py

Put all strategies in here and import into main file.

A strategy needs to implement .bid() and .join_launch() methods.
"""


class Strategy(object):
    """
    Template strategy, which specific strategies inherit.
    """
    def bid(self, public_information):
        raise Exception("you need to implement a bid strategy!")

    def join_launch(self, public_information):
        raise Exception("you need to implement a launch strategy!")


class Human(Strategy):
    """
    Human strategy always asks for input.
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
