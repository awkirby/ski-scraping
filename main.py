import requests
from lxml import html
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from PIL import Image
from PIL import UnidentifiedImageError
from scraping import get_web_data, ski_resort_info_numbers
from scraping import ResortScraper
from time import sleep
import numpy as np
import pandas as pd

from aws import upload_to_aws
from cleaning_functions import CleanSkiData


def main():

    # Instantiate a list to store data
    info = []

    # Initialise Chrome Driver
    driver = webdriver.Chrome("chromedriver.exe")

    html_data = get_web_data("https://www.skiresort.info/ski-resorts/")

    # Use function in the scraping.py file to get information on the number of resorts
    first_resort, last_resort, total_resorts = ski_resort_info_numbers(html_data)

    # Calculate the number of pages to scrape
    # Assume first page 50 resorts and subsequent have 200
    # Use numpy's .ceil() function to round up page number
    pages = int(np.ceil((total_resorts - last_resort) / 200) + 1)

    # Get an initial resort number
    resort_number = first_resort

    # Loop through pages starting from 1 explicitly
    for page in range(1, pages+1, 1):

        # Get the web page again
        html_data = get_web_data("https://www.skiresort.info/ski-resorts/page/{}/".format(page))

        # Also access it with the web driver
        driver.get("https://www.skiresort.info/ski-resorts/page/{}/".format(page))
        print("Data taken from https://www.skiresort.info/ski-resorts/page/{}/".format(page))

        # Scroll down the page part 1, 30000 is not enough
        driver.execute_script(f'window.scrollBy(0, 30000)')

        # Wait a bit in case there is any loading needed
        sleep(30.0)

        # Scroll down the page part 2, should get to the end
        driver.execute_script(f'window.scrollBy(0, 50000)')
        # Wait a bit in case there is any loading needed
        sleep(30.0)

        first_resort, last_resort, total_resorts = ski_resort_info_numbers(html_data)

        print('This page has resorts {} to {} out of {}\n'.format(first_resort, last_resort, total_resorts))

        # Extract the resort data from the current website page
        # First get the element with all the resorts
        resorts = driver.find_element_by_xpath('//*[@id="resortList"]')
        # Get a list of all the resorts
        resort_list = resorts.find_elements_by_xpath("//*[starts-with(@id, 'resort')]")
        # Remove the first item in the list as this is the parent element
        # It also contains 'resort' in its ID
        resort_list = resort_list[1:]

        # Loop through each resort on list
        for resort in resort_list:

            # Instantiate ResortScraper class
            # This extracts the info in the resort card
            resort_info = ResortScraper(resort_number, resort)

            # Get the web page url
            resort_info.get_web_page_link(page)

            # Add resort content, a dictionary, to list
            info.append(resort_info.content)

            # Add to counter
            resort_number += 1

        # Save at each page in case of failure
        # Create DataFrame to save
        df_resort_info = pd.DataFrame(info)
        # Save file to allow checking
        df_resort_info.to_csv("results/ski_resort_data.csv")

    # Clean data using the CleanSkiData class
    df_clean_info = CleanSkiData(df_resort_info)

    # Get some info on the amount and quality of data
    print("Percentage of missing values in each column:\n")
    print(df_clean_info.check_null_values())

    # Remove any rows with no values for cost
    df_clean_info.drop_empty_cost_rows()

    # Split ski pass cost into more useful columns
    df_clean_info.split_cost_columns()

    # For some columns make values numerical
    num_cols = ["Elevation Change (m)", "Base Elevation (m)", "Max Elevation (m)",
                "Total Piste Length (km)", "Blue Piste Length (km)", "Red Piste Length (km)", "Black Piste Length (km)",
                "Ski Lifts"]

    df_clean_info.make_values_numerical(num_cols)

    # Remove unnecessary characters from resort names
    df_clean_info.clean_resort_names()

    # Confirm all values are unique
    df_clean_info.check_unique()

    # Save results
    df_clean_info.data.to_csv("results/ski_resort_data_clean.csv")

    upload_to_aws('results/ski_resort_data.csv', 'aicore-akirby', 'ski-scraper/ski_resort_data.csv')
    upload_to_aws('results/ski_resort_data_clean.csv', 'aicore-akirby', 'ski-scraper/ski_resort_data_clean.csv')

    driver.quit()


if __name__ == "__main__":
    main()
