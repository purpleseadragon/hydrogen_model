import pandas as pd
import matplotlib.pyplot as plt


# coefficients list
installed_capacity = 1000 # kW
panel_efficiency = 0.2 # 20% efficiency
panel_area = 1.5 # m2
rated_power = 0.3 # kW
tilt = 38 # degrees (standard)

file_path = r"C:\Users\o_dav\Dropbox\2023_thesis\input_data.xlsx"

df = pd.read_excel(file_path, sheet_name='input_main')

#energy cut off column represents the energy produced by a single panel with ~ 1.5 m2 of area and vertical axis configuration
def plot_average_energy_per_day_solar(df):
    sum_by_time_of_day = df.groupby('time')['solar_output'].mean()
    xs = [k.hour + k.minute/60 + k.second/3600 for k in sum_by_time_of_day.keys()]
    ys = [sum_by_time_of_day[k] for k in sum_by_time_of_day.keys()]
    plt.plot(xs, ys)
    plt.xlabel('Time of day (hrs)')
    plt.ylabel('Average power generation (W)')
    plt.xlim(0, 24)
    plt.ylim(-5, None)
    plt.show()


def plot_average_energy_per_day(df, heading):
    sum_by_time_of_day = df.groupby('time')[heading].mean()
    xs = [k.hour + k.minute/60 + k.second/3600 for k in sum_by_time_of_day.keys()]
    ys = [sum_by_time_of_day[k] for k in sum_by_time_of_day.keys()]
    plt.plot(xs, ys)
    plt.xlabel('Time of day (hrs)')
    plt.ylabel('Average power generation (kW)')
    plt.xlim(0, 24)
    plt.ylim(-5, None)
    plt.show()


def plot_average_energy_per_month(df, heading):
    if heading != 'solar_output':
        sum_by_month = df.groupby('month')[heading].sum()*1/12*1e-3
    else:
        sum_by_month = df.groupby('month')[heading].sum()*1/12*1e-6
    # xs = [k for k in sum_by_month.keys()]
    ys = [sum_by_month[k] for k in sum_by_month.keys()]

    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct','Nov','Dec']
    plt.bar(months, ys)
    plt.xlabel('Month')
    if heading != 'solar_output':
        plt.ylabel('Total power generation (MWh)')
    else:
        plt.ylabel('Total power generation (MWh)')
    # plt.xlim(0, )
    # plt.ylim(-5, None)
    plt.show()



if __name__ == "__main__":

    heading = 'wind_output_1'
    plot_average_energy_per_month(df, heading)    

    heading = 'wind_output_2'
    plot_average_energy_per_month(df, heading)

    heading = 'solar_output'
    plot_average_energy_per_month(df, heading)
    