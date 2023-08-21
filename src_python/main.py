# Importing modules
import pandas as pd

input_file_path = r"C:\Users\o_dav\Dropbox\2023_thesis\input_data.xlsx"
output_file_path = r"C:\Users\o_dav\Dropbox\2023_thesis\output_data_gen.xlsx"

inputs = pd.read_excel(input_file_path)

# print(inputs.head())
# print(inputs.columns)
# print(inputs.index)

headers = {
    "sort": [], "time": [], "date": [], "h2_prod_rate": [],
    "battery_input": [], "battery_output": [], "battery_level": [], 
    "purchase_rate": [], "sell_rate": []
    }

outputs = pd.DataFrame(headers)

# for 1 January
start_time = 120 # Jan 1, 10 am
end_time = 3288 # Jan 12, 10 am

# set variables
solar_panels = 1000 # rated capacity is 245 * number of panels kW
solar_price = 50 # $/MWh (refer to thesis)

wind_turbines = 80 # rated capacity is 3400 * number of turbines kW
wind_price = 60 # $/MWh (refer to thesis)

# assume PEM for now
electrolysers = 80 # rated capacity is 1990 * number of electrolysers 
electrolyser_capacity = 1990 # kW
electrolyser_capacity_total = electrolysers*electrolyser_capacity # kW

batteries = 10 # rated capacity is 3000 * number of batteries kWh
battery_capacity = 3000 # kWh
battery_capacity_total = batteries*battery_capacity # kWh
battery_eff = 0.9 # 90% efficiency
#battery_charge_rate = 3000 # kW

time_diff = 1/12 # hours

# initial setup
battery_level = 0 # kWh

sort = inputs.loc[start_time,'sort']
date = inputs.loc[start_time,'date']
time = inputs.loc[start_time,'time']

solar_output = inputs.loc[start_time,'solar_output']*solar_panels
wind_output = inputs.loc[start_time,'wind_output']*wind_turbines
grid_price = inputs.loc[start_time,'grid_price']


# (1) inefficient algorithm 
sell_rate = 0
battery_output = 0

h2_prod_rate = electrolyser_capacity_total

battery_input = max(min(wind_output + solar_output - h2_prod_rate,(battery_capacity_total - battery_level)/time_diff) , 0)

if battery_input < wind_output + solar_output - h2_prod_rate:
    sell_rate = wind_output + solar_output - h2_prod_rate - battery_input


if wind_output + solar_output < h2_prod_rate:
    battery_output = min(h2_prod_rate - wind_output - solar_output , battery_level * time_diff * battery_eff)


purchase_rate = max(h2_prod_rate - wind_output - solar_output - battery_output, 0)

battery_level = battery_level + battery_input * time_diff - battery_output * time_diff



new_row = {"sort": sort, "time": time, "date": date, "h2_prod_rate": h2_prod_rate ,
    "battery_input": battery_input, "battery_output": battery_output, "battery_level": battery_level, 
    "purchase_rate": purchase_rate, "sell_rate": sell_rate}

outputs = pd.concat([outputs, pd.DataFrame(new_row, index=[0])], ignore_index=True)

# working loop
for i in range(start_time, end_time -start_time):
    # get solar generation data
    solar_output = inputs.loc[i,'solar_output']

    # get wind generation data
    wind_output = inputs.loc[i,'wind_output']
    
    # get grid energy prices
    grid_price = inputs.loc[i,'grid_price']

    print(solar_output, wind_output, grid_price)

    # get electrolysis capacity

    # get battery storage capacity

    # assign production to electrolysis and battery storage

    # choose amount of energy to purchase from grid

    # record all data

    # new_row = {...}

    # outputs.append(new_row, ignore_index=True)
    
    break


outputs.to_excel(output_file_path, index=False) 
