import os
import time
import numpy as np


STYLES_FILES = "./styles.txt"

ATTRIBUTES = {
    "texture": ["straight", "wavy", "curly"],
    "length": ["short", "medium length", "long"],
    "fade": ["", "low fade", "mid fade", "high fade"],
    "half": ["", "half up" "half down"],
    "thick": ["thin", "regular", "thick"],
    "gender": ["men", "women"]
}

POSTFIX_ATTR = ["gender", "half"]

def get_queries():
    # Stores the results
    queries = {}
    # Gets the lines from the file
    lines = get_lines()
    
    # Counter
    combination_count = 0 
    
    for line in lines:
        line_split = line.split("|")
        
        style_name = line_split[0].strip()
        
        style_attributes = []
        if len(line_split) > 1:
            style_attributes = [s.strip() for s in line_split[1].split(",")]
        
        postfixs = []
        i = 0
        while i < len(style_attributes):
            if style_attributes[i] in POSTFIX_ATTR:
                postfixs.append(style_attributes.pop(i))
            else:
                i += 1
                
        order_arr = style_attributes + [style_name] + postfixs
        
        combinations = create_combinations("", order_arr)
        queries[style_name] = combinations
        combination_count += len(combinations)
        
        # print(style_name, combinations)
    
    print(f"Created {combination_count} different query combinations")
    
    return queries
    
# Returns all the possible combinations of the attributes for the styles
def create_combinations(cur_str, order_arr):
    if len(order_arr) == 0:
        return [cur_str.strip().lower()]
    
    cur_combs = []
    # Adds each possiblity to the tree
    if order_arr[0] in ATTRIBUTES:
        for attr in ATTRIBUTES[order_arr[0]]:
            cur_combs += create_combinations(cur_str + f"{attr} ", order_arr[1:]) 
    # Adds the raw string to the combination if its not a key in the dictionary
    else:
        cur_combs += create_combinations(cur_str + f"{order_arr[0]} ", order_arr[1:]) 
        
    return cur_combs
        

def get_lines():
    # Loads Styles lines from txt file
    # Ignoring comments
    styles = [] 
    with open(STYLES_FILES,'r') as file:
        for x in file.readlines():
            line = x.strip()
            if len(line) < 2 or line[:2] == "--" or line[0] == "#":
                continue
            styles.append(line)
    
    return styles
            
            
if __name__ == "__main__":
    get_queries()