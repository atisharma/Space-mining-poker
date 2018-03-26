#!/usr/bin/env python3
"""
Runs on remote machine to serve strategy decisions to game client.
Listen on socket and reply with bid / launch decision.
strategy.name is the IP address.
"""

import socket
import sys
from xmlrpc.server import SimpleXMLRPCServer

from strategies import *


def run_server(strategy=Terminal(), port=49000):
    """Create the RPC server and share the entire strategy object."""
    #hostname = socket.gethostname()
    hostname = "0.0.0.0"    # be greedy and listen on all local interfaces
    IP = socket.gethostbyname(hostname)
    server = SimpleXMLRPCServer((IP, port), allow_none=True, logRequests=False)
    print("Listening on %s:%d" % (IP, port) )
    server.register_instance(strategy)
    server.serve_forever()

def main(argv):
    if len(argv) < 1:
        print("Specify either the port number (> 1024) or the player number (<= 1024)!")
        return
    port = int(argv[0])
    if port <= 1024:
        port += 49000
    strategy = Terminal()
    run_server(strategy, port)

if __name__ == "__main__":
    main(sys.argv[1:])
