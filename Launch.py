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
    "scraped_styles": []
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
def ScrapeAndClean(style, raw_style_dir, clean_style_dir, callback):
    for dir in directions.keys():
        # Scapes and store into the folder
        raw_dir = os.path.join(raw_style_dir, dir)
        if not os.path.isdir(raw_dir):
            os.makedirs(raw_dir)
        
        clean_dir = os.path.join(clean_style_dir, dir)
        if not os.path.isdir(clean_dir):
            os.makedirs(clean_dir)
        
        scrape(query=f"{style} hairstyle{directions[dir]}", folder=raw_dir)
        print("FINISHED SCAPING")
            
        print("Scaped Images:", os.listdir(raw_dir))
            
        for img in os.listdir(raw_dir):
            if callback["Exit"]:
                return
                
            raw_img = os.path.join(raw_dir, img)
            cleaned = clean_img(raw_img)
                
            # os.remove(raw_img)
            
            # If image was not accepted continue
            if cleaned is None:
                continue

            cv2.imwrite(os.path.join(clean_dir, img), cleaned)
            
            time.sleep(0.1)
                
        callback["Finished"][dir] = True

         
# Style parser
# Scapes, cleans and shows cleaned image
def parse_style(style):
    end_early = False
    
    thread = None
    callback = {
            "Finished": {},
            "Exit": False,
        }
    
    raw_style_dir = os.path.join(RAW_IMAGES_DIR, style)
    if not os.path.isdir(raw_style_dir):
        os.makedirs(raw_style_dir)
        
    clean_style_dir = os.path.join(CLEAN_IMAGES_DIR, style)
    if not os.path.isdir(clean_style_dir):
        os.makedirs(clean_style_dir)
        
    accepted_style_dir = os.path.join(ACCEPTED_IMAGES_DIR, style)
    if not os.path.isdir(accepted_style_dir):
        os.makedirs(accepted_style_dir)
    
    for dir in directions.keys():
        callback["Finished"][dir] = False
        
    thread = threading.Thread(target=ScrapeAndClean, args=(style, raw_style_dir, clean_style_dir, callback,))
    thread.start()
    
    for dir in directions.keys(): 
        
        clean_dir = os.path.join(clean_style_dir, dir)
        if not os.path.isdir(clean_dir):
            os.makedirs(clean_dir)
        
        accepted_dir = os.path.join(accepted_style_dir, dir)
        if not os.path.isdir(accepted_dir):
            os.makedirs(accepted_dir)
        
        print(f"STARTING {style} in the {dir} direction")
        
        print("Creating Directories...")

        print("Scraping...")
        
        while not callback["Finished"][dir] or len(os.listdir(clean_dir)) > 0:
            if len(os.listdir(clean_dir)) == 0:
                plt.imshow(np.zeros((500,500)))
                plt.xlabel(f"Waiting... 'H' to end ::: Any other key to continue")
                plt.show()
                plt.pause(0.5)
                while msvcrt.kbhit():
                    msvcrt.getch()
                key = msvcrt.getch().decode("utf-8")
                
                if key == "H" or key == "h":
                    end_early = True
                    callback["Exit"] = True
                    break
                continue
            
            img_name = os.listdir(clean_dir)[0]
            img_pth = os.path.join(clean_dir, img_name)
            img = cv2.imread(img_pth)
            
            accepted_pth = os.path.join(accepted_dir, img_name)
            
            print("Displaying the image")
            
            plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
            plt.xlabel(f"{style} hairstyle in {dir} ||| 'A' to Accept ::: 'R' to reject ::: 'H' to end")
            plt.show()
            
            while True:
                plt.pause(0.5)
                while msvcrt.kbhit():
                    msvcrt.getch()
                key = msvcrt.getch().decode("utf-8")
                # Moves file to accepted
                if key == "A" or key == "a":
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
                    end_early = True
                    callback["Exit"] = True
                    break
                
                print("Invalid Key, Input valid key")
                                        
            if end_early:
                break      
            
        if end_early:
            break
    
    if thread.is_alive():
        thread.join()
        
def launch():
    plt.imshow(np.zeros((500,500)))
    plt.xlabel(f"Waiting... 'H' to end ::: Any other key to continue")
    plt.ion()
    plt.show()
    plt.pause(0.5)

    for style in styles:
        if styles in progress["scraped_styles"]:
            print(f"Already completed {style}. Skipping...")
            continue
        
        print(f"Starting {style}. \n Any key to continue or 'H' to stop...")
        while msvcrt.kbhit():
            msvcrt.getch()
        key = msvcrt.getch().decode("utf-8")
        if key == "h" or key == "H":
            break
        
        parse_style(style)
        progress["scraped_styles"].append(style)
        
    plt.close()
    
if __name__ == "__main__":
    launch()
    
# Write save file
with open(JSON_SAVE_FILE,'w') as json_file:
    progress = json.dump(progress, json_file)
   
