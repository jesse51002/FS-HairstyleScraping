import hashlib
import os

import sys
sys.path.insert(0,'./src')
import Constants
import shutil
import pickle 

from aws_s3_downloader import download_aws_folder, get_download_folders
from aws_s3_uploader import upload_aws_folder



chosen = -1
while chosen < 1 or chosen > 2:
    print("""
    Delete already uploaded folder from?
        1. Raw
        2. Clean
        """)
    
    chosen = int(input())

    if chosen >= 1 or chosen <= 2:
        print(f"""
        You have picked option {chosen}, are sure this action is irreversible\n
        Type 'confirm' to proceed
        """)

        if input() != "confirm":
            print("'confirm' was typed incorrectly. Restart...")
            chosen = -1
            continue
    else:
        print(f"{chosen} is an invalid choice, pick a valid choice")

root_dir = None
check_order_file = None

pickle_file = None

if chosen == 1:
    root_dir = Constants.RAW_BODY_IMAGES_DIR
    check_order_file = Constants.FINIHSED_BODY_RAW_TXT
    pickle_file = "./data/duplicate_hash_store_raw.pickle"
elif chosen == 2:
    root_dir = Constants.CLEAN_BODY_IMAGES_DIR
    check_order_file = Constants.FINIHSED_BODY_CLEAN_UPLOAD
    pickle_file = "./data/duplicate_hash_store.pickle"


folder_order = []
if check_order_file is not None:
    # Creates file if it doesnt exist
    if not os.path.isfile(check_order_file):
        file = open(check_order_file, 'w')
        file.close()
             
    # Instanties the finihsed folders from file
    with open(check_order_file, 'r') as file:
        for x in file.readlines():
            line = x.strip()
            if len(line) == 0:
                continue
            folder_order.append(line)

    for folder in os.listdir(root_dir):
        if folder not in folder_order:
            folder_order.append(folder)
else:
    folder_order = os.listdir(root_dir)

hashes = set()
names = set()
folders_finished = set()

if chosen == 2:
    rel_base = root_dir.split("/")[-1] + "/"
    download_folders = get_download_folders(rel_base)

    for i in range(len(download_folders)):
        download_folders[i] = download_folders[i].split("/")[-1][:-4]

    for folder in folder_order:
        if folder not in download_folders:
            folder_order.remove(folder)

if os.path.isfile(pickle_file):
    with open(pickle_file, "rb") as input_file:
        stored_data = pickle.load(input_file)
    hashes = stored_data["hashes"]
    names = stored_data["names"]
    folders_finished = stored_data["folders_finished"]

num = 0
removed = 0

for folder in folder_order:
    folder_path = os.path.join(root_dir, folder)
    if folder in folders_finished:
        print(folder, "was already parsed in the pickle file")
        continue
    
    folder_downloaded = False
    if not os.path.isdir(folder_path):
        if chosen == 1 or "0background_free" in folder:
            print(folder, "doesn't exist")
            continue
        elif chosen == 2:
            key = rel_base + folder + ".zip"
            zip_process_thread = download_aws_folder(folder_path, key)
            zip_process_thread.join()
            folder_downloaded = True

    duplicate_found = False
    for root, dirs, files in os.walk(folder_path):
        for filename in files:
            
            path = os.path.join(root, filename)
    
            if ".ipynb_checkpoints" in path:
                continue
    
            is_duplicate = True
            name = os.path.basename(filename.split(".")[0])
            if name not in names:
                names.add(name)
                
                try:
                    digest = hashlib.sha1(open(path, 'rb').read()).digest()
                except:
                    is_duplicate = False
                    print("File alraedy being accesseed:", path)
                    continue
                if digest not in hashes:
                    hashes.add(digest)
                    is_duplicate = False
    
            if is_duplicate:
                print("Removing", path)
                try:
                    os.remove(path)
                    removed += 1
                    duplicate_found = True
                except:
                    print("File cant be removed, alraedy being accesseed:", path)
                    
            if num % 1000 == 0:
                print("Finished", num, "images")
            num += 1

    if folder_downloaded:
        if duplicate_found:
            upload_aws_folder(folder_path, os.path.join(rel_base, folder))
            
        shutil.rmtree(folder_path)

    # Adds to finished folder to be saved in picke file later
    folders_finished.add(folder)
            
            
print(f"Went through {num} images and removed {removed} duplicates")

print("Saving snapshot to pickle")
# Open a file and use dump()
with open(pickle_file, 'wb') as file:
    # A new file will be created
    pickle.dump({
        "hashes": hashes,
        "names": names,
        "folders_finished": folders_finished
    }, file)
print("Finished saving snapshot to pickle")
