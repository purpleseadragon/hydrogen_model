# Importing modules
import pandas as pd

from algorithms import *


input_file_path = r"C:\Users\o_dav\Dropbox\2023_thesis\input_data.xlsx"
output_file_path = r"C:\Users\o_dav\Dropbox\2023_thesis\output_data_gen.xlsx"

inputs = pd.read_excel(input_file_path)

# print(inputs.head())
# print(inputs.columns)
# print(inputs.index)

headers = {
    "sort": [], "time": [], "date": [], "solar_gen": [], "wind_gen": [],"electrolyser_input": [], 
    "h2_prod_rate": [], "battery_input": [], "battery_output": [], "battery_level": [], "purchase_rate": [], 
    "sell_rate": [], "cumulative_battery": [], "grid_price": [], "purchase_cost": [], "sell_cost": [], "sell_net_price": []
    }

outputs = pd.DataFrame(headers)

# constants -> consider changing to taking from JSON or similar method

time_step = 1/12 # hours

# for 1 January
# start_time = 120 # Jan 1, 10 am -> only have data from here for wind
# end_time = 20000 # Jan 12, 10 am -> 12 day time period 3288


# set variables
solar_panels = 100000 # rated capacity is 575 * number of panels W
solar_price = 65 # $/MWh (gencost 2022 low end)
ac_conversion_eff = 0.95 # 95% efficiency
print(f"total installed solar is {solar_panels*575e-6:,.2f} MW")

wind_turbines = 25 # rated capacity is 3400 * number of turbines kW
wind_price = 75 # $/MWh (gencost 2022 low end)
dc_conversion_eff = 0.95 # 95% efficiency

print(f"total installed wind is {wind_turbines*3.4:,.2f} MW")

# average houselod uses about 15 kWh per day -> 15/24 = 0.625 kW

# assume PEM for now
electrolysers = 20 # rated capacity is 1990 * number of electrolysers 
electrolyser_capacity = 1990 # kW
electrolyser_capacity_total = electrolysers*electrolyser_capacity # kW
min_production_eff = 48+7 # kWh / kg at max capacity (48 kWh/kg for stack + 7 kWh/kg for tertiary processes)
max_production_eff = 40+7 # kWh / kg at min capacity (40 kWh/kg for stack + 7 kWh/kg for tertiary processes)
electrolyser_cost_per_kw_2023 = 1606 # $/kW (alkaline gencost 2022/23) # PEM is 2628
electrolyser_ul = 20 # years
print(f"total installed electrolyser capaccity is {electrolyser_capacity_total*1e-3:,.2f} MW")

batteries = 20 # rated capacity is 3000 * number of batteries kWh
battery_capacity = 3000 # kWh
battery_capacity_total = batteries*battery_capacity # kWh
battery_eff = 0.9 # 90% efficiency
battery_max_time = 8 # hours
battery_max_charge_rate = 3000*batteries # kW
battery_cost_per_kwh_2023 = 485 # $/kWh
battery_ul = 20 # years
print(f"total installed battery capacity is {battery_capacity_total*1e-3:,.2f} MWh")

 # for max purchase price algorithm
price_maximum = 20 # $/MWh
electrolyser_min_capacity = 0.3 # fraction of max capacity -> dependent on type of electrolyser e.g. PEM, alkaline, etc.

