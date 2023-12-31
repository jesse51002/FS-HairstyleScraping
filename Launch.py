import json
import os
import msvcrt
import cv2
import threading
import matplotlib.pyplot as plt
import time
import numpy as np

from Scrapper import scrape
from Cleaner import clean_img


RAW_IMAGES_DIR = "./images/raw_images"
CLEAN_IMAGES_DIR = "./images/clean_images"
ACCEPTED_IMAGES_DIR = "./images/accepted_images"

JSON_SAVE_FILE = "./progress.json"
STYLES_FILES = "./styles.txt"

directions = {
    "front": "",
    "side": " side profile"
}

progress = {
    "scraped_styles": [],
    }

# Load progress
if os.path.isfile(JSON_SAVE_FILE):
    """
    with open(JSON_SAVE_FILE,'r') as json_file:
        progress = json.load(json_file)
    """

# Loads Styles
styles = [] 
with open(STYLES_FILES,'r') as file:
   styles = [x.strip() for x in file.readlines()]

# Scaper
def ScrapeAndClean(global_data):
    for style in styles:
        # End early if wants to exit
        if global_data["Exit"]:
            return
        
        global_data["Finished"][style] = {"Completed": False}
        
        for direction in directions.keys():
            # End early if wants to exit
            if global_data["Exit"]:
                return
            
            global_data["Finished"][style][direction] = False
            
            print(f"Starting Scape and Clean for {style} in {direction}")
            
            # Creatses directories
            raw_dir = os.path.join(RAW_IMAGES_DIR, style, direction)
            if not os.path.isdir(raw_dir):
                os.makedirs(raw_dir)
                
            clean_dir = os.path.join(CLEAN_IMAGES_DIR, style, direction)
            if not os.path.isdir(clean_dir):
                os.makedirs(clean_dir)
            
            # Scapes the stlye and direction
            SCStyDir(style, direction, raw_dir, clean_dir,global_data)
            
            global_data["Finished"][style][direction] = True
            
        global_data["Finished"][style]["Completed"] = True
    
    global_data["CleanFinished"] = True
            
    
    
            
# Scrapes a specific 
def SCStyDir(style, direction, raw_dir, clean_dir, global_data):
    
    
    # Scapes and store into the folder
    
    # Thread Lock for downloaded_paths
    lock = threading.Lock()
    downloaded_paths = []
    finished = {"Finished":False}
    
    # For Scape to tell when scraping is finsihed
    def finished_callback():
        finished["Finished"] = True
        
    # For scrape to tell when an image was downloaded
    def img_download_callback(path):
        lock.acquire()
        downloaded_paths.append(path)
        lock.release()
        
    
    # Scapes and downloads
    hide_browser = False  
    scrape_thread = threading.Thread(target=scrape, args=(global_data, f"{style}{directions[direction]}", raw_dir, img_download_callback, finished_callback, hide_browser))
    scrape_thread.start()
    
    # Loop until scraping is finished and all cleaned
    while not finished["Finished"] or len(downloaded_paths) > 0 :
        # End early if wants to exit
        if global_data["Exit"]:
            return
        
        # if nothing has been downloaded yet then wait
        if len(downloaded_paths) == 0:
            time.sleep(0.1)
            continue
        
        # Gets image and cleans it
        raw_img = downloaded_paths[0]
        cleaned = clean_img(raw_img)
        
        # Removes the raw img after it is cleaned       
        # os.remove(raw_img)
                    
        # If image was not accepted continue
        if cleaned is not None:
           # Save the cleaned image
            cv2.imwrite(os.path.join(clean_dir, os.path.basename(raw_img)), cleaned)
        
        
        # Remove the path just claned
        lock.acquire()
        downloaded_paths.pop(0)
        lock.release()
        time.sleep(0.1)
                        
    
    scrape_thread.join()
    
