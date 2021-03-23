import pandas as pd
from cleaning_functions import combine_csv
# Lets play around with our data

file_names = ["ski_resort_data_p1-7.csv", "ski_resort_data_p8-15.csv", "ski_resort_data.csv"]
df_ski_resorts = combine_csv(file_names)

pd.set_option('display.max_columns', 10)
pd.set_option('display.width', 500)

print(df_ski_resorts.head())
print(df_ski_resorts.groupby("Page Link").count())


print(df_ski_resorts[["Name", "Country", "Ski Lifts", "Ski Pass Cost", "Total Piste Length"]].iloc[195:215])
print(df_ski_resorts.info())
# Nearly 10% of the cost values missing!
print(df_ski_resorts.isnull().mean()*100)
