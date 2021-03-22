import requests
from lxml import html
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from PIL import Image
from PIL import UnidentifiedImageError
from scraping import get_web_data, ski_resort_info_numbers
from driver_bot import Bot
from time import sleep
import numpy as np
import pandas as pd

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

    print('This page has resorts {} to {} out of {}'.format(first_resort, last_resort, total_resorts))

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

        # IDs as set by the website + just the id number
        resort_id = resort.get_attribute('id')
        resort_id_num = resort_id.replace("resort", "")

        # Instantiate a dictionary and store data
        resort_info = {"Access Order": resort_number, "ID": resort_id_num}

        # Get resort text
        resort_text = resort.text.splitlines()

        # The name is the first bit of text
        resort_info["Name"] = resort_text[0]

        # The location needs to be accessed specifically
        try:
            resort_info["Continent"] = resort.find_element_by_xpath(
                                '//*[@id="' + resort_id + '"]/div/div[1]/div[1]/div[2]/div/a[1]').text
        except NoSuchElementException:
            resort_info["Continent"] = None
            pass
        try:
            resort_info["Country"] = resort.find_element_by_xpath(
                                '//*[@id="' + resort_id + '"]/div/div[1]/div[1]/div[2]/div/a[2]').text
        except NoSuchElementException:
            resort_info["Country"] = None
            pass

        # Get link to more detailed information
        try:
            resort_src = resort.find_element_by_xpath('//*[@id="' + resort_id + '"]/div/div[1]/div[1]/div[1]/a')
            resort_info["Web Link"] = resort_src.get_attribute('href')
        except NoSuchElementException:
            resort_info["Web Link"] = None
            pass

        resort_info["Page Link"] = "https://www.skiresort.info/ski-resorts/page/{}/".format(page)


        # Get ratings information
        stars_path = '//*[@id="' + resort_id + '"]/div/div[2]/div[2]/table/tbody/tr[1]/td/a/div/div'
        try:
            resort_stars = resort.find_element_by_xpath(stars_path)
            resort_info["Star Rating"] = resort_stars.get_attribute('data-rank')
        except NoSuchElementException:
            resort_info["Star Rating"] = None
            pass

        # Get altitude and piste length information
        altitude_path = '//*[@id="' + resort_id + '"]/div/div[2]/div[2]/table/tbody/tr[2]/td[2]'
        try:
            altitude_info = resort.find_element_by_xpath(altitude_path)
            altitude_info = altitude_info.find_elements_by_tag_name('span')

            # Create some checks in case all values are not available
            if len(altitude_info) == 3:
                altitude_text = [a.text for a in altitude_info]
                resort_elevation_change, resort_base_height, resort_max_height = altitude_text[:3]
                resort_info["Elevation Change"] = resort_elevation_change
                resort_info["Base Elevation"] = resort_base_height
                resort_info["Max Elevation"] = resort_max_height
            else:
                resort_info["Elevation Change"] = altitude_info.text
        except NoSuchElementException:
            resort_info["Elevation Change"] = None
            pass



        # Get piste length information
        piste_path = '//*[@id="' + resort_id + '"]/div/div[2]/div[2]/table/tbody/tr[3]/td[2]'
        try:
            piste_info = resort.find_element_by_xpath(piste_path)
            piste_info = piste_info.find_elements_by_tag_name('span')

            # Create some checks
            if len(piste_info) > 1:

                piste_text = [p.text for p in piste_info]
                resort_piste_length, piste_length_blue, piste_length_red, piste_length_black = piste_text[:4]
                resort_info["Total Piste Length"] = resort_piste_length
                resort_info["Blue Piste Length"] = piste_length_blue
                resort_info["Red Piste Length"] = piste_length_red
                resort_info["Black Piste Length"] = piste_length_black

            elif len(piste_info) == 1:
                resort_info["Total Piste Length"] = piste_info[0].text
        except NoSuchElementException:
            resort_info["Total Piste Length"] = None
            resort_info["Blue Piste Length"] = None
            resort_info["Red Piste Length"] = None
            resort_info["Black Piste Length"] = None
            pass

        # Get number of ski lifts
        # Assign path because of length
        ski_lift_path = '//*[@id="' + resort_id + '"]/div/div[2]/div[2]/table/tbody/tr[4]/td[2]/ul/li'
        try:
            ski_lifts = resort.find_element_by_xpath(ski_lift_path)
            resort_info["Ski Lifts"] = ski_lifts.text
        except NoSuchElementException:
            resort_info["Ski Lifts"] = None

            # Get costs (will need some cleaning later)
        costs_path = '//*[@id="' + resort_id + '"]/div/div[2]/div[2]/table/tbody/tr[5]/td[2]'
        try:
            resort_costs = resort.find_element_by_xpath(costs_path)
            resort_info["Ski Pass Cost"] = resort_costs.text
        except NoSuchElementException:
            resort_info["Ski Pass Cost"] = None

            # Get a picture!
        try:
            photo_link = resort.find_element_by_xpath('//*[@id="' + resort_id + '"]/div/div[2]/div[1]/a/div/img')
            photo_link = photo_link.get_attribute('data-src')
            try:
                resort_info["Photo URL"] = 'https://www.skiresort.info/' + photo_link
                # Now download the photo
                img = Image.open(requests.get(resort_info["Photo URL"], stream=True).raw)
                resort_info["Photo"] = img
            except UnidentifiedImageError:
                resort_info["Photo"] = None
                pass
        except NoSuchElementException:
            resort_info["Photo URL"] = None
            resort_info["Photo"] = None
            pass

        # Add dictionary to list
        info.append(resort_info)

        # Add to counter
        resort_number += 1

    # Save at each page in case of failure
    # Create DataFrame to save
    df_resort_info = pd.DataFrame(info)
    # Save file to check TODO: Save to S3
    df_resort_info.to_csv("ski_resort_data.csv")

driver.quit()