def main(opt_alg, inputs, outputs, start_time, end_time, state, wind_loc):
    # initial setup
    battery_level = 0
    # working loop
    def working_loop(opt_alg, price_state, wind_loc, inputs=inputs, outputs=outputs, battery_level=battery_level):
        """iterates through each timestep and calls the algorithm to determine the next timestep"""
        for i in range(start_time, end_time-start_time):
            sort = inputs.loc[i,'sort']
            time = inputs.loc[i,'time']
            date = inputs.loc[i,'date']

            solar_output = inputs.loc[i,'solar_output']*solar_panels*10**(-3) # W -> kW
            wind_output = inputs.loc[i,f'wind_output_{wind_loc}']*wind_turbines # kW
            grid_price = inputs.loc[i,f'grid_price_{price_state}'] # $/MWh
            
            # generates cumulative battery 
            if len(outputs) > battery_max_time/time_step:
                outputs['cumulative_battery'] = outputs['battery_input'].rolling(window=int(battery_max_time/time_step)).sum() - \
                    - outputs['battery_input']
                cumulative_battery = outputs.loc[i-start_time-1,'cumulative_battery']
            else:
                outputs['cumulative_battery'] = 0
                cumulative_battery = 0

            # call algorithm
            new_row = opt_alg(outputs, sort, time, date, solar_output, 
                            wind_output, battery_level, time_step, 
                            battery_capacity_total, battery_max_charge_rate, battery_eff, battery_max_time,
                            electrolyser_capacity_total, grid_price, cumulative_battery,
                            min_production_eff, max_production_eff,
                            wind_price, solar_price,
                            price_maximum, electrolyser_min_capacity)
            
            outputs = pd.concat([outputs, pd.DataFrame(new_row, index=[0])], ignore_index=True)

            battery_level = outputs.loc[i-start_time,'battery_level']
        return outputs

    outputs = working_loop(opt_alg, state, wind_loc)



    # sum over the 12 days
    total_h2_produced = outputs['h2_prod_rate'].sum()*time_step # kg/h converted to kg/min and then taking into account time step

    outputs["purchase_cost"] = outputs[f"grid_price"] * outputs["purchase_rate"]*time_step*10**(-3) # $/MWh * kWh * ... -> $
    outputs["sell_net_price"] = outputs["grid_price"]*outputs["sell_rate"] *time_step*10**(-3)# $/MWh * kWh * ... -> $ # takes difference between cost of electricity and price sold for 


    # calculate total cost
    total_cost_purchased = outputs['purchase_cost'].sum()
    total_cost_sold = outputs['sell_net_price'].sum()

    total_cost_solar = inputs['solar_output'][start_time:end_time].sum()*time_step*solar_panels*solar_price*10**(-6) # ... -> Wh * n * $/MWh * MWh/Wh -> $
    total_cost_wind = inputs[f'wind_output_{wind_loc}'][start_time:end_time].sum()*time_step*wind_turbines*wind_price*10**(-3) # ... -> kWh * n * $/MWh * MWh/Wh -> $

    total_cost_battery = battery_capacity_total*battery_cost_per_kwh_2023 * (end_time - start_time) / (battery_ul*365*24*12)
    total_cost_electrolyser = electrolyser_capacity_total*electrolyser_cost_per_kw_2023 * (end_time - start_time) / (electrolyser_ul*365*24*12)
    print("")
    print(f"total h2 produced: {total_h2_produced:,.2f} kg, average production: {total_h2_produced/(end_time-start_time)/time_step:,.2f} kg/hr")
    print(f"total cost of purchased electricity: ${total_cost_purchased:,.2f}")
    print(f"net profit from sold electricity: ${total_cost_sold:,.2f}") # need to get difference between produced and sold prices 
    print(f"total price solar: ${total_cost_solar:,.2f}")
    print(f"total price wind: ${total_cost_wind:,.2f} ")
    print(f"cost of batteries over the time period: ${total_cost_battery:,.2f}")
    print(f"cost of electrolysers over the time period: ${total_cost_electrolyser:,.2f}")

    # price per kg of H2
    print(f"price per kg of H2: ${(total_cost_purchased + total_cost_solar + total_cost_wind + total_cost_battery + total_cost_electrolyser-total_cost_sold)/(total_h2_produced):,.2f} excl. of electrolyser, conversion, and battery costs")

    outputs.to_excel(output_file_path, index=False) 

if __name__ == "__main__":
    # change parameters for different test results
    state_1 = 'qld'
    state_2 = 'sa'
    wind_loc_1 = '1'
    wind_loc_2 = '2'
    start_time = 132 # Jan 1, 10:30 am -> only have data from here for wind
    end_time = 3288 # Jan 12, 10:30 am -> 12 day time period

    # output to different files


    # print("\nusing trivial algorithm, QLD prices, wind location 1 \n")
    # main(trivial, inputs, outputs, start_time, end_time, state_1, wind_loc_1)

    # print("\nusing max purchase price algorithm, QLD prices, wind location 1 \n")
    # main(max_purchase_price, inputs, outputs, start_time, end_time, state_1, wind_loc_1)

    # print("\nusing trivial algorithm, SA prices, wind location 1 \n")
    # main(trivial, inputs, outputs, start_time, end_time, state_2, wind_loc_1)

    # print("\nusing max purchase price algorithm, SA prices, wind location 1 \n")
    # main(max_purchase_price, inputs, outputs, start_time, end_time, state_2, wind_loc_1)

    # print("\nusing trivial algorithm, QLD prices, wind location 2 \n")
    # main(trivial, inputs, outputs, start_time, end_time, state_1, wind_loc_2)

    # print("\nusing max purchase price algorithm, QLD prices, wind location 2 \n")
    # main(max_purchase_price, inputs, outputs, start_time, end_time, state_1, wind_loc_2)

    # print("\nusing trivial algorithm, SA prices, wind location 2 \n")
    # main(trivial, inputs, outputs, start_time, end_time, state_2, wind_loc_2)

    print("\nusing max purchase price algorithm, SA prices, wind location 2 \n")
    main(max_purchase_price, inputs, outputs, start_time, end_time, state_2, wind_loc_2)
