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
ALLOWED_ANGLES = np.array([
    [[0, 20], [70, 90]], # pitch (up and down)
    [[0, 20], [55, 90]], # yaw  (side to side)
    [[0, 20], [0, 35]], # roll (angling side to side)
])


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
        

def clean_img(path, visualize=False, res_check=True, angle_check=True):
    img = cv2.imread(path)
    img, angle_image = crop_image(img, visualize=visualize, res_check=res_check)
    # If image isn't valid then return 
    if img is None:
        return None

    pitch, yaw, roll = model.predict(angle_image)
    if visualize:
        print(pitch, yaw, roll)
    
    if angle_check:
        invalid_angle = True
        for i in range(ALLOWED_ANGLES.shape[1]):
            if abs(pitch[0]) < ALLOWED_ANGLES[0, i, 0] or abs(pitch[0]) > ALLOWED_ANGLES[1, i, 1]:
                continue
            if abs(yaw[0]) < ALLOWED_ANGLES[1, i, 0] or abs(yaw[0]) > ALLOWED_ANGLES[1, i, 1]:
                continue
            if abs(roll[0]) < ALLOWED_ANGLES[2, i, 0] or abs(roll[0]) > ALLOWED_ANGLES[2, i, 1]:
                continue
            
            # Found a valid angle
            invalid_angle = False
            break
                
        # If no valid angle was found then return None
        if invalid_angle:
            print("Invalid Angle... Rejected")
            return None
        
    
    if visualize:
        model.draw_axis(img, yaw, pitch, roll)
        model.draw_axis(angle_image, yaw, pitch, roll)
        
        plt.imshow(cv2.cvtColor(angle_image, cv2.COLOR_BGR2RGB))
        plt.show()
    
    print("Accepted")
    
    return img


if __name__ == "__main__":
    clean_img("images/raw_images/afro_bun/side/8eca278a8a15788d52ba0df6eb9a0a05.jpg", visualize=True, res_check=False, angle_check=False)