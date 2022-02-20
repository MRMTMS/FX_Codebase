import EuropeanVanilla


def price(spot, strike, for_rate, dom_rate, vol, maturity):
    
    call_value = EuropeanVanilla.price("call", spot, strike, for_rate, dom_rate, vol, maturity)
    put_value =  EuropeanVanilla.price("put", spot, strike, for_rate, dom_rate, vol, maturity)
    
    return call_value + put_value