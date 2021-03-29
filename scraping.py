import requests
from lxml import html

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException

from PIL import Image
from PIL import UnidentifiedImageError

from io import BytesIO

from aws import upload_to_aws


def get_web_data(url: str):
    """

    :param url: Takes a website URL
    :return: Returns an html object with the website content
    """
    # Use requests to get the web page
    r = requests.get(url)

    # Use the .content attribute to get the text data from the website
    # Combine this with the fromstring method in the html module
    return html.fromstring(r.content)


def ski_resort_info_numbers(data):
    """

    :param data: An html object created with .fromstring method
    :return: A tuple with the number for the first resort, last
    resort and total resorts
    """
    numbers = data.xpath('//*[@id="pagebrowser"]/div/div/span')

    # List comprehension to get each number individually
    resort_numbers = [r.text_content() for r in numbers]

    # Assign each number to the appropriate variable
    first_resort = int(resort_numbers[0])
    last_resort = int(resort_numbers[1])
    total_resorts = int(resort_numbers[2])

    return first_resort, last_resort, total_resorts

# Create a class to extract data from each resort


class ResortScraper:

    def __init__(self, resort_number, resort_card):

        # Create dictionary to store data, and add order
        self.content = {"Access Order": resort_number}

        # Extracts the ID
        self.resort_card = resort_card
        self.id = resort_card.get_attribute('id')

        # Uses the id to extract remaining attributes
        self.content["ID"] = self.id.replace("resort", "")

        self.content["Name"] = resort_card.text.splitlines()[0]

        # The location needs to be accessed specifically
        try:
            self.content["Continent"] = resort_card.find_element_by_xpath(
                '//*[@id="' + self.id + '"]/div/div[1]/div[1]/div[2]/div/a[1]').text
        except NoSuchElementException:
            self.content["Continent"] = None
            pass
        try:
            self.content["Country"] = resort_card.find_element_by_xpath(
                '//*[@id="' + self.id + '"]/div/div[1]/div[1]/div[2]/div/a[2]').text
        except NoSuchElementException:
            self.content["Country"] = None
            pass

        # Get link to more detailed information
        try:
            resort_src = resort_card.find_element_by_xpath('//*[@id="' + self.id + '"]/div/div[1]/div[1]/div[1]/a')
            self.content["Web Link"] = resort_src.get_attribute('href')
        except NoSuchElementException:
            self.content["Web Link"] = None
            pass

        # Get ratings information
        stars_path = '//*[@id="' + self.id + '"]/div/div[2]/div[2]/table/tbody/tr[1]/td/a/div/div'
        try:
            resort_stars = resort_card.find_element_by_xpath(stars_path)
            self.content["Star Rating"] = resort_stars.get_attribute('data-rank')
        except NoSuchElementException:
            self.content["Star Rating"] = None
            pass

        # Get altitude and piste length information
        altitude_path = '//*[@id="' + self.id + '"]/div/div[2]/div[2]/table/tbody/tr[2]/td[2]'
        try:
            altitude_info = resort_card.find_element_by_xpath(altitude_path)
            altitude_info = altitude_info.find_elements_by_tag_name('span')

            # Create some checks in case all values are not available
            if len(altitude_info) == 3:
                altitude_text = [a.text for a in altitude_info]
                resort_elevation_change, resort_base_height, resort_max_height = altitude_text[:3]
                self.content["Elevation Change (m)"] = resort_elevation_change
                self.content["Base Elevation (m)"] = resort_base_height
                self.content["Max Elevation (m)"] = resort_max_height
            elif len(altitude_info) == 1:
                self.content["Elevation Change (m)"] = altitude_info[0].text
                self.content["Base Elevation (m)"] = None
                self.content["Max Elevation (m)"] = None
            else:
                self.content["Elevation Change (m)"] = None
                self.content["Base Elevation (m)"] = None
                self.content["Max Elevation (m)"] = None

        except NoSuchElementException:
            self.content["Elevation Change (m)"] = None
            self.content["Base Elevation (m)"] = None
            self.content["Max Elevation (m)"] = None
            pass

        # Get piste length information
        piste_path = '//*[@id="' + self.id + '"]/div/div[2]/div[2]/table/tbody/tr[3]/td[2]'
        try:
            piste_info = resort_card.find_element_by_xpath(piste_path)
            piste_info = piste_info.find_elements_by_tag_name('span')

            # Create some checks
            if len(piste_info) > 1:

                piste_text = [p.text for p in piste_info]
                resort_piste_length, piste_length_blue, piste_length_red, piste_length_black = piste_text[:4]
                self.content["Total Piste Length (km)"] = resort_piste_length
                self.content["Blue Piste Length (km)"] = piste_length_blue
                self.content["Red Piste Length (km)"] = piste_length_red
                self.content["Black Piste Length (km)"] = piste_length_black

            elif len(piste_info) == 1:
                self.content["Total Piste Length (km)"] = piste_info[0].text
                self.content["Blue Piste Length (km)"] = None
                self.content["Red Piste Length (km)"] = None
                self.content["Black Piste Length (km)"] = None

        except NoSuchElementException:
            self.content["Total Piste Length (km)"] = None
            self.content["Blue Piste Length (km)"] = None
            self.content["Red Piste Length (km)"] = None
            self.content["Black Piste Length (km)"] = None
            pass

        # Get number of ski lifts
        # Assign path because of length
        ski_lift_path = '//*[@id="' + self.id + '"]/div/div[2]/div[2]/table/tbody/tr[4]/td[2]/ul/li'
        try:
            ski_lifts = resort_card.find_element_by_xpath(ski_lift_path)
            self.content["Ski Lifts"] = ski_lifts.text
        except NoSuchElementException:
            self.content["Ski Lifts"] = None

            # Get costs (will need some cleaning later)
        costs_path = '//*[@id="' + self.id + '"]/div/div[2]/div[2]/table/tbody/tr[5]/td[2]'
        try:
            resort_costs = resort_card.find_element_by_xpath(costs_path)
            self.content["Ski Pass Cost"] = resort_costs.text
        except NoSuchElementException:
            self.content["Ski Pass Cost"] = None

        # Get a picture!
        try:
            photo_link = resort_card.find_element_by_xpath('//*[@id="' + self.id + '"]/div/div[2]/div[1]/a/div/img')
            photo_link = photo_link.get_attribute('data-src')
            try:
                self.content["Photo URL"] = 'https://www.skiresort.info/' + photo_link
                # Now download the photo
                img = Image.open(requests.get(self.content["Photo URL"], stream=True).raw)
                # Create a name
                self.content["Photo"] = self.content["Name"].replace(" ", "_") + "_ID" + self.id + ".jpg"
                # Create an object in memory, aws needs a file to upload
                mem_obj = BytesIO()
                img.save(mem_obj, format=img.format)
                mem_obj.seek(0)
                # Store in aws bucket
                upload_to_aws(mem_obj, 'aicore-akirby', 'ski-scraper/resort-images/' + self.content["Photo"])

            except UnidentifiedImageError:
                self.content["Photo"] = None
                pass
        except NoSuchElementException:
            self.content["Photo URL"] = None
            self.content["Photo"] = None
            pass

    def get_web_page_link(self, page):
        # Gets the link where the resort was found
        self.content["Page Link"] = "https://www.skiresort.info/ski-resorts/page/{}/".format(page)
