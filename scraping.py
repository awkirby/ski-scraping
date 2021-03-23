import requests
from lxml import html
from PIL import Image
from selenium import webdriver


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
