import requests
from lxml import html
from selenium import webdriver
from PIL import Image
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
pages = 5 #int(np.ceil((total_resorts - last_resort) / 200) + 1)

# Get an initial resort number
resort_number = first_resort

# Loop through pages starting from 1 explicitly
for page in range(1, pages+1, 1):

    # Get the web page again
    html_data = get_web_data("https://www.skiresort.info/ski-resorts/page/{}/".format(page))

    # Also access it with the web driver
    driver.get("https://www.skiresort.info/ski-resorts/page/{}/".format(page))
    print("Data taken from https://www.skiresort.info/ski-resorts/page/{}/".format(page))

    # Scroll down the page, 10000 was not enough
    driver.execute_script(f'window.scrollBy(0, 30000)')

    # Wait a bit in case there is any loading needed, increase later
    sleep(3.0)

    first_resort, last_resort, total_resorts = ski_resort_info_numbers(html_data)

    print('This page has resorts {} to {} out of {}'.format(first_resort, last_resort, total_resorts))

    # Extract the resort data from the current website page
    #resorts = driver.find_element_by_class_name('panel.panel-default.resort-list-item resort-list-item-image--big')
    resorts = driver.find_element_by_xpath('//*[@id="resortList"]')#/div')
    resorts = html.fromstring(resorts.text)

    # Loop through each resort on list
    for resort in resorts:
        print(resort.text)
        break
        # IDs as set by the website + just the id number
        resort_id = resort.get("id")
        resort_id_num = resort_id.replace("resort", "")

        # Instantiate a dictionary and store data
        resort_info = {"Access Order": resort_number, "ID": resort_id_num}

        # Get resort name

        # There are two cases (so far), because of fonts
        #if resort.xpath('//*[@id="' + resort_id + '"]/div/div[1]/div[1]/div[1]/a/text()')[0] isempty:
        resort_name = resort.xpath('//*[@id="' + resort_id + '"]/div/div[1]/div[1]/div[1]/a/text()')[0]
        resort_info["Name"] = resort_name

        # Get link to more detailed information
        resort_src = resort.xpath('//*[@id="' + resort_id + '"]/div/div[1]/div[1]/div[1]/a')[0].get('href')
        resort_info["Web Link"] = resort_src
        resort_info["Page Link"] = "https://www.skiresort.info/ski-resorts/page/{}/".format(page)

        # Get location information
        resort_continent = resort.xpath('//*[@id="' + resort_id + '"]/div/div[1]/div[1]/div[2]/div/a[1]/text()')[0]
        resort_country = resort.xpath('//*[@id="' + resort_id + '"]/div/div[1]/div[1]/div[2]/div/a[2]/text()')[0]
        resort_info["Continent"] = resort_continent
        resort_info["Country"] = resort_country

        # Get ratings information
        stars_path = '//*[@id="' + resort_id + '"]/div/div[2]/div[2]/table/tbody/tr[1]/td/a/div'
        resort_stars = resort.xpath(stars_path)[0].get('title')[0]
        resort_info["Star Rating"] = resort_stars

        # Get altitude information
        altitude_info = resort.xpath('//*[@id="' + resort_id + '"]/div/div[2]/div[2]/table/tbody/tr[2]/td[2]')[0]
        altitude_text = [a.text for a in altitude_info]
        resort_elevation_change, resort_base_height, resort_max_height = altitude_text[:3]
        resort_info["Elevation Change"] = resort_elevation_change
        resort_info["Base Elevation"] = resort_base_height
        resort_info["Max Elevation"] = resort_max_height

        # Get piste length information
        piste_info = resort.xpath('//*[@id="' + resort_id + '"]/div/div[2]/div[2]/table/tbody/tr[3]/td[2]')[0]
        piste_text = [p.text for p in piste_info]
        resort_piste_length, piste_length_blue, piste_length_red, piste_length_black = piste_text[:4]
        resort_info["Total Piste Length"] = resort_piste_length
        resort_info["Blue Piste Length"] = piste_length_blue
        resort_info["Red Piste Length"] = piste_length_red
        resort_info["Black Piste Length"] = piste_length_black

        # Get number of ski lifts
        # Assign path because of length
        ski_lift_path = '//*[@id="' + resort_id + '"]/div/div[2]/div[2]/table/tbody/tr[4]/td[2]/ul/li/text()'
        ski_lifts = resort.xpath(ski_lift_path)[0]
        resort_info["Total Ski Lifts"] = ski_lifts.replace(" ski lifts", "")

        # Get costs (will need some cleaning later)
        costs_path = '//*[@id="' + resort_id + '"]/div/div[2]/div[2]/table/tbody/tr[5]/td[2]/text()'
        resort_costs = resort.xpath(costs_path)[0]
        resort_info["Ski Pass Cost"] = resort_costs

        # Get a picture!
        photo_link = resort.xpath('//*[@id="' + resort_id + '"]/div/div[2]/div[1]/a/div/img')[0].get('data-src')
        resort_info["Photo URL"] = 'https://www.skiresort.info/' + photo_link
        # Now download the photo
        img = Image.open(requests.get(resort_info["Photo URL"], stream=True).raw)
        resort_info["Photo"] = img

        # Add dictionary to list
        info.append(resort_info)

        # Add to counter
        resort_number += 1

# Create DataFrame to save
df_resort_info = pd.DataFrame(info)
# Save file to check TODO: Save to S3
df_resort_info.to_csv("ski_resort_data.csv")

driver.quit()
