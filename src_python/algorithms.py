# ...
from helper import generate_sell_cost
from electrolysis import electrolysis

def algorithm_1(outputs, sort, time, date, 
            solar_output, wind_output, battery_level, 
            time_diff, battery_capacity_total, battery_max_charge_rate, battery_eff, 
            battery_max_time, electrolyser_capacity_total, grid_price, cumulative_battery,
            min_production_eff, max_production_eff,
            wind_price, solar_price, price_sell_minimum,
            price_buy_maximum, electrolyser_min_capacity):
    """The trivial algorithm attempts to maintain electrolysis production at 100%  capacity by any means possible."""
    # (1) inefficient algorithm 
    sell_rate = 0
    battery_output = 0
    sell_cost = 0

    electrolyser_input = electrolyser_capacity_total

    h2_prod_rate = electrolysis(electrolyser_input, 0.1*electrolyser_capacity_total, electrolyser_capacity_total, min_production_eff, max_production_eff)

    # if wind and solar are greater than electrolyser capacity, then excess goes to battery
    battery_input = max(min((wind_output + solar_output - electrolyser_input)*battery_eff,(battery_capacity_total - battery_level)/time_diff), 0)

    # after the initial 8 hours, has to start remembering battery input over initial 8 hours and battery level cannot exceed this
    # if len(outputs) > battery_max_time/time_diff:
    #     battery_output = min(max(battery_level/time_diff - cumulative_battery, 0), battery_max_charge_rate)

    # if wind + solar < electrolyser_input, then use battery to make up the difference
    # if len(outputs) > battery_max_time/time_diff and wind_output + solar_output < electrolyser_input:
    #     battery_output = max(min((electrolyser_input - wind_output - solar_output)/battery_eff, battery_level / time_diff*battery_eff), max(battery_level/time_diff - cumulative_battery,0))
    
    # elif len(outputs) > battery_max_time/time_diff:
    #     battery_output = max(battery_level/time_diff - cumulative_battery,0)

    if wind_output + solar_output < electrolyser_input:
        battery_output = min((electrolyser_input - wind_output - solar_output), battery_level / time_diff, battery_max_charge_rate)

    # if wind + solar > battery_input + electrolyser_input, then sell excess
    if battery_input - battery_output < wind_output + solar_output - electrolyser_input:
        sell_rate = wind_output + solar_output - electrolyser_input - battery_input + battery_output

    # if wind + solar < electrolyser_input, then purchase from grid to make up the difference
    purchase_rate = max(electrolyser_input - wind_output - solar_output - battery_output, 0)

    battery_level = round(battery_level + battery_input * time_diff - battery_output * time_diff,2)

    new_row = {
        "sort": sort, "time": time, "date": date, "electrolyser_input": electrolyser_input, "solar_gen": solar_output, 
        "wind_gen": wind_output,"h2_prod_rate": h2_prod_rate, "battery_input": battery_input, "battery_output": battery_output, 
        "battery_level": battery_level, "purchase_rate": purchase_rate, "grid_price": grid_price, "sell_rate": sell_rate, "sell_cost": sell_cost
        }
    
    sell_cost = sell_rate*grid_price*time_diff*10**(-3)
    
    return new_row


