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
