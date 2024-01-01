import os
from GoogleImageScraper.GoogleImageScraper import GoogleImageScraper
from GoogleImageScraper.patch import webdriver_executable



RAW_IMAGES_DIR = "./images/raw_images"

WEBDRIVER_PATH = os.path.normpath(os.path.join(os.getcwd(), "GoogleImageScraper", 'webdriver', webdriver_executable()))

SCRAPE_COUNT = 50
HIDE_BROWSER = True
MIN_RESOLUTION = (500,700)
MAX_RESOLUTION = (2000,2000)


def scrape (stop_func=None,query="long bob hairstyle", folder=RAW_IMAGES_DIR , download_callback=None, finished_callback=None, hide_browser=HIDE_BROWSER):
    image_scraper = GoogleImageScraper(WEBDRIVER_PATH,"","",SCRAPE_COUNT,HIDE_BROWSER,MIN_RESOLUTION,MAX_RESOLUTION)
    
    image_scraper.headless = hide_browser
    image_scraper.search_key = query
    image_scraper.image_path = folder
    image_scraper.img_download_callback = download_callback
    image_scraper.finish_scrape_callback = finished_callback
    
    image_scraper.find_image_urls(stop_func)
    
            
if __name__ == "__main__":
    output = os.path.join(RAW_IMAGES_DIR, "test")
    if not os.path.isdir(output):
        os.makedirs(output)
    scrape(folder=output, img_count=5)