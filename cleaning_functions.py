import pandas as pd

# Helpful functions for data cleaning

def combine_csv(csv_file_path: list):
    """
    This function imports csv files and
    combines them into a single DataFrame
    :param: List of file paths to csvs
    :return: Concatenated DataFrame
    """

    csv_files = [pd.read_csv(f, index_col=0, usecols=range(1, 20)) for f in csv_file_path]

    return pd.concat(csv_files)


class CleanSkiData:
    """
    Contains a number of helpful functions to clean the data
    extracted from skiresort.info using the main.py script
    """
    def check_null_values(self):
        # returns a breakdown of null values in each column
        return self.isnull().mean() * 100

    def drop_empty_cost_rows(self, column="Ski Pass Cost"):
        # For a given column, drops any rows with null values
        # Default is Ski Pass Cost, because it is a key value for the project
        return self.dropna(subset=[column])

    def split_cost_columns(self):
        # Split out the cost into 3 columns
        # "Currency"
        # "Ski Pass Cost"
        # "Cost in Euros"

        # Step 1 - Replace ",-" and " / approx."
        self["Ski Pass Cost"] = self["Ski Pass Cost"].str.replace(",-", "", regex=False)
        self["Ski Pass Cost"] = self["Ski Pass Cost"].str.replace(" / approx.", "", regex=False)

        # Split the strings
        self["Ski Pass Cost"] = self["Ski Pass Cost"].str.split()

        # Now create the new columns
        # The first value in the list is the currency
        # The second value the original cost
        # The -1 value shall be the cost in euros
        self["Currency"] = self["Ski Pass Cost"].str[0]
        self["Cost in Euros"] = self["Ski Pass Cost"].str[-1]
        self["Ski Pass Cost"] = self["Ski Pass Cost"].str[1]

    def make_ski_lifts_numerical(self):
        # Modifies the information in ski lifts column
        # Leaves only the numerical value
        self["Ski Lifts"] = self["Ski Lifts"].str.split().str[0]

    def clean_resort_names(self):
        # Removes the phrase "temporarily closed" from ski resort names
        # This information is unnecessary
        self["Name"] = self["Name"].str.replace(" (temporarily closed)", "")

    def check_unique(self):
        # Confirms there are no duplicate resorts
        if len(self["Name"].unique()) == len(self["Name"]):
            return "No duplicate resorts!"
        else:
            return "There are duplicate resorts!"
