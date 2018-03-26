"""
This file is meant to be modified to define the players active in the game.
"""

from strategies import *

# Define players here.

player_dict = {
    #'Ati' : 'localhost:49000',
    #'Alex' : 'localhost:49001',
    #'Cedric' : Terminal(),
    'SpongeBob' : SpongeBob(),
    'PassiveLauncher' : PassiveLauncher(),
    'AlwaysLauncher' : AlwaysLaunch(),
    'AggressiveLauncher' : AggressiveLauncher(),
    'EVBot' : EVBot(),
}
