#!/usr/bin/env python3
"""
Runs on client machine.
Listen on socket and reply with bid / launch decision.
strategy.name is the IP address.
"""

import socket
from xmlrpc.server import SimpleXMLRPCServer
import logging


hostname = socket.gethostname()
IP = socket.gethostbyname(hostname)
PORT = 49000


def broadcast(message):
    print(message)


def bid(private_information, public_information):
    print('-------------')
    print(private_information['name'] + " up.")
    print(public_information)
    print("Your tech: %d" % private_information['tech'])
    print("Your money: %d" % private_information['bankroll'])
    amount = input("Enter bid: ")
    if not amount.isnumeric():
        amount = 0
    launch = input("Launch? (Y/N) ")
    if launch[0].upper() == 'Y':
        launching = True
    else:
        launching = False
    return int(amount), launching


def join_launch(private_information, public_information):
    print('-------------')
    print(private_information['name'] + " up.")
    print(public_information)
    print("Your tech: %d" % private_information['tech'])
    print("Your money: %d" % private_information['bankroll'])
    launch = input("Join launch? (Y/N) ")
    if launch[0].upper() == 'Y':
        return True
    else:
        return False


server =  SimpleXMLRPCServer((IP, PORT), allow_none=True,
                             logRequests=False)
print("Listening on %s:%d" % (IP, PORT) )
server.register_function(bid, "bid")
server.register_function(join_launch, "join_launch")
server.register_function(broadcast, "broadcast")
server.serve_forever()
