import numpy as np
import scipy.stats as ss
import EuropeanVanilla


def price(cpflag, spot, strike, for_rate, dom_rate, vol, maturity, payout_ccy):
        
    omega = 1 if cpflag == "call" else -1
    d1 = (np.log(spot/strike) + (dom_rate - for_rate + vol ** 2 / 2) * maturity) / (vol * np.sqrt(maturity))
    d2 = (np.log(spot/strike) + (dom_rate - for_rate - vol ** 2 / 2) * maturity) / (vol * np.sqrt(maturity))
        
    if payout_ccy == "for":
        
        pv = np.exp(-for_rate * maturity) * ss.norm.cdf(omega * d1) * spot
        
    else:
           
        pv = np.exp(-dom_rate * maturity) * ss.norm.cdf(omega * d2)

        return pv

def replication_price(cpflag, spot, strike, for_rate, dom_rate, vol, maturity, payout_ccy):

    eps = 0.001
    omega = 1 if cpflag == "call" else -1
    vanilla_value_up_bump = EuropeanVanilla.price(cpflag, spot, strike + eps, for_rate, dom_rate, vol, maturity)
    vanilla_value_down_bump = EuropeanVanilla.price(cpflag, spot, strike - eps, for_rate, dom_rate, vol, maturity)

    return omega * (vanilla_value_down_bump - vanilla_value_up_bump) / (2 * eps)