# Finds valid cleaned image to show to user
def find_image(global_data):
    # Loops through all the styles folder
    for style in os.listdir(CLEAN_IMAGES_DIR):
        style_dir = os.path.join(CLEAN_IMAGES_DIR, style)
        
        # Empty style directory handling 
        if len(os.listdir(style_dir)) == 0:
            # If its finsihed and its empty then delete the folder
            if style not in global_data["Finished"] or global_data["Finished"][style]["Completed"]:
                os.rmdir(style_dir)
            continue
        
        # Loops throught all the styles directions
        for direction in os.listdir(style_dir):
            direction_dir = os.path.join(style_dir, direction)
            
            # Empty style direction directory handling 
            if len(os.listdir(direction_dir)) == 0:
                # If its finsihed and its empty then delete the folder
                if direction not in global_data["Finished"][style] or  global_data["Finished"][style][direction]:
                    os.rmdir(direction_dir)
                continue
            
            # Uses the first found image
            return os.path.join(direction_dir, os.listdir(direction_dir)[0]), style, direction
        
    return None, None, None

    

# Style parser
# Scapes, cleans and shows cleaned image
def parse_style(global_data): 
    
    plt.imshow(np.zeros((500,500)))
    plt.xlabel(f"Starting...")
    plt.ion()
    plt.show()
    plt.pause(0.2)
    
    while not global_data["Exit"]:
        img_pth, style, direction = find_image(global_data)
        
        if img_pth is None:
            if global_data["CleanFinished"]:
                break
            
            plt.imshow(np.zeros((500,500)))
            plt.xlabel(f"Waiting for cleaned image... H to stop")
            
            
            if msvcrt.kbhit():
                key = msvcrt.getch().decode("utf-8")
                if key == "H" or key == "h":
                    global_data["Exit"] = True
                    break
            
            plt.pause(0.2)
            
            continue
        
        accepted_dir = os.path.join(ACCEPTED_IMAGES_DIR, style, direction)
        if not os.path.isdir(accepted_dir):
            os.makedirs(accepted_dir)
        
        img = cv2.imread(img_pth)
                
        accepted_pth = os.path.join(accepted_dir, os.path.basename(img_pth))
                
        print("Displaying the image")
                
        plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        plt.xlabel(f"{style} hairstyle in {direction} ||| 'A' to Accept ::: 'R' to reject ::: 'H' to end")
        
        while True:
            plt.pause(0.2)
            
            key = None
            if msvcrt.kbhit():
                key = msvcrt.getch().decode("utf-8")
            else:
                continue
            
            # Moves file to accepted
            if key == "A" or key == "a":
                # Write/ Overwrite accepted image
                if os.path.isfile(accepted_pth):
                    os.remove(accepted_pth)
                os.rename(img_pth, accepted_pth)
                break             
            # If rejected delete the image
            elif key == "R" or key == "r":
                os.remove(img_pth)
                break
            # Forcefully ends the application
            elif key == "H" or key == "h":
                global_data["Exit"] = True
                break
            else:     
                print("Invalid Key, Input valid key")
            
            
        
    plt.close()
    plt.ioff()

# Starts the application
def launch():
    global_data = {
        "Finished": {},
        "Exit": False,
        "CleanFinished": False
    }
    
    # Makes importart paths
    if not os.path.exists(RAW_IMAGES_DIR):
        os.makedirs(RAW_IMAGES_DIR)
    if not os.path.exists(CLEAN_IMAGES_DIR):
        os.makedirs(CLEAN_IMAGES_DIR)
    if not os.path.exists(ACCEPTED_IMAGES_DIR):
        os.makedirs(ACCEPTED_IMAGES_DIR)
    
    # Scapes and downloads
    scrape_clean_thread = threading.Thread(target=ScrapeAndClean, args=(global_data,))
    scrape_clean_thread.start()

    parse_style(global_data)
    
    
    print("Waiting for Clean and Scrape thread to end...")
    scrape_clean_thread.join()
        
    plt.close()  
    
if __name__ == "__main__":
    launch()
    
    # Write save file
    with open(JSON_SAVE_FILE,'w') as json_file:
        progress = json.dump(progress, json_file)
    
