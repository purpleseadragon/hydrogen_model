# ...

from electrolysis import electrolysis_PEM

def trivial(outputs, sort, time, date, 
            solar_output, wind_output, battery_level, 
            time_diff, battery_capacity_total, battery_eff, battery_max_time,
            electrolyser_capacity_total, grid_price, cumulative_battery,
            price_maximum, electrolyser_min_capacity):
    """The trivial algorithm attempts to maintain electrolysis production at 100%  capacity by any means possible."""
    # (1) inefficient algorithm 
    sell_rate = 0
    battery_output = 0

    electrolyser_input = electrolyser_capacity_total

    h2_prod_rate = electrolysis_PEM(electrolyser_input, 0.1*electrolyser_capacity_total, electrolyser_capacity_total, 48+7, 40+7)

    # if wind and solar are greater than electrolyser capacity, then excess goes to battery
    # if more than 8 time periods also need to do balancing to make sure battery outputs are >= battery inputs over last n (8) hours
    battery_input = max(min(wind_output + solar_output - electrolyser_input,(battery_capacity_total - battery_level)/time_diff), 0)

    # if wind + solar < electrolyser_input, then use battery to make up the difference
    if len(outputs) > battery_max_time/time_diff and wind_output + solar_output < electrolyser_input:
        battery_output = max(min((electrolyser_input - wind_output - solar_output)/battery_eff, battery_level / time_diff*battery_eff), max(battery_level/time_diff - cumulative_battery,0))
    
    elif len(outputs) > battery_max_time/time_diff:
        battery_output = max(battery_level/time_diff - cumulative_battery,0)

    elif wind_output + solar_output < electrolyser_input:
        battery_output = (electrolyser_input - wind_output - solar_output)/battery_eff , battery_level / time_diff* battery_eff

    # if wind + solar > battery_input + electrolyser_input, then sell excess
    if battery_input < wind_output + solar_output - electrolyser_input:
        sell_rate = wind_output + solar_output - electrolyser_input - battery_input + battery_output

    # if wind + solar < electrolyser_input, then purchase from grid to make up the difference
    purchase_rate = max(electrolyser_input - wind_output - solar_output - battery_output, 0)

    battery_level = battery_level + battery_input * time_diff - battery_output * time_diff

    new_row = {
        "sort": sort, "time": time, "date": date, "electrolyser_input": electrolyser_input, "h2_prod_rate": h2_prod_rate ,
        "battery_input": battery_input, "battery_output": battery_output, "battery_level": battery_level, 
        "purchase_rate": purchase_rate, "sell_rate": sell_rate, "grid_price": grid_price
        }
    
    return new_row


def max_purchase_price(outputs, sort, time, date, 
            solar_output, wind_output, battery_level, 
            time_diff, battery_capacity_total, battery_eff, battery_max_time,
            electrolyser_capacity_total, grid_price, cumulative_battery,
            price_maximum, electrolyser_min_capacity):
    # this algorithm only purchases hydrogen if it is cheaper a price maximum
    # up to some minimum capacity
    pass