import sys
sys.path.insert(0,'./src')

from Utils import find_images

import Constants


raw_count = len(find_images(Constants.RAW_BODY_IMAGES_DIR))
clean_count = len(find_images(Constants.CLEAN_BODY_IMAGES_DIR))
accept_count = len(find_images(Constants.ACCEPTED_BODY_IMAGES_DIR))

print("raw body images:", raw_count)
print("clean body images:", clean_count)
print("accepted body images:", accept_count)
