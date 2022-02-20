import numpy as np
import EuropeanVanilla


def log_normal_pdf(x, mu, sigma):
    return 1 / (x * sigma * np.sqrt(2* np.pi)) * np.exp(-((np.log(x)- mu) ** 2)/(2 * sigma ** 2))

def value_at_strike(strike, spot, for_rate, dom_rate, vol, maturity, approx=False):
    
    if approx:
       
        eps = 0.001
        call_value = EuropeanVanilla.price("call", spot, strike, for_rate, dom_rate, vol, maturity)
        call_value_up_bump = EuropeanVanilla.price("call", spot, strike + eps, for_rate, dom_rate, vol, maturity)
        call_value_down_bump = EuropeanVanilla.price("call", spot, strike - eps, for_rate, dom_rate, vol, maturity)

        finite_diff = (call_value_up_bump - 2 * call_value + call_value_down_bump) / eps ** 2

        pdf_value_at_strike = np.exp(dom_rate * maturity) * finite_diff
    
    else:

        mu = np.log(spot) + (dom_rate - for_rate - vol ** 2 / 2) * maturity
        sigma = vol * np.sqrt(maturity)
        pdf_value_at_strike = log_normal_pdf(strike, mu, sigma)

    return pdf_value_at_strike