# Importing modules
import pandas as pd

from algorithms import *


input_file_path = r"C:\Users\o_dav\Dropbox\2023_thesis\input_data.xlsx"
output_file_path = r"C:\Users\o_dav\Dropbox\2023_thesis\output_data_gen.xlsx"
output_summary_file_path = r"C:\Users\o_dav\Dropbox\2023_thesis\output_data_summary.xlsx"

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

use_index = 1 # set to 0 for 2023 and set to 1 for 2030 scenario

wind_locations = {'1': "Mt Emerald", '2': "Coopers Gap"}
# constants -> consider changing to taking from JSON or similar method

time_step = 1/12 # hours

# for 1 January
# start_time = 120 # Jan 1, 10 am -> only have data from here for wind
# end_time = 20000 # Jan 12, 10 am -> 12 day time period 3288


# set variables
solar_panels = 77000 # rated capacity is 575 * number of panels W
solar_price = [76, 55][use_index] # $/MWh 
ac_conversion_eff = 0.95 # 95% efficiency
solar_panel_rated = 575e-6 # MW
print(f"total installed solar is {solar_panels*solar_panel_rated:,.2f} MW")

wind_turbines = 13 # rated capacity is 3400 * number of turbines kW
wind_turbines_rated = 3.4 # MW
wind_price = [95,75][use_index] # $/MWh (gencost 2022 low end)
dc_conversion_eff = 0.95 # 95% efficiency

print(f"total installed wind is {wind_turbines*wind_turbines_rated:,.2f} MW")

# average houselod uses about 15 kWh per day -> 15/24 = 0.625 kW

# assume PEM for now
electrolysers = 2 # rated capacity is 1990 * number of electrolysers 
electrolyser_capacity = 22140 # kW
electrolyser_capacity_total = electrolysers*electrolyser_capacity # kW
min_production_eff = 48+7 # kWh / kg at max capacity (48 kWh/kg for stack + 7 kWh/kg for tertiary processes)
max_production_eff = 40+7 # kWh / kg at min capacity (40 kWh/kg for stack + 7 kWh/kg for tertiary processes)
electrolyser_cost_per_kw_2023 = [2638,1278][use_index] # $/kW (PEM gencost 2022/23) # PEM is 2628
electrolyser_ul = 7.5 # years
electrolyser_min_capacity = 0.1 # fraction of max capacity -> dependent on type of electrolyser e.g. PEM, alkaline, etc.
print(f"total installed electrolyser capaccity is {electrolyser_capacity_total*1e-3:,.2f} MW")

batteries = 17 # rated capacity is 3000 * number of batteries kWh
battery_capacity = 3900 # kWh
battery_capacity_total = batteries*battery_capacity # kWh
battery_eff = 0.9 # 90% efficiency
battery_max_time = 4 # hours
battery_max_charge_rate = battery_capacity_total/battery_max_time # kW
battery_cost_per_kwh_2023 = [485, 411][use_index] # $/kWh
battery_ul = 20 # years
print(f"total installed battery capacity is {battery_capacity_total*1e-3:,.2f} MWh")

# for algorithm_2 algorithm
price_buy_maximum = min(solar_price, wind_price) - 40 # $/MWh
price_sell_minimum = max(solar_price, wind_price) + 40 # $/MWh

print(price_buy_maximum,  price_sell_minimum)

water_cost = 3.301e-3 # $/L
water_to_hydrogen_ratio = 12 # L/kg

