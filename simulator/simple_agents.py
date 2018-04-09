import random 
from utils import Action


class RandomAgent:
    def __init__(self, Action):
        self.Action = Action

    def act(self, state=None):
        return random.choice(list(self.Action))


class BollingerBandAgent:

    def act(self, state):
    	cross_upper_band, cross_lower_band = state 
    	if cross_upper_band:
    		return Action.SELL
    	if cross_lower_band:
    		return Action.BUY
    	return Action.HOLD