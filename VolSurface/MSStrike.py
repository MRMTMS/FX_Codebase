import numpy as np
import scipy.optimize as so
import ATMStrike
import EuropeanVanilla


def get_strike(cpflag, spot, for_rate, dom_rate, vol, maturity, delta_conv, delta_type, delta_level):

    omega = 1 if cpflag == "call" else -1
    starting_point = ATMStrike.get_strike(spot, for_rate, dom_rate, vol, maturity, "ATMF", delta_conv)
    obj = lambda strike: EuropeanVanilla.delta(cpflag, spot, strike, for_rate, dom_rate, vol, maturity, delta_conv, delta_type) - omega * delta_level
    
    strike = so.fsolve(obj, starting_point)
    
    return strike

"""
cpflag = "put"
spot = 1.3465
for_rate = 3.4590409573467507 / 100
dom_rate = 2.9378348524295794 / 100
vol = 18.25 / 100
ms_vol = 0.950 / 100
vol = vol + ms_vol
maturity = 1.0
delta_conv = "pips"
delta_type = "spot"
delta_level = 25 / 100

print(get_strike(cpflag, spot, for_rate, dom_rate, vol, maturity, delta_conv, delta_type, delta_level))
"""