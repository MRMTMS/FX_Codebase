import numpy as np
import scipy.stats as ss


def price(cpflag, spot, strike, for_rate, dom_rate, vol, maturity):
    
    omega = 1 if cpflag == "call" else -1
    forward = spot * np.exp((dom_rate - for_rate) * maturity)
    d1 = (np.log(spot/strike) + (dom_rate - for_rate + vol ** 2 / 2) * maturity) / (vol * np.sqrt(maturity))
    d2 = (np.log(spot/strike) + (dom_rate - for_rate - vol ** 2 / 2) * maturity) / (vol * np.sqrt(maturity))
    
    pv = omega * np.exp(-dom_rate * maturity) * (forward * ss.norm.cdf(omega * d1) - strike * ss.norm.cdf(omega * d2))
    
    return pv

def delta(cpflag, spot, strike, for_rate, dom_rate, vol, maturity, delta_conv = "pips", delta_type = "spot"):
    
    omega = 1 if cpflag == "call" else -1
    forward = spot * np.exp((dom_rate - for_rate) * maturity)
    d1 = (np.log(spot/strike) + (dom_rate - for_rate + vol ** 2 / 2) * maturity) / (vol * np.sqrt(maturity))
    d2 = (np.log(spot/strike) + (dom_rate - for_rate - vol ** 2 / 2) * maturity) / (vol * np.sqrt(maturity))
    d = (d1 + d2) / 2

    if delta_type == "spot":
        if delta_conv == "pips":
            return omega * np.exp(-for_rate * maturity) * ss.norm.cdf(omega * d1)
        elif delta_conv == "perc":
            return omega * np.exp(-dom_rate * maturity) * ss.norm.cdf(omega * d2) * strike / spot
    
    elif delta_type == "fwd":
        if delta_conv == "pips":
            return omega * ss.norm.cdf(omega * d1)
        elif delta_conv == "perc":
            return omega * ss.norm.cdf(omega * d2) * strike / forward 
    
    elif delta_type == "simple":
        return omega * ss.norm.cdf(omega * d)