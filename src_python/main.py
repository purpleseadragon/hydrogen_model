# Importing modules
import pandas as pd

from algorithms import *


input_file_path = r"C:\Users\o_dav\Dropbox\2023_thesis\input_data.xlsx"
output_file_path = r"C:\Users\o_dav\Dropbox\2023_thesis\output_data_gen.xlsx"

inputs = pd.read_excel(input_file_path)


print(inputs.head())
print(inputs.columns)
print(inputs.index)

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
battery_max_time = 8 # hours
#battery_charge_rate = 3000 # kW

time_diff = 1/12 # hours

# initial setup
battery_level = 0

# working loop
for i in range(start_time, end_time -start_time):
    sort = inputs.loc[i,'sort']
    time = inputs.loc[i,'time']
    date = inputs.loc[i,'date']

    solar_output = inputs.loc[i,'solar_output']*solar_panels
    wind_output = inputs.loc[i,'wind_output']*wind_turbines
    grid_price = inputs.loc[i,'grid_price']

    new_row = trivial(sort, time, date, solar_output, wind_output, battery_level, time_diff, battery_capacity_total, battery_eff, electrolyser_capacity_total)
    
    outputs = pd.concat([outputs, pd.DataFrame(new_row, index=[0])], ignore_index=True)

    battery_level = outputs.loc[i-start_time,'battery_level']
    # get electrolysis capacity

    # get battery storage capacity

    # assign production to electrolysis and battery storage

    # choose amount of energy to purchase from grid

    # record all data

    # new_row = {...}

    # outputs.append(new_row, ignore_index=True)


outputs.to_excel(output_file_path, index=False) 
