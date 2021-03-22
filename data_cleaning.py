import pandas as pd
# Lets play around with our data

df_ski_resorts = pd.read_csv("ski_resort_data.csv")

print(df_ski_resorts.head())
print(df_ski_resorts.groupby("Page Link").count())

pd.set_option('display.max_columns', 10)
pd.set_option('display.width', 500)
print(df_ski_resorts[["Name", "Country", "Ski Lifts", "Ski Pass Cost", "Total Piste Length"]].iloc[195:215])
print(df_ski_resorts.info())
# Nearly 10% of the cost values missing!
print(df_ski_resorts.isnull().mean()*100)
