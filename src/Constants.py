import os

# Faces files
RAW_IMAGES_DIR = "./images/raw_images"
CLEAN_IMAGES_DIR = "./images/clean_images"
ACCEPTED_IMAGES_DIR = "./images/accepted_images"

FINIHSED_RAW_TXT = "./images/finished_raw"

# Body files
RAW_BODY_IMAGES_DIR = "./data/raw_images"
CLEAN_BODY_IMAGES_DIR = "./data/clean_images"
ACCEPTED_BODY_IMAGES_DIR = "./data/accepted_images"

FINIHSED_BODY_RAW_TXT = "./data/finished_raw"


# Stop file
STOP_FILE  = "stop.json"

SCRAPE_ADDS = ["", "front profile", "side profile"]


# Process counts
HAIR_CLEAN_PROCESSES = 1
HAIR_SCRAPE_PROCESSES = 12


def make_dirs():
    # Makes hair importart paths
    if not os.path.exists(RAW_IMAGES_DIR):
        os.makedirs(RAW_IMAGES_DIR)
    if not os.path.exists(CLEAN_IMAGES_DIR):
        os.makedirs(CLEAN_IMAGES_DIR)
    if not os.path.exists(ACCEPTED_IMAGES_DIR):
        os.makedirs(ACCEPTED_IMAGES_DIR)
    
    
    # Makes body importart paths
    if not os.path.exists(RAW_BODY_IMAGES_DIR):
        os.makedirs(RAW_BODY_IMAGES_DIR)
    if not os.path.exists(CLEAN_BODY_IMAGES_DIR):
        os.makedirs(CLEAN_BODY_IMAGES_DIR)
    if not os.path.exists(ACCEPTED_BODY_IMAGES_DIR):
        os.makedirs(ACCEPTED_BODY_IMAGES_DIR)