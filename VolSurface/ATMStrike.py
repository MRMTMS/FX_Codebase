import numpy as np


def get_strike(spot, for_rate, dom_rate, vol, maturity, atm_type, delta_conv):

    if atm_type == "ATMF":
        return spot * np.exp((dom_rate - for_rate) * maturity)
    else:
        if delta_conv == "pips":
            return spot * np.exp((dom_rate - for_rate + vol ** 2 / 2) * maturity)
        else:
            return spot * np.exp((dom_rate - for_rate - vol ** 2 / 2) * maturity)