def main(opt_alg, inputs, outputs, start_time, end_time, state, wind_loc, name="n/a", printing=False):
    # initial setup
    battery_level = 0
    # working loop
    def working_loop(opt_alg, price_state, wind_loc, inputs=inputs, outputs=outputs, battery_level=battery_level):
        """iterates through each timestep and calls the algorithm to determine the next timestep"""
        for i in range(start_time, end_time):
            sort = inputs.loc[i,'sort']
            time = inputs.loc[i,'time']
            date = inputs.loc[i,'date']

            solar_output = inputs.loc[i,'solar_output']*solar_panels*10**(-3) # W -> kW
            wind_output = inputs.loc[i,f'wind_output_{wind_loc}']*wind_turbines # kW
            grid_price = inputs.loc[i,f'grid_price_{price_state}'] # $/MWh
            
            # generates cumulative battery 
            if len(outputs) > battery_max_time/time_step:
                outputs['cumulative_battery'] = outputs['battery_input'].rolling(window=int(battery_max_time/time_step)).sum() \
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
                            wind_price, solar_price, price_sell_minimum,
                            price_buy_maximum, electrolyser_min_capacity)
            
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

    total_solar_produced = inputs['solar_output'][start_time:end_time].sum()*time_step*solar_panels
    total_cost_solar = total_solar_produced*solar_price*10**(-6) # ... -> Wh * n * $/MWh * MWh/Wh -> $

    total_wind_produced = inputs[f'wind_output_{wind_loc}'][start_time:end_time].sum()*time_step*wind_turbines
    total_cost_wind = total_wind_produced*wind_price*10**(-3) # ... -> kWh * n * $/MWh * MWh/Wh -> $

    total_cost_battery = battery_capacity_total*battery_cost_per_kwh_2023 * (end_time - start_time) / (battery_ul*365*24*12)
    total_cost_electrolyser = electrolyser_capacity_total*electrolyser_cost_per_kw_2023 * (end_time - start_time) / (electrolyser_ul*365*24*12)
    total_cost_electrolyser += + 0.02*total_cost_electrolyser # 2% maintenance cost
    
    if printing:
        print(f"total h2 produced: {total_h2_produced:,.2f} kg, average production: {total_h2_produced/(end_time-start_time)/time_step:,.2f} kg/hr, capacity factor:  \
            {total_h2_produced/(end_time-start_time)/time_step/electrolysis(electrolyser_capacity_total, electrolyser_min_capacity*electrolyser_capacity_total, electrolyser_capacity_total, min_production_eff, max_production_eff):,.2f}")
        print(f"total cost of purchased electricity: ${total_cost_purchased:,.2f}")
        print(f"total price of sold electricity: ${total_cost_sold:,.2f}") # need to get difference between produced and sold prices 
        print(f"total price solar: ${total_cost_solar:,.2f}, total solar produced: {total_solar_produced:,.2f}, solar capacity factor: {(total_solar_produced/((end_time-start_time)*solar_panels*solar_panel_rated*time_step*10**6))*100:,.2f}%")
        print(f"total price wind: ${total_cost_wind:,.2f}, wind capacity factor: {(total_wind_produced/((end_time-start_time)*wind_turbines*wind_turbines_rated*time_step*10**3))*100:,.2f}%")
        print(f"cost of batteries over the time period: ${total_cost_battery:,.2f}")
        print(f"cost of electrolysers over the time period: ${total_cost_electrolyser:,.2f}")
        print(f"total kWh purchased from grid: {outputs['purchase_rate'].sum()*time_step:,.2f} kWh")
        print(f"total kWh sold to grid: {outputs['sell_rate'].sum()*time_step:,.2f} kWh")
        print(f"total kWh put into system: {(outputs['solar_gen'].sum()*time_step + outputs['wind_gen'].sum()*time_step+outputs['purchase_rate'].sum()*time_step):,.2f} kWh")
        print(f"total kWh taken from system: {(outputs['electrolyser_input'].sum()*time_step +outputs['sell_rate'].sum()*time_step):,.2f} kWh")
        print(f"total kWh stored in batteries: {outputs['battery_input'].sum()*time_step:,.2f} kWh")
        print(f"total kWh taken from batteries: {outputs['battery_output'].sum()*time_step:,.2f} kWh")
                                                        

        # price per kg of H2
    print(f"price per kg of H2: ${(total_cost_purchased + total_cost_solar + total_cost_wind + total_cost_battery + total_cost_electrolyser + total_h2_produced*water_to_hydrogen_ratio*water_cost-total_cost_sold)/(total_h2_produced):,.2f}")

    outputs.to_excel(output_file_path, index=False) 

    outputs_summary = {
        "name": name,
        "h2_price": (total_cost_purchased + total_cost_solar + total_cost_wind + total_cost_battery + total_cost_electrolyser-total_cost_sold)/(total_h2_produced),
        "total_h2_produced": total_h2_produced, "h2_average_production (kg/s)": total_h2_produced/(end_time-start_time)/time_step, "h2_capacity_factor": total_h2_produced/(end_time-start_time)/time_step/electrolysis(electrolyser_capacity_total, electrolyser_min_capacity*electrolyser_capacity_total, electrolyser_capacity_total, min_production_eff, max_production_eff),  
        "total_wind_produced": total_wind_produced, "wind_capacity_factor:": (total_wind_produced/((end_time-start_time)*wind_turbines*wind_turbines_rated*time_step*10**3))*100, "total_wind_cost": total_cost_wind, 
        "total_solar_produced": total_solar_produced, "solar_capacity_factor": (total_solar_produced/((end_time-start_time)*solar_panels*solar_panel_rated*time_step*10**6))*100, "total_cost_solar": total_cost_solar,
        "battery_cost": total_cost_battery, 
        "electrolyser_cost": total_cost_electrolyser, 
        "total_purchased": outputs['purchase_rate'].sum()*time_step, "total_purchased_cost": total_cost_purchased,
        "total_sold": outputs['sell_rate'].sum()*time_step, "total_sold_cost": total_cost_sold,
        "total_into_system": (outputs['solar_gen'].sum()*time_step + outputs['wind_gen'].sum()*time_step+outputs['purchase_rate'].sum()*time_step), "total_from_system": (outputs['electrolyser_input'].sum()*time_step +outputs['sell_rate'].sum()*time_step),
        "total_into_batteries": outputs['battery_input'].sum()*time_step, "total_from_batteries": outputs['battery_output'].sum()*time_step,
        }
    
    return outputs_summary

