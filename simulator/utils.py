import math
from enum import Enum

# action list
class Action(Enum):
    HOLD=0
    BUY=1
    SELL=2

def round_up(v):
    return (math.ceil(v*10000)/10000)

def round_down(v):
    return (math.floor(v*10000)/10000)