import hashlib
import os

import sys
sys.path.insert(0,'./src')
import Constants

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
            print(f"'confirm' was typed incorrectly. Restart...")
            chosen = -1
            continue
    else:
        print(f"{chosen} is an invalid choice, pick a valid choice")

root_dir = None
check_order_file = None

if chosen == 1:        
    root_dir = Constants.RAW_BODY_IMAGES_DIR
    check_order_file = Constants.FINIHSED_BODY_RAW_TXT
elif chosen == 2:
    root_dir = Constants.CLEAN_BODY_IMAGES_DIR
    check_order_file = Constants.FINIHSED_BODY_CLEAN_UPLOAD


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

num = 0
removed = 0

for folder in folder_order:
    folder_path = os.path.join(root_dir, folder)

    if not os.path.isdir(folder_path):
        print(folder, "doesn't exist")
        continue

    for root, dirs, files in os.walk(folder_path):
        for filename in files:
            
            path = os.path.join(root, filename)
    
            if ".ipynb_checkpoints" in path or Constants.BACKGROUND_REMOVED_NAME in path:
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
                except:
                    print("File cant be removed, alraedy being accesseed:", path)
                
    
            if num % 1000 == 0:
                print("Finished", num, "images")
            num += 1

print(f"Went through {num} images and removed {removed} duplicates")

