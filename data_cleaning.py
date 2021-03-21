import pandas as pd
# Lets play around with our data

df_ski_resorts = pd.read_csv("ski_resort_data.csv")

print(df_ski_resorts.head())
print(df_ski_resorts.groupby("Page Link").count())
print(df_ski_resorts["Name"].iloc[50:100])
