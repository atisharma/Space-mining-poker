"""
This file is meant to be modified to define the players active in the game.
"""

from strategies import *

# Define players here.

player_dict = {
    'Sharma' : 'laika.clients.soton.ac.uk:49000',
    'Wittig' : 'localhost:49001',
    'Sivyer' : 'localhost:49229',
    'Simpson' : 'localhost:49193',
    'Peploe' : 'localhost:49823',
    'Comerford' : 'localhost:49902',
    'Freckelton' : 'localhost:49224',
    'Lovelock' : 'localhost:49933',
    #'Cedric' : Terminal(),
    'SpongeBob' : SpongeBob(),
    'PassiveLauncher' : PassiveLauncher(),
    #'AlwaysLauncher' : AlwaysLaunch(),
    #'AggressiveLauncher' : AggressiveLauncher(),
    #'Observer' : Observer(),
    #'Evie' : EVBot(),
}
