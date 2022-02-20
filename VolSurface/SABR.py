import numpy as np
import scipy.optimize as so
import ATMStrike
import MSStrike
import EuropeanVanilla


def get_vol(spot, strike, for_rate, dom_rate, maturity, alpha, nu, rho, beta = 1):
    
    forward = spot * np.exp((dom_rate - for_rate) * maturity)
    log_F_K = np.log(forward / strike)
    FK = forward * strike

    z = nu / alpha * FK ** ((1 - beta)/2) * log_F_K
    chi = lambda x: np.log((np.sqrt(1 - 2 * rho * x + x ** 2) + x - rho)  / (1 - rho))
    
    A = alpha / FK ** ((1 - beta)/2) / (1 + (1- beta) ** 2 / 24 * log_F_K ** 2 + (1 - beta) ** 4 / 1920 * log_F_K ** 4)
    B = z / chi(z)
    C = 1 + ((1 - beta) ** 2 / 24 * alpha ** 2 / FK ** (1 - beta) + 1/ 4 * rho * beta * nu * alpha / FK ** ((1 - beta)/2) + (2 - 3 * rho ** 2) / 24 * nu ** 2) * maturity
    vol = A * B * C

    return vol

def calibration(spot, for_rate, dom_rate, atm_vol, ms_vol, rr_vol, maturity, atm_type, delta_conv, delta_type, rr_sign, tol = 0.000001, max_iter = 500):
    
    # Determine K_ATM (step 2)
    K_ATM = ATMStrike.get_strike(spot, for_rate, dom_rate, atm_vol, maturity, atm_type, delta_conv)
    
    # Use (3.9) together with... (step 3)
    K_25d_C_MS = float(MSStrike.get_strike("call", spot, for_rate, dom_rate, atm_vol + ms_vol, maturity, delta_conv, delta_type, 0.25))
    K_25d_P_MS = float(MSStrike.get_strike("put", spot, for_rate, dom_rate,  atm_vol + ms_vol, maturity, delta_conv, delta_type, 0.25))
    
    # Use (3.10) to determine V_target (step 4)
    call_value = EuropeanVanilla.price("call", spot, K_25d_C_MS, for_rate, dom_rate, atm_vol + ms_vol, maturity)
    put_value = EuropeanVanilla.price("put", spot, K_25d_P_MS, for_rate, dom_rate, atm_vol + ms_vol, maturity)
    V_target = call_value + put_value
    
    # Choose initial guess (step 5)
    sig_25d_SS = ms_vol
    
    
    error = 1.0
    iter = 0
    while (error > tol and max_iter > iter):
        iter += 1

        # Optimization (step 6)
        K_25d_C = float(MSStrike.get_strike("call", spot, for_rate, dom_rate, atm_vol + sig_25d_SS + rr_sign * 0.5 * rr_vol, maturity, delta_conv, delta_type, 0.25))
        K_25d_P = float(MSStrike.get_strike("put", spot, for_rate, dom_rate,  atm_vol + sig_25d_SS - rr_sign * 0.5 * rr_vol, maturity, delta_conv, delta_type, 0.25))
    
        strikes = np.array([K_25d_P, K_ATM, K_25d_C])
        
        starting_point = np.array([0.174, 0.816, -0.112])
        anchor_vols = np.array([atm_vol + sig_25d_SS - rr_sign * 0.5 * rr_vol, atm_vol, atm_vol + sig_25d_SS + rr_sign * 0.5 * rr_vol])
        
        obj = lambda parameters, strikes, anchor_vols: get_vol(spot, strikes, for_rate, dom_rate, maturity, parameters[0], parameters[1], parameters[2]) - anchor_vols
        calibrated_parameters = so.least_squares(obj, starting_point, args=(strikes, anchor_vols))
        

        sabr_call_vol = get_vol(spot, K_25d_C_MS, for_rate, dom_rate, maturity, calibrated_parameters.x[0], calibrated_parameters.x[1], calibrated_parameters.x[2], beta = 1)
        sabr_put_vol = get_vol(spot, K_25d_P_MS, for_rate, dom_rate, maturity, calibrated_parameters.x[0], calibrated_parameters.x[1], calibrated_parameters.x[2], beta = 1)
        
        # Price up the market strangle (step 7)
        call_value = EuropeanVanilla.price("call", spot, K_25d_C_MS, for_rate, dom_rate, sabr_call_vol, maturity)
        put_value = EuropeanVanilla.price("put",  spot, K_25d_P_MS, for_rate, dom_rate, sabr_put_vol, maturity)
        V_trial = call_value + put_value
        
        # Check stopping condition (step 8)
        if V_target - V_trial > 0:
            sig_25d_SS += 0.01 * sig_25d_SS
            error = V_target - V_trial
        else:
            sig_25d_SS -= 0.01 * sig_25d_SS
            error = V_trial - V_target

    return {"parameters": calibrated_parameters.x, "strikes": strikes, "error": error, "iter": iter}

"""
cpflag = "put"
spot = 1.3465
for_rate = 3.4590409573467507 / 100
dom_rate = 2.9378348524295794 / 100
atm_vol = 18.25 / 100
ms_vol = 0.950 / 100
rr_vol = -0.600 / 100
atm_type = "DNS"
rr_sign = 1.0
maturity = 1.0
delta_conv = "pips"
delta_type = "spot"
delta_level = 25 / 100

strike = 1.3620
alpha = 0.17431060
nu = 0.81694072
rho = -0.11268306

sabr_parameters = calibration(spot, for_rate, dom_rate, atm_vol, ms_vol, rr_vol, maturity, atm_type, delta_conv, delta_type, rr_sign, tol = 0.000001, max_iter = 500)

atm_strike = ATMStrike.get_strike(spot, for_rate, dom_rate, atm_vol, maturity, atm_type, delta_conv)

anchor_strikes = sabr_parameters["strikes"]
w = np.linspace(atm_strike * (1 - 0.2), atm_strike * (1 + 0.2))
x = np.sort(np.concatenate((w, anchor_strikes), axis=0))
calibrated_sabr = get_vol(spot, x, for_rate, dom_rate, maturity, sabr_parameters["parameters"][0], sabr_parameters["parameters"][1], sabr_parameters["parameters"][2], beta = 1)
clark_sabr = get_vol(spot, x, for_rate, dom_rate, maturity, alpha, nu, rho, beta = 1)
calibrated_sabr_vol_at_anchor_strikes = get_vol(spot, anchor_strikes, for_rate, dom_rate, maturity, sabr_parameters["parameters"][0], sabr_parameters["parameters"][1], sabr_parameters["parameters"][2], beta = 1)

import matplotlib.pyplot as plt
plt.plot(x, clark_sabr, color = "r", label = "Clark")
plt.plot(x, calibrated_sabr, color = "b", label = "MRM")
plt.plot(anchor_strikes, calibrated_sabr_vol_at_anchor_strikes, marker = "o", color = "k", linestyle='', markersize = 6, label = "Calibration points")
plt.legend()
plt.show()
"""