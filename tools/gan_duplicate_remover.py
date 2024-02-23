import hashlib
import os

import sys
sys.path.insert(0,'./src')
import Constants

hashes = set()

num = 0
removed = 0

for root, dirs, files in os.walk(Constants.CLEAN_BODY_IMAGES_DIR):
    print()
    for filename in files:
        path = os.path.join(root, filename)
        digest = hashlib.sha1(open(path,'rb').read()).digest()
        if digest not in hashes:
            hashes.add(digest)
        else:
            print("Removing", path)
            os.remove(path)
            removed += 1
        if num % 1000 == 0:
            print("Finished", num, "images")
        num += 1

print(f"Went through {num} images and removed {removed} duplicates")