An example of a web scraping program using Selenium with ChromeDrive

The program extracts information on every ski resort in the world
(almost 6000) from the www.skiresort.info webpage.

The following information is taken:

* **Name**
* **Star Rating**
* **Continent**
* **Country**
* **Number of ski lifts**
* **Length of pistes** (with colour breakdown)
* **Cost of ski pass** in local currency and euros
* **Elevation details**

Images from the website are also taken and saved to AWS S3 cloud service

The scraping function is accessed from main.py. Data cleaning functions are 
applied to the raw data to make the output more user-friendly.

April 2021