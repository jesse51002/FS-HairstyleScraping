import hashlib
import os

import sys
sys.path.insert(0,'./src')
import Constants

hashes = set()
names = set()

num = 0
removed = 0



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
    
if chosen == 1:        
    root_dir = Constants.RAW_BODY_IMAGES_DIR
elif chosen == 2:
    root_dir = Constants.CLEAN_BODY_IMAGES_DIR

for root, dirs, files in os.walk(root_dir):
    for filename in files: 
        path = os.path.join(root, filename)

        if ".ipynb_checkpoints" in path or Constants.BACKGROUND_REMOVED_NAME in path:
            continue

            
        is_duplicate = True
        name = os.path.basename(filename.split(".")[0])
        if name not in names:
            names.add(name)
            
            try:
                digest = hashlib.sha1(open(path,'rb').read()).digest()
            except:
                is_duplicate = False
                print("File alraedy being accesseed:", path)
                continue
            if digest not in hashes:
                hashes.add(digest)
                is_duplicate = False

        if is_duplicate:
            print("Removing", path)
            os.remove(path)
            removed += 1

        if num % 1000 == 0:
            print("Finished", num, "images")
        num += 1

print(f"Went through {num} images and removed {removed} duplicates")

