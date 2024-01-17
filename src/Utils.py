import json
import os
import math
import Constants
import re


img_types = ['png', 'jpeg', 'jpg', 'webp']

def setStopFile(stop : bool):
    file = open(Constants.STOP_FILE, 'w')
    json.dump({"Stop": stop}, file)
    file.close()
    
def getStop():
    with open(Constants.STOP_FILE, 'r') as file:
        stop = json.load(file)
        return(stop["Stop"])

# Finds all the images in a directory
def find_images(path: str):
    img_list = []
    
    if os.path.isdir(path):
        for sub in os.listdir(path):
            img_list += find_images(os.path.join(path, sub))
    else:
        name = os.path.basename(path)
        file_type = name.split(".")[-1]
        if file_type in img_types:
            img_list.append(path)
        
    
    return img_list

# Finds all the images in a directory
def delete_empty(path: str):    
    if os.path.isfile(path):
        return
    if os.path.isdir(path):
        pth_list = os.listdir(path)
        if len(pth_list) == 0:
            os.rmdir(path)
            return
        
        for p in pth_list:
            delete_empty(os.path.join(path, p))
        
        if len(os.listdir(path)) == 0:
            os.rmdir(path)

    
    
def split_hair_dict(dict: dict, count : int):
    # Reads file if exists
    already_scraped = []
    if os.path.isfile(Constants.FINIHSED_RAW_TXT):
        with open(Constants.FINIHSED_RAW_TXT, 'r') as scrape_file:
            already_scraped = [x.strip() for x in scrape_file.readlines()]
    
    # Removes values that have already been scraped
    for style in dict.keys():
        i = 0
        while i < len(dict[style]):
            style_type = dict[style][i]
            together = f'\n{style}/{style_type}'
                
            if together in already_scraped:
                dict[style].pop(i)
            else:
                i += 1
                    
        # Removes style if all the style_types have been completed
        if len(dict[style]) == 0:
            del dict[style]
        
        
    split_dicts = [{} for _ in range(count)]
    
    keys = list(dict.keys())
    # calcualtes the amount of keys per dictionary
    amount_per = math.ceil(len(keys) / count)
    
    # splits the dictionary
    global_i = 0
    for i in range(count):
        for _ in range(amount_per):
            if global_i >= len(keys):
                break
            split_dicts[i][keys[global_i]] = dict[keys[global_i]]
            global_i += 1
    
    return split_dicts

def get_file_path(pth : str, root_dir : str):
    clean_idx = pth.index(root_dir)
    pth_start = clean_idx + len(root_dir) + 1
    pth_list = "/".join(re.split('[/\\\\]', pth[pth_start:])[:-1])
    return pth_list