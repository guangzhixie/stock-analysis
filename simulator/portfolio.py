import numpy as np
from utils import *


# internal state
state_list = ["stock", "cash", "total_value", "is_holding_stock", "return_since_entry"]
spread = 0.01 # 1 bps


class Portfolio:
    
    # initialize portfolio variables
    def __init__(self, final_price, capital=60000.0, init_order_ratio=0.7, verbose=False, states=state_list):
        self.verbose = verbose
        self.states = states
        self.init_capital = capital
        self.init_order_ratio = init_order_ratio
        self.cash = capital
        self.stock = 0.0
        self.final_price = final_price
        
        ### Mapping states to their names
        self.state_dict = {}
        self.state_dict["stock"] = self.stock
        self.state_dict["cash"] = self.cash
        self.state_dict["total_value"] = self.init_capital
        self.state_dict["is_holding_stock"] = 0
        self.state_dict["return_since_entry"] = 0
    

    
    def __buy(self, current_price):
        if not current_price:
            return 0
        
        buy_price = current_price * (1 + spread)
        
        avaliable_cash = self.cash * self.init_order_ratio if self.cash == self.init_capital else self.cash
        if avaliable_cash == 0:
            return 0
        
        stock_to_buy = round_down(avaliable_cash / buy_price)
        
        cash_used = stock_to_buy * buy_price
        
        if self.verbose:
            print "original stock:{}, stock to buy:{}, original cash:{}, buy price:{}, cash used:{}".format(
                self.stock, stock_to_buy, self.cash, buy_price, cash_used)
            
        self.stock += stock_to_buy
        self.cash -= cash_used
        
        if self.verbose:
            print ", stock now:{}, cash now:{}, total value:{}".format(
                self.stock, self.cash, self.getCurrentValue(current_price))
        
        return stock_to_buy
    
    
    
    def __sell(self, current_price):
        if not current_price:
            return 0
        
        sell_price = current_price * (1 - spread)
        
        stock_to_sell = self.stock
        if stock_to_sell == 0:
            return 0
        
        cash_gained = stock_to_sell * sell_price
        
        if self.verbose:
            print "original stock:{}, stock to sell:{}, original cash:{}, sell price:{}, cash gained:{}".format(
                self.stock, stock_to_sell, self.cash, sell_price, cash_gained)
        
        self.stock -= stock_to_sell
        self.cash += cash_gained
        
        if self.verbose:
            print "stock now:{}, cash now:{}, total value:{}".format(
                self.stock, self.cash, self.getCurrentValue(current_price)) 
        
        return stock_to_sell
    
    
    ## PUBLIC METHODS ##
     
    # apply action (buy, sell or hold) to the portfolio
    # update the internal state after the action
    def apply_action(self, current_price, action):
        self.state_dict["total_value"] = self.getCurrentValue(current_price)
        if self.verbose:
            print "Action start", action, "Total value before action", self.state_dict["total_value"]           
        
        if action == Action.BUY:
            stock_to_buy = self.__buy(current_price)
            if stock_to_buy == 0:
                action = Action.HOLD
                
        elif action == Action.SELL:
            stock_to_sell = self.__sell(current_price)
            if stock_to_sell == 0:
                action = Action.HOLD
        
        self.reward = self.getCurrentValue(self.final_price) - self.state_dict["total_value"] 
        
        # Update states
        self.state_dict["stock"] = self.stock
        self.state_dict["cash"] = self.cash
        self.state_dict["total_value"] = self.getCurrentValue(current_price)
        self.state_dict["is_holding_stock"] = (self.stock > 0)*1
        self.state_dict["return_since_entry"] = self.getReturnsPercent(current_price)
        
        if self.verbose:
            print "Action end:", action, "Reward:", self.reward
            
        return action
        

    def getCurrentValue(self, current_price):
        sell_price = current_price * (1 - spread)
        return self.stock * sell_price + self.cash

    
    def getReturnsPercent(self, current_price):
        return 100 * (self.getCurrentValue(current_price) - self.init_capital) / self.init_capital


    # return internal state    
    def getCurrentStates(self, states=None):
        if not states:
            states = self.states
        return [self.state_dict[state] for state in states]
    
    
    def getReward(self):
        return self.reward

    
    def printCurrentHoldings(self, current_price):
        print "%.2f stocks, %.2f cash, %.2f current value, %.2f percent returns" \
                % (self.stock, self.cash, self.getCurrentValue(current_price), 
                   self.getReturnsPercent(current_price))

    
    # reset portfolio
    def reset(self):
        self.__init__(final_price=self.final_price, capital=self.init_capital, states = self.states,
                      init_order_ratio = self.init_order_ratio, verbose=self.verbose)
        