# ...

def trivial(sort, time, date, solar_output, wind_output, battery_level, time_diff, battery_capacity_total, battery_eff, electrolyser_capacity_total):
    # (1) inefficient algorithm 
    sell_rate = 0
    battery_output = 0

    h2_prod_rate = electrolyser_capacity_total

    # if wind and solar are greater than electrolyser capacity, then sell excess
    battery_input = max(min(wind_output + solar_output - h2_prod_rate,(battery_capacity_total - battery_level)/time_diff) , 0)

    # if wind + solar > battery_input + h2_prod_rate, then sell excess
    if battery_input < wind_output + solar_output - h2_prod_rate:
        sell_rate = wind_output + solar_output - h2_prod_rate - battery_input

    # if wind + solar < h2_prod_rate, then use battery to make up the difference
    if wind_output + solar_output < h2_prod_rate:
        battery_output = min(h2_prod_rate - wind_output - solar_output , battery_level / time_diff * battery_eff)

    # if wind + solar < h2_prod_rate, then purchase from grid to make up the difference
    purchase_rate = max(h2_prod_rate - wind_output - solar_output - battery_output, 0)

    battery_level = battery_level + battery_input * time_diff - battery_output * time_diff

    new_row = {
        "sort": sort, "time": time, "date": date, "h2_prod_rate": h2_prod_rate ,
        "battery_input": battery_input, "battery_output": battery_output, "battery_level": battery_level, 
        "purchase_rate": purchase_rate, "sell_rate": sell_rate
        }
    
    return new_row