"""
A Sound of Distant Thunder: A point-and-click adventure/RPG
with body-snatching horror elements in a space station setting.
"""

# Version information
__version__ = '0.1.0'
__author__ = 'Your Name'

# Import key subsystems for easy access
from .core import GameEngine, EventSystem
from .game import GameState, Hero
from .ui import UIManager

__all__ = [
    'GameEngine',
    'EventSystem',
    'GameState',
    'Hero',
    'UIManager'
]