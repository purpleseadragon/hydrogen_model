# use solar generation data based on townsville solar irradiance data

# could I just do a two layer cdf for the solar generation one for total produced (by season) 
# and then again for distributing throughout the day

# or just choose a day then subsequent 12? days for either solar or wind

import pandas as pd

file_path = r"C:\Users\o_dav\Dropbox\2023_thesis\solar_data.xlsx"

df = pd.read_excel(file_path, sheet_name='vertical axis')

if __name__ == "__main__":
    print("testing...")
    # print(df.head())
    # print(df.columns)
    print(df.loc[30,'SS'])
    # print(df.iloc[2,1])
    