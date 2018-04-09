from env import *
from simple_agents import * 
from portfolio import *

def run_random_agent(data, capital=60000.0, init_order_ratio=0.7, verbose=False, recent_k=0):
    ra = RandomAgent(Action)
    env = Environment(data=data, recent_k=recent_k)
    portfolio = Portfolio(final_price=env.getFinalPrice(), capital=capital, init_order_ratio=init_order_ratio, verbose=verbose)

    is_done = False 
    while not is_done:
        action = ra.act()
        portfolio.apply_action(env.getCurrentPrice(), action)
        is_done, _ = env.step()

    portfolio.printCurrentHoldings(env.getCurrentPrice())
    return portfolio.getReturnsPercent(env.getCurrentPrice())


def run_bollingerband_agent(data, capital=60000.0, init_order_ratio=0.7, 
                            verbose=False, recent_k=0, bollinger_threshold=0):
    bba = BollingerBandAgent()
    env = Environment(data=data, recent_k=recent_k, 
                      states=["cross_upper_band", "cross_lower_band"], bollinger_threshold=bollinger_threshold)
    portfolio = Portfolio(final_price=env.getFinalPrice(), capital=capital, init_order_ratio=init_order_ratio, verbose=verbose)

    is_done = False 
    state = env.getCurrentStates()

    while not is_done:
        # print portfolio.getCurrentHoldings()
        action = bba.act(state)
        # print action
        portfolio.apply_action(env.getCurrentPrice(), action)
        is_done, state = env.step()

    portfolio.printCurrentHoldings(env.getCurrentPrice())    
    return portfolio.getReturnsPercent(env.getCurrentPrice())


def run_alwaysbuy_agent(data, capital=60000.0, init_order_ratio=0.7, verbose=False, recent_k=0):
    env = Environment(data=data, recent_k=recent_k)
    portfolio = Portfolio(final_price=env.getFinalPrice(), capital=capital, init_order_ratio=init_order_ratio, verbose=verbose)

    is_done = False 
    while not is_done:
        portfolio.apply_action(env.getCurrentPrice(), Action.BUY)
        is_done, _ = env.step()

    portfolio.printCurrentHoldings(env.getCurrentPrice())
    return portfolio.getReturnsPercent(env.getCurrentPrice())