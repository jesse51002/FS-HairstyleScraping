from pinscrape import pinscrape
import os

RAW_IMAGES_DIR = "./images/raw_images"

def scrape(query="wavy hair side profile", folder=RAW_IMAGES_DIR ,  img_count=20):

    images_dir = os.path.join(folder)
    
    details = pinscrape.scraper.scrape(query, images_dir, max_images=img_count)

    if details["isDownloaded"]:
        print(f"\nDownloading completed for {query} !!")
        print(f"\nTotal urls found: {len(details['extracted_urls'])}")
        print(f"\nTotal images downloaded (including duplicate images): {len(details['url_list'])}")
    else:
        print("\nNothing to download !!")
        
if __name__ == "__main__":
    scrape()