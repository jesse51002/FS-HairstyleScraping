# Import SixDRepNet
from sixdrepnet import SixDRepNet
import cv2
import os
import matplotlib.pyplot as plt
import numpy as np

from Detection import output_bb

SIZE_FACE_MULT = 3.5
ANGLE_FACE_MULT = 2
MINIMUM_QUALITY = 0

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

# Create model
# Weights are automatically downloaded
model = SixDRepNet()


def crop_image(img, res_check=True, visualize=False):
    # Detect faces
    faces = output_bb(img)

    # No face detected
    if len(faces) == 0:
        print("No face detected... Rejected")
        return None, None
    
    if len(faces) > 1:
        print("Multiple face detected... Rejected")
        return None, None
    
    # Selects larges face
    x, y, w, h = faces[0]
    
    mid_x, mid_y = int(x + w/2), int(y + h/2)
    max_size = int(max(w,h) / 2)
    
    
    # Resolution checker
    if res_check and max_size * SIZE_FACE_MULT * 2 < MINIMUM_QUALITY:
        return None, None
    if visualize:
        print("Resolution: ", max_size * SIZE_FACE_MULT * 2)
    
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
    
    return boundedimage, angle_image
        

def clean_img(path, direction="front", visualize=False, res_check=False, angle_check=True):
    img = cv2.imread(path)
    img, angle_image = crop_image(img, visualize=visualize, res_check=res_check)
    # If image isn't valid then return 
    if img is None:
        return None

    pitch, yaw, roll = model.predict(angle_image)
    if visualize:
        print(pitch, yaw, roll)
    
    # Checks the validity of the picture face angle based on the given direction
    if angle_check:
        if abs(pitch[0]) < ALLOWED_ANGLES[direction][0, 0] or abs(pitch[0]) > ALLOWED_ANGLES[direction][0, 1]:
            print("Invalid Pitch Angle... Rejected")
            return None
        if abs(yaw[0]) < ALLOWED_ANGLES[direction][1, 0] or abs(yaw[0]) > ALLOWED_ANGLES[direction][1, 1]:
            print("Invalid Yaw Angle... Rejected")
            return None
        if abs(roll[0]) < ALLOWED_ANGLES[direction][2, 0] or abs(roll[0]) > ALLOWED_ANGLES[direction][2, 1]:
            print("Invalid Roll Angle... Rejected")
            return None
    
    # Visualize  
    if visualize:
        model.draw_axis(img, yaw, pitch, roll)
        model.draw_axis(angle_image, yaw, pitch, roll)
        
        plt.imshow(cv2.cvtColor(angle_image, cv2.COLOR_BGR2RGB))
        plt.show()
    
    print("Accepted")
    
    return img


if __name__ == "__main__":
    clean_img("images/raw_images/straight long bob hairstyle/side/straightlongbobhairstylesideprofile16.jpeg", visualize=True, res_check=False, angle_check=False)