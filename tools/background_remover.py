import os
import sys
sys.path.insert(0, './src')

import cv2
import numpy as np
import torch

from human_matting.inference import remove_background
import Constants
from Utils import find_images

TARGET_BACKGROUND_DIR = os.path.join(Constants.CLEAN_BODY_IMAGES_DIR, Constants.BACKGROUND_REMOVED_NAME)
BATCH_SIZE = 5
TARGET_SIZE = 1024


def remove_images_background():
    if not os.path.isdir(TARGET_BACKGROUND_DIR):
        os.makedirs(TARGET_BACKGROUND_DIR)
    
    image_pths = set(find_images(Constants.CLEAN_BODY_IMAGES_DIR))
    already_done = set(find_images(TARGET_BACKGROUND_DIR))

    image_pths = list(image_pths - already_done)
    
    torch.no_grad()
    for i in range(0, len(image_pths), BATCH_SIZE):

        pths = image_pths[i:min(i + BATCH_SIZE, len(image_pths))]

        batched_input = np.zeros((len(pths), TARGET_SIZE, TARGET_SIZE, 3))

        for j in range(len(pths)):
            img = cv2.imread(pths[j])
            img = cv2.resize(img, (TARGET_SIZE, TARGET_SIZE), interpolation=cv2.INTER_CUBIC)
            batched_input[j] = img
            
        batched_input = batched_input[:, :, :, ::-1].copy()
        
        unscaled_imgs = torch.tensor(batched_input).permute((0, 3, 1, 2))
        unscaled_imgs = unscaled_imgs.float().to("cuda:0")
        img = unscaled_imgs / 255

        output_imgs, pred_segments = remove_background(img)
        output_imgs = output_imgs.detach().cpu().numpy().transpose(0, 2, 3, 1)
        
        for j in range(len(pths)):
            output_img = output_imgs[j]
            img_name = os.path.basename(pths[j])
            cv2.imwrite(os.path.join(TARGET_BACKGROUND_DIR, img_name), output_img)

        if i % 100 == 0:
            print(f"Removed Background {i}/{len(image_pths)}")


if __name__ == "__main__":
    remove_images_background()