if __name__ == "__main__":
    # change parameters for different test results
    state_1 = 'qld'
    state_2 = 'sa'
    wind_loc_1 = '1'
    wind_loc_2 = '2'
    start_time = 34560 # may start
    end_time = 43487 # may end

    outputs_summary_headers = {
        "name": [],
        "h2_price": [],
        "total_h2_produced": [], "h2_average_production (kg/s)": [], "h2_capacity_factor": [],  
        "total_wind_produced": [], "wind_capacity_factor:": [], "total_wind_cost": [], 
        "total_solar_produced": [], "solar_capacity_factor": [], "total_cost_solar": [],
        "battery_cost": [], 
        "electrolyser_cost": [], 
        "total_purchased": [], "total_purchased_cost": [],
        "total_sold": [], "total_sold_cost": [],
        "total_into_system": [], "total_from_system": [],
        "total_into_batteries": [], "total_from_batteries": [],
        }
    
    outputs_summary = pd.DataFrame(outputs_summary_headers)
    # print("\nusing algorithm_1, QLD prices, wind location 1 \n")
    # main(algorithm_1, inputs, outputs, start_time, end_time, state_1, wind_loc_1, True)

    # output to different files
    # states = ['qld', 'sa']
    # wind_locs = ['1', '2']
    # algorithms = [algorithm_1, algorithm_2, algorithm_3]
    # times = [[34560, 43487], [52128,61055], [96192, 105119]] # corresponding to May, July, December

    # for algorithm in algorithms:
    #     for state in states:
    #         for wind_loc in wind_locs:
    #             for time in times:
    #                 start_time = time[0]
    #                 end_time = time[1]
    #                 if time[0] == 34560:
    #                     month = 'may'
    #                 elif time[0] == 52128:
    #                     month = 'july'
    #                 else:
    #                     month = 'dec'
    #                 print(f"\nusing {algorithm.__name__}, {month}, {state} prices, wind location {wind_loc} \n")
    #                 name = f"{algorithm.__name__}_{month}_{state}_{wind_locations[wind_loc]}"
    #                 new_row = main(algorithm, inputs, outputs, start_time, end_time, state, wind_loc, name)
    #                 outputs_summary = pd.concat([outputs_summary, pd.DataFrame(new_row, index=[0])], ignore_index=True)

    # if use_index == 0:
    #     outputs_summary.to_excel(output_summary_file_path, index=False) 
    # else:
    #     outputs_summary.to_excel(output_summary_file_path.replace('.xlsx', '_2030.xlsx'), index=False)






    print("\nusing algorithm_1, QLD prices, wind location 1 \n")
    main(algorithm_3, inputs, outputs, start_time, end_time, state_1, wind_loc_1)

    # print("\nusing algorithm_3 QLD prices, wind location 1 \n")
    # main(algorithm_3, inputs, outputs, start_time, end_time, state_1, wind_loc_1)

    # print("\nusing algorithm_2, SA prices, wind location 1 \n")
    # main(algorithm_2, inputs, outputs, start_time, end_time, state_2, wind_loc_1)

    # print("\nusing algorithm_1, QLD prices, wind location 2 \n")
    # main(algorithm_1, inputs, outputs, start_time, end_time, state_1, wind_loc_2)

    # print("\nusing algorithm_2, QLD prices, wind location 2 \n")
    # main(algorithm_2, inputs, outputs, start_time, end_time, state_1, wind_loc_2)

    # print("\nusing algorithm_1 algorithm, SA prices, wind location 2 \n")
    # main(algorithm_1, inputs, outputs, start_time, end_time, state_2, wind_loc_2)

    # print("\nusing algorithm_2 algorithm, SA prices, wind location 2 \n")
    # main(algorithm_2, inputs, outputs, start_time, end_time, state_2, wind_loc_2)
