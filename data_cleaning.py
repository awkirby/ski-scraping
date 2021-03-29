import pandas as pd

from cleaning_functions import combine_csv

# Lets play around with our data
# This script is purely for exploratory purposes
# It has been implemented in the CleanSkiClass

df_ski_resorts = pd.read_csv("ski_resort_data_full.csv", index_col=0, usecols=range(1, 18))

pd.set_option('display.max_columns', 10)
pd.set_option('display.max_rows', 40)
pd.set_option('display.width', 500)

print(df_ski_resorts.head())
print(df_ski_resorts.groupby("Page Link").count())


print(df_ski_resorts[["Name", "Country", "Ski Lifts", "Ski Pass Cost", "Total Piste Length"]].iloc[195:215])
print(df_ski_resorts.info())
# Check for missing values
print(df_ski_resorts.isnull().mean()*100)

# Reviewing the results, 42% of the cost values are missing
# The aim of the ML tool will be to estimate the cost.
# Check if the missing cost entries have a more detailed website
# Otherwise remove them as they won't be useful
df_ski_resorts_no_link = df_ski_resorts.dropna(subset=["Web Link"])
print(df_ski_resorts_no_link.isnull().mean()*100)

# Having dropped the rows with no weblinks
# Demonstrated by no nulls in that column

# The number of missing ski pass costs remain the same
# Potentially these could be captured by using the more detailed links
# Future effort maybe?

# Remove rows with no cost values as they cannot be used in the training
df_ski_resorts = df_ski_resorts.dropna(subset=["Ski Pass Cost"])
# Review new breakdown
print(df_ski_resorts.isnull().mean()*100)

# Now split out the cost into 3 columns
# "Currency"
# "Ski Pass Cost"
# "Cost in Euros"

# Step 1 - Replace ",-" and " / approx."
df_ski_resorts["Ski Pass Cost"] = df_ski_resorts["Ski Pass Cost"].str.replace(",-", "", regex=False)
df_ski_resorts["Ski Pass Cost"] = df_ski_resorts["Ski Pass Cost"].str.replace(" / approx.", "", regex=False)
print(df_ski_resorts["Ski Pass Cost"].iloc[195:215])

# Split the strings
df_ski_resorts["Ski Pass Cost"] = df_ski_resorts["Ski Pass Cost"].str.split()
print(df_ski_resorts["Ski Pass Cost"].iloc[195:215])

# Now create the new columns
# The first value in the list is the currency
# The second value the original cost
# The -1 value shall be the cost in euros
df_ski_resorts["Currency"] = df_ski_resorts["Ski Pass Cost"].str[0]
df_ski_resorts["Cost in Euros"] = df_ski_resorts["Ski Pass Cost"].str[-1]
df_ski_resorts["Ski Pass Cost"] = df_ski_resorts["Ski Pass Cost"].str[1]

# Reviewing the results this has worked perfectly!
print(df_ski_resorts[["Currency", "Ski Pass Cost", "Cost in Euros"]].iloc[190:210])

# Now get only the numerical value of the ski lifts
df_ski_resorts["Ski Lifts"] = df_ski_resorts["Ski Lifts"].str.split().str[0]
print(df_ski_resorts["Ski Lifts"])

# Some of the ski resorts have (temporarily closed) in the name
df_ski_resorts["Name"] = df_ski_resorts["Name"].str.replace(" (temporarily closed)", "")

# Check for duplicates
print(len(df_ski_resorts["Name"].unique()) / len(df_ski_resorts["Name"]))
# Great there are none!
