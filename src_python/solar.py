# use solar generation data based on townsville solar irradiance data

# could I just do a two layer cdf for the solar generation one for total produced (by season) 
# and then again for distributing throughout the day

# or just choose a day then subsequent 12? days for either solar or wind

import pandas as pd
import matplotlib.pyplot as plt



# coefficients list
installed_capacity = 1000 # kW
panel_efficiency = 0.2 # 20% efficiency
panel_area = 1.5 # m2
rated_power = 0.3 # kW
tilt = 38 # degrees (standard)

file_path = r"C:\Users\o_dav\Dropbox\2023_thesis\solar_data.xlsx"

df = pd.read_excel(file_path, sheet_name='vertical axis')

#energy cut off column represents the energy produced by a single panel with ~ 1.5 m2 of area and vertical axis configuration
def plot_average_energy_per_day(df):
    sum_by_time_of_day = df.groupby('HH24')['Energy Cut Off (MWh)'].sum()
    xs = [k for k in sum_by_time_of_day.keys()]
    ys = [sum_by_time_of_day[k] for k in sum_by_time_of_day.keys()]
    plt.plot(xs, ys)
    plt.xlabel('day')
    plt.ylabel('energy cut off (kWh)')
    plt.show()

# Filter by Month and day



if __name__ == "__main__":
    print("testing...")
    print(df.head())
    # print(df.columns)
    # print(df.loc[30,'SS'])
    # print(df.iloc[2,1])
    installed_capacity = 1000 # kW
    sum_by_time_of_day = df.groupby('HH24')['Energy Cut Off (MWh)'].sum()

    print(type(sum_by_time_of_day))
    print(sum_by_time_of_day.head())
    print(sum_by_time_of_day[0.0])

    plot_average_energy_per_day(df)
    