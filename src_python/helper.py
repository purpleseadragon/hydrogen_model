

def generate_sell_cost(sell_rate, solar_output, wind_price, solar_price):
    """making the assumption that battery_price > wind_price > solar_price"""
    cost = 0
    if sell_rate < solar_output:
        cost = solar_price
    else:
        cost = wind_price
    return cost