def algorithm_2(outputs, sort, time, date, 
            solar_output, wind_output, battery_level, 
            time_diff, battery_capacity_total, battery_max_charge_rate, battery_eff, 
            battery_max_time, electrolyser_capacity_total, grid_price, cumulative_battery,
            min_production_eff, max_production_eff,
            wind_price, solar_price, price_sell_minimum,
            price_buy_maximum, electrolyser_min_capacity):
    
    # this algorithm only purchases hydrogen if it is cheaper a price maximum
    # up to some minimum capacity
    sell_rate = 0
    battery_input = 0
    battery_output = 0
    sell_cost = 0
    purchase_rate = 0


    # after the initial 8 hours, has to start remembering battery input over initial 8 hours and battery level cannot exceed this
    # if len(outputs) > battery_max_time/time_diff:
    #     battery_output = min(max(battery_level/time_diff - cumulative_battery, 0), battery_max_charge_rate)

    # purchase as much energy as possible if price is below price maximum
    if grid_price < price_buy_maximum and wind_output + solar_output + battery_output < electrolyser_capacity_total:
        battery_input = min((battery_capacity_total - battery_level)/time_diff, battery_max_charge_rate)
        # purchase rate is amount required to get max battery input + electrolyser capacity
        purchase_rate = max(electrolyser_capacity_total - wind_output - solar_output + battery_input/battery_eff - battery_output, 0)
    
    elif grid_price < price_buy_maximum and wind_output + solar_output + battery_output >= electrolyser_capacity_total:
        battery_input = min((battery_capacity_total - battery_level)/time_diff, battery_max_charge_rate)
        # purchase rate is amount required to get max battery input + electrolyser capacity
        purchase_rate = max(battery_input/battery_eff -(solar_output + wind_output + battery_output - electrolyser_capacity_total)/battery_eff, 0)

    # # if price is less than maximum but not sufficiently low to purchase for battery purchase only enough to meet max electrolyser capacity
    # elif grid_price < price_buy_maximum:
    #     purchase_rate = max(electrolyser_capacity_total - wind_output - solar_output, 0)
    #     # if wind + solar < electrolyser_input, then use battery to make up the difference

    elif grid_price >= price_buy_maximum and wind_output + solar_output + battery_output < electrolyser_capacity_total:
        battery_output = min((electrolyser_capacity_total - wind_output - solar_output - battery_output), battery_level / time_diff, battery_max_charge_rate)

    elif grid_price >= price_buy_maximum and wind_output + solar_output + battery_output >= electrolyser_capacity_total:
        battery_input = max(min((wind_output + solar_output + battery_output - electrolyser_capacity_total)*battery_eff,(battery_capacity_total - battery_level)/time_diff, battery_max_charge_rate), 0)

    battery_input_raw = battery_input/battery_eff

    battery_level = round(battery_level + battery_input * time_diff - battery_output * time_diff,2)

    # if wind + solar + battery_output   > battery_input + electrolyser_input, then sell excess
    if battery_output + wind_output + solar_output + purchase_rate > electrolyser_capacity_total + battery_input_raw:
        sell_rate = max(wind_output + solar_output - electrolyser_capacity_total - battery_input_raw + battery_output, 0)
        # sell_cost = generate_sell_cost(sell_rate, solar_output, wind_price, solar_price)
        

    # balance 
    electrolyser_input = purchase_rate + wind_output + solar_output + battery_output - battery_input_raw - sell_rate

    if electrolyser_input < electrolyser_min_capacity*electrolyser_capacity_total:
        electrolyser_input = electrolyser_min_capacity*electrolyser_capacity_total
        purchase_rate = electrolyser_input - (purchase_rate + wind_output + solar_output + battery_output - battery_input_raw - sell_rate)

    h2_prod_rate = electrolysis(electrolyser_input, electrolyser_min_capacity*electrolyser_capacity_total, electrolyser_capacity_total, min_production_eff, max_production_eff)
    
    if sell_rate > 0 and purchase_rate > 0:
        if purchase_rate > sell_rate:
            purchase_rate -= sell_rate
            sell_rate = 0
        else:
            sell_rate -= purchase_rate
            purchase_rate = 0

    sell_cost = sell_rate*grid_price*time_diff*10**(-3)
    
    new_row = {
        "sort": sort, "time": time, "date": date, "electrolyser_input": electrolyser_input, "solar_gen": solar_output, 
        "wind_gen": wind_output,"h2_prod_rate": h2_prod_rate, "battery_input": battery_input, "battery_output": battery_output, 
        "battery_level": battery_level, "purchase_rate": purchase_rate, "grid_price": grid_price, "sell_rate": sell_rate, "sell_cost": sell_cost
        }
    
    return new_row


