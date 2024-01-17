import os
import cv2
import time
from Utils import getStop, get_file_path
from sixdrepnet import SixDRepNet
import matplotlib.pyplot as plt
import numpy as np

from Detection import output_bb

SIZE_FACE_MULT = 2.75
ANGLE_FACE_MULT = 2
MINIMUM_QUALITY = 300

# This is mirrored to negative angles as well
# Format
# [ 
#   pitch (up and down),
#   yaw  (side to side),
#   roll (angling side to side)
# ]

ALLOWED_ANGLES = {
    "front": np.array([[0, 13], [0, 13], [0, 13]]),
    "side": np.array([[0, 35], [25, 90], [0, 35]])
    }


def crop_image(img, res_check=True, visualize=False, bottom_extend=False, max_faces=None):
    # Detect faces
    faces = output_bb(img)

    # No face detected
    if len(faces) == 0:
        print("No faces detected... Rejected")
        return None, None
    
    if max_faces is not None and len(faces) > max_faces:
        print("To many faces detected... Rejected")
        return None, None
    
    bounded_images = []
    angle_images = []
    
    for x, y, w, h in faces:  
        
        mid_x, mid_y = int(x + w/2), int(y + h/2)
        max_size = int(max(w,h) / 2)
        
        
        # Resolution checker
        if res_check and max_size * SIZE_FACE_MULT * 2 < MINIMUM_QUALITY:
            print("Resolution wasnt big enough... Rejected")
            continue
        if visualize:
            print("Resolution: ", max_size * SIZE_FACE_MULT * 2)
            print("Face Resolution: ", max_size * 2)
        
        bounds =  (
            int(mid_x - max_size * SIZE_FACE_MULT), # Bottom
            int(mid_x + max_size * SIZE_FACE_MULT), # top
            int(mid_y - max_size * SIZE_FACE_MULT), # left
            int(mid_y + max_size * SIZE_FACE_MULT) # right
        )
        
        """
        print("Mid:", (mid_x, mid_y))
        print("shape:", img.shape)
        print("Size:", max_size * SIZE_FACE_MULT)
        """
        
        b,t,l,r = bounds 
        
        b_bounds, t_bounds, l_bounds, r_bounds = (
            max(0,-1*b),
            max(0,t - img.shape[1]),
            max(0,-1*l), 
            max(0,r - img.shape[0])
            )
        
        if bottom_extend and r_bounds > 0:
            print("Bottom doesnt reach... Rejected")
            continue
            
        
        boundedimage = img[
            max(0, l): min(img.shape[0], r),
            max(0, b): min(img.shape[1], t)
            ]
        
        boundedimage = cv2.copyMakeBorder(
            boundedimage, 
            l_bounds,  # left
            r_bounds, # right
            b_bounds, # bottom
            t_bounds, #top
            cv2.BORDER_CONSTANT #borderType
            )
        
        
        # Cropped Image for angle detection
        angle_size = int(ANGLE_FACE_MULT * max_size)
        angle_center = int(max_size * SIZE_FACE_MULT)
        angle_image = boundedimage[angle_center -angle_size:angle_center + angle_size, angle_center -angle_size:angle_center + angle_size].copy()
        
        if visualize:
            # Draw bounding boxes
            face_start_x, face_start_y  = (int(angle_center - w /2), int(angle_center - h /2))
            cv2.rectangle(boundedimage, (face_start_x, face_start_y), (face_start_x + w, face_start_y + h), (255, 0, 0), 2)
            
        bounded_images.append(boundedimage)
        angle_images.append(angle_image)
    
    if len(bounded_images) == 0:
        bounded_images, angle_images = None, None
    
    return bounded_images, angle_images
        

def clean_img(model, path, visualize=False, res_check=False, save_path=None, bottom_extend=False, max_faces=None):
    raw_img = cv2.imread(path)
    imgs, angle_images = crop_image(raw_img, visualize=visualize, res_check=res_check, bottom_extend=bottom_extend, max_faces=max_faces)
    # If image isn't valid then return 
    if imgs is None:
        return None, None
    
    imgs_final = []
    directions = []
    
    for i in range(len(imgs)):
        img = imgs[i]
        angle_image = angle_images[i]
        
        pitch, yaw, roll = model.predict(angle_image)
        if visualize:
            print(pitch, yaw, roll)
        
        # Finds valid angle that hte image fits
        valid_direction = None
        
        # Checks the validity of the picture face angle based on the given direction
        for direction in ALLOWED_ANGLES:
            if abs(pitch[0]) < ALLOWED_ANGLES[direction][0, 0] or abs(pitch[0]) > ALLOWED_ANGLES[direction][0, 1]:
                continue
            if abs(yaw[0]) < ALLOWED_ANGLES[direction][1, 0] or abs(yaw[0]) > ALLOWED_ANGLES[direction][1, 1]:
                continue
            if abs(roll[0]) < ALLOWED_ANGLES[direction][2, 0] or abs(roll[0]) > ALLOWED_ANGLES[direction][2, 1]:
                continue
            valid_direction = direction
            break
            
        
        # Visualize  
        if visualize:
            model.draw_axis(img, yaw, pitch, roll)
            model.draw_axis(angle_image, yaw, pitch, roll)
            
            plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
            plt.show()
        
        print("Accepted")
        
        if save_path is not None:
            cv2.imwrite(save_path, img)
        
        imgs_final.append(img)
        directions.append(valid_direction)
        
    
    return imgs_final, directions


    # Preprocessor
def Preprocess(clean_queue, accept_queue, root_clean_dir, root_raw_dir):    
    # Create model
    # Weights are automatically downloaded
    model = SixDRepNet()
    
    # Loop until errors out from timeout (nothing more to clean)
    while True:
        # End early if wants to exit
        if getStop():
            return
        
        # Gets image and cleans it
        raw_img = clean_queue.get(timeout=60)
        if not os.path.isfile(raw_img):
            continue
        
        cleaned_imgs, directions = clean_img(model, raw_img, res_check=True)
        
        # Removes the raw img after it is cleaned       
        os.remove(raw_img)
        
        
        # If image was not accepted continue
        if cleaned_imgs is None or directions is None:
            continue
        
        for i in range(len(cleaned_imgs)):
            cleaned = cleaned_imgs[i]
            direction = directions[i]
            
            if direction is None:
                continue
            
            # Gets the relative path to raw root directory
            pth_list = get_file_path(raw_img, root_raw_dir[2:])
            # Gets the images save path
            clean_dir = os.path.join(root_clean_dir, pth_list, direction)
            if not os.path.isdir(clean_dir):
                os.makedirs(clean_dir)
            
            # Creates the name
            base_split = os.path.basename(raw_img).split(".")
            new_name = ".".join(base_split[:-1]) + str(i) + "." + base_split[-1]
            final_pth = os.path.join(clean_dir, new_name)
            
            # Save the cleaned image
            cv2.imwrite(final_pth, cleaned)
            
            # Adds to the queue for acceptance
            if accept_queue is not None:
                accept_queue.put(final_pth)
       
                        
if __name__ == "__main__":
    # Create model
    # Weights are automatically downloaded
    model = SixDRepNet()
    # clean_img("images/raw_images/straight long bob hairstyle/side/straightlongbobhairstylesideprofile16.jpeg", visualize=True, res_check=False, angle_check=False)
    clean_img(model, "images/R2_1105.png", visualize=True, res_check=False, bottom_extend=True)
    
