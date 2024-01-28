import json
import os
import msvcrt
import cv2
from multiprocessing import Process, Queue, Lock
import matplotlib.pyplot as plt
import time
import numpy as np

from Preprocessor import Preprocess
from Utils import setStopFile, getStop, find_images, \
    split_hair_dict, get_file_path, delete_empty, split_body_arr
from Querys import get_queries, create_body_queries
from Scrapper import hair_scrape
from FlickrScrape.flickr_scraper import body_scrape


import Constants

# Can either be hair or body
mode = "hair"


# Style parser
# Scapes, cleans and shows cleaned image
def parse_style(accept_queue : Queue, root_clean_dir : str, root_accepted_dir : str, clean_processes : list[Process]): 
    plt.imshow(np.zeros((500,500)))
    plt.xlabel(f"Starting...")
    plt.ion()
    plt.show()
    plt.pause(0.2)
    
    while not getStop():
        img_pth = None
        if not accept_queue.empty():
            img_pth = accept_queue.get()

        # If there is not image to accept currently
        if img_pth is None:
            # Only continues images are still being cleaned
            clean_active = False
            for p in clean_processes:
                if p.is_alive():
                    clean_active = True
                    break
            if not clean_active:
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
    
        pth_list = get_file_path(img_pth, root_clean_dir[2:])
        
        # Gets the images save path
        accepted_dir = os.path.join(root_accepted_dir, pth_list)
        if not os.path.isdir(accepted_dir):
            os.makedirs(accepted_dir)
        accepted_pth = os.path.join(accepted_dir, os.path.basename(img_pth))
        
        img = cv2.imread(img_pth)
                   
        print("Displaying the image")
                
        plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        plt.xlabel(f"{pth_list} ||| 'A' to Accept ::: 'R' to reject ::: 'H' to end")
        
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
            
            # Clears key presses
            while msvcrt.kbhit():
                key = msvcrt.getch()
            
            
    print("Ending accepting GUI")
    plt.close()
    plt.ioff()

# Starts the application
def launch():  
    # makes important directories
    Constants.make_dirs()
    
    # Sets stop to false
    setStopFile(False)
    
    print("""
          Choose mode
            1. Hair
            2. Body
          """)
    
    chosen = int(input())
    while chosen < 1 or chosen > 2:
        print(f"{chosen} is an invalid choice, pick a valid choice")
        chosen = int(input())
    
    if chosen == 1:
        mode = "hair"
        root_raw_dir = Constants.RAW_IMAGES_DIR
        root_clean_dir = Constants.CLEAN_IMAGES_DIR
        root_accepted_dir = Constants.ACCEPTED_IMAGES_DIR
    elif chosen == 2:
        mode = "body"
        root_raw_dir = Constants.RAW_BODY_IMAGES_DIR
        root_clean_dir = Constants.CLEAN_BODY_IMAGES_DIR
        root_accepted_dir = Constants.ACCEPTED_BODY_IMAGES_DIR
        
    
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
    
    scrape_processes = []
    clean_processes = []
    
    # Instantiates and fills queue with current images
    clean_queue = Queue() 
    raw_images = find_images(root_raw_dir)
    for img in raw_images:
        clean_queue.put(img)
    print(f"Instantiates clean queue with {len(raw_images)} raw images")
    
    # Instantiates and fills queue with current images
    accept_queue = Queue() 
    clean_images = find_images(root_clean_dir)
    for img in clean_images:
        accept_queue.put(img)
    print(f"Instantiates accept queue with {len(clean_images)} clean images")
    
    scrape_done_lock = Lock()           
    
    if chosen == 1 or chosen == 2:
        splits = None
        scrape_func = None
        scrape_processes_count = 1
        clean_processes_count = 1
        
        if mode == "hair":
            splits = split_hair_dict(get_queries(), Constants.HAIR_SCRAPE_PROCESSES)
            scrape_func = hair_scrape
            scrape_processes_count = Constants.HAIR_SCRAPE_PROCESSES
            clean_processes_count = Constants.HAIR_CLEAN_PROCESSES
        elif mode == "body":
            splits = split_body_arr(create_body_queries(), Constants.BODY_SCRAPE_PROCESSES)
            scrape_func = body_scrape
            scrape_processes_count = Constants.BODY_SCRAPE_PROCESSES
            clean_processes_count = Constants.BODY_CLEAN_PROCESSES
        
        """ 
        for i in range(scrape_processes_count):
            # Scapes and downloads
            scrape_process = Process(target=scrape_func, args=(splits[i], clean_queue, scrape_done_lock))
            scrape_process.start()
            scrape_processes.append(scrape_process)
        """
        
        for _ in range(clean_processes_count):
            # preprocesses
            clean_process = Process(target=Preprocess, args=(clean_queue, accept_queue, root_clean_dir, root_raw_dir, mode))
            clean_process.start()
            clean_processes.append(clean_process)
        
            

    if chosen == 1 or chosen == 3:
        parse_style(accept_queue, root_clean_dir, root_accepted_dir, clean_processes)
    elif chosen == 2:
        while True:
            scraping = False
            # Checks if still scraping
            for scrape_p in scrape_processes:
                if scrape_p.is_alive():
                    scraping = True
                    break
                
            cleaning = False
            # Checks if still scraping
            for clean_p in clean_processes:
                if clean_p.is_alive():
                    cleaning = True
                    break
                
            if not cleaning and not scraping:
                break
            
            print("'H' TO STOP THE SCAPING/CLEANING")
            if msvcrt.kbhit():
                key = msvcrt.getch().decode("utf-8")
                if key == "H" or key == "h":
                    # Sets stop to True
                    setStopFile(True)
                    break
            
            time.sleep(1)
    
    
    # Ensures stop
    setStopFile(True)
    
    print("Set Stop File")
    
    # Waits for processes to end processes
    for p in scrape_processes:
        if p.is_alive():
            p.kill()
            print("Waiting for Scrape thread to end...")
        p.join()
        
    for c in clean_processes:
        if c.is_alive():
            c.kill()
            print("Waiting for Clean thread to end...")
        c.join()
        
    clean_queue.cancel_join_thread()
    accept_queue.cancel_join_thread()
             
    print("Killed Threads")
    
    # Deletes empty folders
    delete_empty(root_raw_dir)
    delete_empty(root_clean_dir)
    delete_empty(root_accepted_dir)
    
    print("ENDING...")
    
if __name__ == "__main__":
    launch()
    