def algorithm_3(outputs, sort, time, date, 
            solar_output, wind_output, battery_level, 
            time_diff, battery_capacity_total, battery_max_charge_rate, battery_eff, 
            battery_max_time, electrolyser_capacity_total, grid_price, cumulative_battery,
            min_production_eff, max_production_eff,
            wind_price, solar_price, price_sell_minimum,
            price_buy_maximum, electrolyser_min_capacity):
    """buys when cheap enough and sells whenm expensive enough"""
        # this algorithm only purchases hydrogen if it is cheaper a price maximum
    # up to some minimum capacity
    sell_rate = 0
    battery_input = 0
    battery_output = 0
    sell_cost = 0
    purchase_rate = 0


    # after the initial 8 hours, has to start remembering battery input over initial 8 hours and battery level cannot exceed this
    # if len(outputs) > battery_max_time/time_diff:
    #     battery_output = min(max(battery_level/time_diff - cumulative_battery, 0), battery_max_charge_rate)

    # purchase as much energy as possible if price is below price maximum
    if grid_price < price_buy_maximum and wind_output + solar_output + battery_output < electrolyser_capacity_total:
        battery_input = min((battery_capacity_total - battery_level)/time_diff, battery_max_charge_rate)
        # purchase rate is amount required to get max battery input + electrolyser capacity
        purchase_rate = max(electrolyser_capacity_total - wind_output - solar_output + battery_input/battery_eff - battery_output, 0)
    
    elif grid_price < price_buy_maximum and wind_output + solar_output + battery_output >= electrolyser_capacity_total:
        battery_input = min((battery_capacity_total - battery_level)/time_diff, battery_max_charge_rate)
        # purchase rate is amount required to get max battery input + electrolyser capacity
        purchase_rate = max(battery_input/battery_eff -(solar_output + wind_output + battery_output - electrolyser_capacity_total)/battery_eff, 0)

    # if price sufficiently high run at minimum electrolyser capacity and sell excess
    elif grid_price > price_sell_minimum:
        battery_output = max(min(battery_level / time_diff, battery_max_charge_rate), battery_output)
        sell_rate = max(wind_output + solar_output + battery_output - electrolyser_min_capacity, 0)
        sell_cost = generate_sell_cost(sell_rate, solar_output, wind_price, solar_price)

    # # if price is less than maximum but not sufficiently low to purchase for battery purchase only enough to meet max electrolyser capacity
    # elif grid_price < price_buy_maximum:
    #     purchase_rate = max(electrolyser_capacity_total - wind_output - solar_output, 0)
    #     # if wind + solar < electrolyser_input, then use battery to make up the difference

    elif grid_price >= price_buy_maximum and grid_price <= price_sell_minimum and wind_output + solar_output + battery_output < electrolyser_capacity_total:
        battery_output = min((electrolyser_capacity_total - wind_output - solar_output - battery_output), battery_level / time_diff, battery_max_charge_rate)

    elif grid_price >= price_buy_maximum and grid_price <= price_sell_minimum and wind_output + solar_output + battery_output >= electrolyser_capacity_total:
        battery_input = max(min((wind_output + solar_output + battery_output - electrolyser_capacity_total)*battery_eff,(battery_capacity_total - battery_level)/time_diff, battery_max_charge_rate), 0)

    battery_input_raw = battery_input/battery_eff

    battery_level = round(battery_level + battery_input * time_diff - battery_output * time_diff,2)

    if grid_price < price_sell_minimum:
        # if wind + solar + battery_output   > battery_input + electrolyser_input, then sell excess
        if battery_output + wind_output + solar_output + purchase_rate > electrolyser_capacity_total + battery_input_raw:
            sell_rate = max(wind_output + solar_output - electrolyser_capacity_total - battery_input_raw + battery_output, 0)
            sell_cost = generate_sell_cost(sell_rate, solar_output, wind_price, solar_price)

    # balance 
    electrolyser_input = purchase_rate + wind_output + solar_output + battery_output - battery_input_raw - sell_rate

    if electrolyser_input < electrolyser_min_capacity*electrolyser_capacity_total:
        electrolyser_input = electrolyser_min_capacity*electrolyser_capacity_total
        purchase_rate = electrolyser_input - (purchase_rate + wind_output + solar_output + battery_output - battery_input_raw - sell_rate)

    h2_prod_rate = electrolysis(electrolyser_input, electrolyser_min_capacity*electrolyser_capacity_total, electrolyser_capacity_total, min_production_eff, max_production_eff)
    
    if sell_rate > 0 and purchase_rate > 0:
        if purchase_rate > sell_rate:
            purchase_rate -= sell_rate
            sell_rate = 0
        else:
            sell_rate -= purchase_rate
            purchase_rate = 0
    
    sell_cost = sell_rate*grid_price*time_diff*10**(-3)
        
    new_row = {
        "sort": sort, "time": time, "date": date, "electrolyser_input": electrolyser_input, "solar_gen": solar_output, 
        "wind_gen": wind_output,"h2_prod_rate": h2_prod_rate, "battery_input": battery_input, "battery_output": battery_output, 
        "battery_level": battery_level, "purchase_rate": purchase_rate, "grid_price": grid_price, "sell_rate": sell_rate, "sell_cost": sell_cost
        }
    
    return new_row