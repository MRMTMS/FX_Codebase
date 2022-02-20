import numpy as np
import scipy.stats as ss
import EuropeanVanilla


def price(cpflag, spot, strike, for_rate, dom_rate, vol, maturity, barrier_level, barrier_direction):
        
    omega = 1 if cpflag == "call" else -1
    forward = spot * np.exp((dom_rate - for_rate) * maturity)
    d1 = (np.log(spot/strike) + (dom_rate - for_rate + vol ** 2 / 2) * maturity) / (vol * np.sqrt(maturity))
    d2 = (np.log(spot/strike) + (dom_rate - for_rate - vol ** 2 / 2) * maturity) / (vol * np.sqrt(maturity))
    d1_B = (np.log(spot/barrier_level) + (dom_rate - for_rate + vol ** 2 / 2) * maturity) / (vol * np.sqrt(maturity))
    d2_B = (np.log(spot/barrier_level) + (dom_rate - for_rate - vol ** 2 / 2) * maturity) / (vol * np.sqrt(maturity))
    
    if barrier_direction == "up":
        # up_and_out call
        if cpflag == "call":
            if strike < barrier_level:
                pv = omega * (np.exp(-dom_rate * maturity) * (forward * (ss.norm.cdf(omega * d1) - ss.norm.cdf(omega * d1_B)) - strike * (ss.norm.cdf(omega * d2) - ss.norm.cdf(omega * d2_B))))
            else:
                pv = 0.0
            return pv
        # up_and_out put
        else:
            if strike < barrier_level:
                pv = EuropeanVanilla.price(cpflag, spot, strike, for_rate, dom_rate, vol, maturity)
            else:
                pv = omega * (np.exp(-dom_rate * maturity) * (forward * ss.norm.cdf(omega * d1_B) - strike * ss.norm.cdf(omega * d2_B)))
            return pv
    else:
        # down_and_out call
        if cpflag == "call":
            if strike < barrier_level:
                pv = omega * (np.exp(-dom_rate * maturity) * (forward * ss.norm.cdf(omega * d1_B) - strike * ss.norm.cdf(omega * d2_B)))
            else:
                pv = EuropeanVanilla.price(cpflag, spot, strike, for_rate, dom_rate, vol, maturity)
            return pv
        # down_and_out put
        else:
            if strike < barrier_level:
                pv = 0.0
            else:
                pv = omega * (np.exp(-dom_rate * maturity) * (forward * (ss.norm.cdf(omega * d1) - ss.norm.cdf(omega * d1_B)) - strike * (ss.norm.cdf(omega * d2) - ss.norm.cdf(omega * d2_B))))
            return pv