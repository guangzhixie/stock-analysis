import pandas as pd 
import numpy as np
from utils import *


state_list = ["current_price", "rolling_mean", "rolling_std", "cross_upper_band", "cross_lower_band", "upper_band",
             "lower_band", "price_over_sma"]

class Environment:
    
    # load pricing data
    # initialize the environment variables
    def __init__(self, data, states=state_list, recent_k = 0, bollinger_threshold=0):
        self.series = data
        self.states = states
        self.recent_k = recent_k
        self.bollinger_threshold=bollinger_threshold
        self.length = len(self.series)
        
        if self.recent_k == 0:
            self.current_index = 0
        else:
            self.current_index = self.length - self.recent_k
        
        self.__init()

    # deriving the features used for the state definition
    def __init(self):
        self.isDone = np.zeros(self.series["Adj Close"].shape, dtype=bool)
        self.isDone[-1] = True 

        ### States
        self.rm = self.series["Adj Close"].rolling(window=20).mean()
        self.rstd = self.series["Adj Close"].rolling(window=20).std()
        self.upper_band, self.lower_band = self.rm + 2 * self.rstd, self.rm - 2 * self.rstd

        ### Mapping states to their names
        self.state_dict = {}
        self.state_dict["current_price"] = self.series["Adj Close"]
        self.state_dict["rolling_mean"] = self.rm
        self.state_dict["rolling_std"] = self.rstd
        self.state_dict["cross_upper_band"] = self.__crossUpperBand()
        self.state_dict["cross_lower_band"] = self.__crossLowerBand()
        self.state_dict["upper_band"] = self.upper_band
        self.state_dict["lower_band"] = self.lower_band
        self.state_dict["price_over_sma"] = self.series["Adj Close"]/self.rm
        
        
    def __crossUpperBand(self):
        crossUpperBand = [0]
        for i in range(1, len(self.series)):
            crossUpperBand.append(self.__checkCrossUpperBand(i)*1)
        return crossUpperBand
    
    
    def __crossLowerBand(self):
        crossLowerBand = [0]
        for i in range(1, len(self.series)):
            crossLowerBand.append(self.__checkCrossLowerBand(i)*1)
        return crossLowerBand
    
        
    def __checkCrossUpperBand(self, curr_index):
        return (
            curr_index - 1 >= 0
            and self.upper_band[curr_index]-self.bollinger_threshold >= self.state_dict["current_price"][curr_index]
            and self.upper_band[curr_index-1]-self.bollinger_threshold < self.state_dict["current_price"][curr_index-1]
        )
    
    def __checkCrossLowerBand(self, curr_index):
        return (
            curr_index - 1 >= 0
            and self.lower_band[curr_index]+self.bollinger_threshold <= self.state_dict["current_price"][curr_index]
            and self.lower_band[curr_index-1]+self.bollinger_threshold > self.state_dict["current_price"][curr_index-1]
        )

    
    ## PUBLIC METHODS ##
    
    # simulate a forward step in the environment, i.e.: moving one day
    def step(self):
        isDone = self.isDone[self.current_index]
        observation = []
        for state in self.states:
            observation.append(self.state_dict[state][self.current_index])
        if not isDone:
            self.current_index += 1
        return isDone, observation

    
    def getCurrentStates(self, states=None):
        if not states:
            states = self.states
        return [self.state_dict[state][self.current_index] for state in states]

    
    ## Add method to get current price as it is commonly used
    def getCurrentPrice(self):
        return self.state_dict["current_price"][self.current_index]
    
    
    def getFinalPrice(self):
        return self.state_dict["current_price"][self.length-1]
    
    
    def getPriceAt(self, index):
        if index < 0:
            return self.state_dict["current_price"][0]
        if index >= self.length:
            return self.getFinalPrice()
        return self.state_dict["current_price"][index]
    

    def plot(self, states_to_plot=None):
        import matplotlib.pyplot as plt
        if not states_to_plot:
            states_to_plot = self.states

        plt.figure(figsize=(10,6))
        for state in states_to_plot:
            ax = self.state_dict[state][self.current_index:].plot()
        ax.legend(states_to_plot)
        plt.show()

    
    def reset(self):
        if self.recent_k == 0:
            self.current_index = 0
        else:
            self.current_index = self.length - self.recent_k
        
    
    def getReward(self, action):
        a = 0
        if action == Action.BUY:
            a = 1
        elif action == Action.SELL:
            a = -1
            
        price_t = self.getCurrentPrice()
        price_t_minus_1 = self.getPriceAt(self.current_index - 1)
        price_t_minus_n = self.getPriceAt(self.current_index - 10)
        
        r = (1 + a*(price_t - price_t_minus_1)/price_t_minus_1)*price_t_minus_1/price_t_minus_n
        return r