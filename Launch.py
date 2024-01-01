import json
import os
import msvcrt
import cv2
import threading
from multiprocessing import Process
import matplotlib.pyplot as plt
import time
import numpy as np

from Scrapper import scrape
from Cleaner import clean_img


RAW_IMAGES_DIR = "./images/raw_images"
CLEAN_IMAGES_DIR = "./images/clean_images"
ACCEPTED_IMAGES_DIR = "./images/accepted_images"

FINIHSED_CLEAN_TXT = "./images/finished_clean"

STYLES_FILES = "./styles.txt"

STOP_FILE  = "stop.json"

directions = {
    "front": "",
    "side": " side profile"
}


# Loads Styles
styles = [] 
with open(STYLES_FILES,'r') as file:
    for x in file.readlines():
        line = x.strip()
        if len(line) < 2 or line[:2] == "--":
            continue
            
        styles.append(line)


def setStopFile(stop):
    file = open(STOP_FILE, 'w')
    json.dump({"Stop": stop}, file)
    file.close()
    
def getStop():
    with open(STOP_FILE, 'r') as file:
        stop = json.load(file)
        return(stop["Stop"])

# Scaper
def ScrapeAndClean():
    cleaned = []
    with open(FINIHSED_CLEAN_TXT, 'r') as clean_file:
        cleaned = [x.strip() for x in clean_file.readlines()]
    
    for style in styles:
        # End early if wants to exit
        if getStop():
            break
                
        for direction in directions.keys():
            
            file_txt = f"{style}:{direction}"
            
            # If already cleaned then skip it
            if file_txt in cleaned:
                break
            
            # End early if wants to exit
            if getStop():
                break
            
            
            print(f"Starting Scape and Clean for {style} in {direction}")
            
            # Creatses directories
            raw_dir = os.path.join(RAW_IMAGES_DIR, style, direction)
            if not os.path.isdir(raw_dir):
                os.makedirs(raw_dir)
                
            clean_dir = os.path.join(CLEAN_IMAGES_DIR, style, direction)
            if not os.path.isdir(clean_dir):
                os.makedirs(clean_dir)
            
            # Scapes the stlye and direction
            SCStyDir(style, direction, raw_dir, clean_dir)
            
            with open(FINIHSED_CLEAN_TXT, 'a') as clean_file:
                clean_file.write(f'\n{file_txt}')
          
            
    print("Finished Scraping and Cleaning!!!")
    
            
# Scrapes a specific 
def SCStyDir(style, direction, raw_dir, clean_dir):    
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
    scrape_thread = threading.Thread(target=scrape, args=(getStop, f"{style}{directions[direction]}", raw_dir, img_download_callback, finished_callback, hide_browser))
    scrape_thread.start()
    
    # Loop until scraping is finished and all cleaned
    while not finished["Finished"] or len(downloaded_paths) > 0 :
        # End early if wants to exit
        if getStop():
            return
        
        # if nothing has been downloaded yet then wait
        if len(downloaded_paths) == 0:
            time.sleep(0.1)
            continue
        
        # Gets image and cleans it
        raw_img = downloaded_paths[0]
        cleaned = clean_img(raw_img, direction=direction)
        
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
current_dir, cur_style, cur_direction = None, None, None
def find_image():
    global current_dir, cur_style, cur_direction
    
    cleaned = []
    if os.path.isfile(FINIHSED_CLEAN_TXT):
        with open(FINIHSED_CLEAN_TXT, 'r') as clean_file:
            cleaned = [x.strip() for x in clean_file.readlines()]
    
    if current_dir is not None:
        # Empty style direction directory handling 
        if len(os.listdir(current_dir)) == 0:
            # If its finsihed and its empty dont use this
            if file_txt in cleaned:
                current_dir = None
            else:
                return None, None, None
        # Uses the first found image
        else:
            return os.path.join(current_dir, os.listdir(current_dir)[0]), cur_style, cur_direction
    
    # Loops through all the styles folder
    for style in os.listdir(CLEAN_IMAGES_DIR):
        style_dir = os.path.join(CLEAN_IMAGES_DIR, style)
        
        # Empty style directory handling 
        if len(os.listdir(style_dir)) == 0:
            os.rmdir(style_dir)
            continue
        
        # Loops throught all the styles directions
        for direction in os.listdir(style_dir):
            file_txt = f"{style}:{direction}"
            
            direction_dir = os.path.join(style_dir, direction)
            
            # Empty style direction directory handling 
            if len(os.listdir(direction_dir)) == 0:
                # If its finsihed and its empty then delete the folder
                if file_txt in cleaned:
                    os.rmdir(direction_dir)
                continue
            
            current_dir, cur_style, cur_direction = direction_dir, style, direction
            # Uses the first found image
            return os.path.join(current_dir, os.listdir(current_dir)[0]), cur_style, cur_direction
        
    return None, None, None

    

# Style parser
# Scapes, cleans and shows cleaned image
def parse_style(scrape_clean_process): 
    
    plt.imshow(np.zeros((500,500)))
    plt.xlabel(f"Starting...")
    plt.ion()
    plt.show()
    plt.pause(0.2)
    
    while not getStop():
        img_pth, style, direction = find_image()
        
        if img_pth is None:
            if scrape_clean_process is None or not scrape_clean_process.is_alive():
                break
            
            plt.imshow(np.zeros((500,500)))
            plt.xlabel(f"Waiting for cleaned image... H to stop")
            
            if msvcrt.kbhit():
                key = msvcrt.getch().decode("utf-8")
                if key == "H" or key == "h":
                    setStopFile(True)
                    break
            
            plt.pause(0.5)
            
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
            plt.pause(0.05)
            
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
                setStopFile(True)
                break
            else:     
                print("Invalid Key, Input valid key")
            
            
        
    plt.close()
    plt.ioff()

# Starts the application
def launch():  
    # Sets stop to false
    setStopFile(False)
    
    
    print("""
          Choose mode
            1. Scrape, Clean and Accept
            2. Only Scrape and Clean
            3. Only Accept
          """)
    
    chosen = int(input())
    while chosen < 1 or chosen > 3:
        print(f"{chosen} is an invalid choice, pick a valid choice")
        chosen = int(input())
        
    # Makes importart paths
    if not os.path.exists(RAW_IMAGES_DIR):
        os.makedirs(RAW_IMAGES_DIR)
    if not os.path.exists(CLEAN_IMAGES_DIR):
        os.makedirs(CLEAN_IMAGES_DIR)
    if not os.path.exists(ACCEPTED_IMAGES_DIR):
        os.makedirs(ACCEPTED_IMAGES_DIR)
        
    scrape_clean_process = None
    if chosen == 1 or chosen == 2:
        # Scapes and downloads
        scrape_clean_process = Process(target=ScrapeAndClean, args=())
        scrape_clean_process.start()

    if chosen == 1 or chosen == 3:
        parse_style(scrape_clean_process)
    elif chosen == 2:
        while scrape_clean_process.is_alive():
            print("'H' TO STOP THE SCAPING")
            if msvcrt.kbhit():
                key = msvcrt.getch().decode("utf-8")
                if key == "H" or key == "h":
                    # Sets stop to True
                    setStopFile(True)
                    break
            
            time.sleep(1)
    
    
    print("Waiting for Clean and Scrape thread to end...")
    if scrape_clean_process is not None:
        scrape_clean_process.kill()
        scrape_clean_process.join()
            
    plt.close()  
    
if __name__ == "__main__":
    launch()
    
