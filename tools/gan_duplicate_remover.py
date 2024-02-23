import hashlib
import os

import sys
sys.path.insert(0,'./src')
import Constants

hashes = set()
names = set()

num = 0
removed = 0

for root, dirs, files in os.walk(Constants.CLEAN_BODY_IMAGES_DIR):
    for filename in files: 
        path = os.path.join(root, filename)

        if ".ipynb_checkpoints" in path:
            continue

        name = os.path.basename(filename.split(".")[0])
        
        digest = hashlib.sha1(open(path,'rb').read()).digest()
        if digest not in hashes and name not in names:
            hashes.add(digest)
            names.add(name)
        else:
            print("Removing", path)
            os.remove(path)
            removed += 1
        if num % 1000 == 0:
            print("Finished", num, "images")
        num += 1

print(f"Went through {num} images and removed {removed} duplicates")