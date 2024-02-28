import os
import sys
sys.path.insert(0,'./src')

import cv2
import numpy as np
from Clip import Clip

import Constants
from Preprocessor import clip_cleaner


REMOVE_DIR = "./data/clip_removed"

def main():
    if not os.path.isdir(REMOVE_DIR):
        os.makedirs(REMOVE_DIR)
    
    clip_model = Clip()

    removed_count = 0
    total_count = 0
    
    for root, dirs, files in os.walk(Constants.CLEAN_BODY_IMAGES_DIR):
        for filename in files:
            img_pth = os.path.join(root, filename)
            if not os.path.isfile(img_pth):
                continue
            
            if ".ipynb_checkpoints" in img_pth or Constants.BACKGROUND_REMOVED_NAME in img_pth:
                continue

            img = cv2.imread(img_pth)
    
            x0, y0, x1, y1 = 0, 0, img.shape[1], img.shape[0]
    
            x_line = np.zeros((img.shape[0], 3))
            y_line = np.zeros((img.shape[1], 3))
            
            for y in range(0, img.shape[0]):
                if np.array_equal(img[y, :], y_line):
                    y0 = y
                else:
                    break
    
            for y in range(img.shape[0] - 1, y0, -1):
                if np.array_equal(img[y, :], y_line):
                    y1 = y
                else:
                    break
            for x in range(0, img.shape[1]):
                if np.array_equal(img[:, x], x_line):
                    x0 = x
                else:
                    break
    
            for x in range(img.shape[1] - 1, x0, -1):
                if np.array_equal(img[:, x], x_line):
                    x1 = x
                else:
                    break
    
            keep_image, probs_dic = clip_cleaner(img[y0:y1, x0:x1], clip_model)
    
            if not keep_image:
                print("Not keeping:", img_pth)
                print("Quality:", probs_dic["Quality"], "\nHuman:", probs_dic["Human"], "\n")

                # Moves the file to the remove directory
                os.rename(img_pth, os.path.join(REMOVE_DIR, os.path.basename(img_pth)))

                removed_count += 1

            total_count += 1

            if total_count % 100 == 0:
                print(f"Looked at {total_count} and removed {removed_count} images")

    print(f"FINISHED!!! Looked at {total_count} and removed {removed_count} images")
        
if __name__ == "__main__":
    main()
            