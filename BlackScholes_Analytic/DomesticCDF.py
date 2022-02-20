import numpy as np
import scipy.integrate as integrate
import DomesticPDF


def value_at_strike(strike, spot, for_rate, dom_rate, vol, maturity, useApproxPDE=False):
    
    pdf = lambda x: DomesticPDF.value_at_strike(x, spot, for_rate, dom_rate, vol, maturity, useApproxPDE)
    
    if len(np.array([strike])) > 1:
        
        cdf_value_at_strike = np.array([integrate.quad(pdf, 0, strike[i])[0] for i in range(len(strike))])
   
    else:
        
        cdf_value_at_strike = integrate.quad(pdf, 0, strike)[0]
    
    return cdf_value_at_strike