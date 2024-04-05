import sys
sys.path.insert(0,'./src')

import os
import cv2
import time
import math
from Utils import getStop, get_file_path
from sixdrepnet import SixDRepNet
import matplotlib.pyplot as plt
import numpy as np

from HumanParsing.segment import body_model
from Detection import detection_model
from Clip import Clip
import Constants

ANGLE_FACE_MULT = 2


model = SixDRepNet()
detect_model = detection_model()
clip_model = DataClassifierClip()

def get_face_angle(img):
    faces = detect_model.inference(img)

    # No face detected
    if len(faces) == 0:
        print("No faces detected... Rejected")
        return None
    
    if max_faces is not None and len(faces) > 1:
        print("To many faces detected... Skipped")
        return None
    
    x, y, w, h = faces[0]

    mid_x, mid_y = int(x + w/2), int(y + h/2)
    max_size = int(max(w,h) / 2)
    scale_size = max_size * ANGLE_FACE_MULT
    
    bounds = (
            mid_x - scale_size, # left
            mid_x + scale_size, # right
            mid_y - scale_size, # bottom 
            mid_y + scale_size # top
    )
        
    l, r, b, t = bounds 
        
    l_bounds, r_bounds, b_bounds, t_bounds = (
        max(0,-1*l), 
        max(0,r - img.shape[1]),
        max(0,-1*b),
        max(0,t - img.shape[0]),
    )

    bounded_image = img[
            max(0, b): min(img.shape[0], t),
            max(0, l): min(img.shape[1], r)
            ]
        
    bounded_image = cv2.copyMakeBorder(
        bounded_image, 
        b_bounds, # bottom
        t_bounds, #top
        l_bounds,  # left
        r_bounds, # right
        cv2.BORDER_CONSTANT #borderType
        )

    pitch, yaw, roll = model.predict(bounded_image)
    return pitch, yaw, roll


def get_image_insights(img_pth, clip_model=clip_model):
    img = cv2.imread(img_pth)

    pitch, yaw, roll = get_face_angle(img)

    classifications = clip_model(img)
    for key in classifications:
        classifications[key] = classifications[key].argmax()

    classifications["HairType"] = clip_model.hair_types_list[classifications["HairType"]]
    classifications["Ethnicity"] = clip_model.ethnicites_list[classifications["HairType"]]
    classifications["Sex"] = clip_model.sex_list[classifications["HairType"]]
    
    
    
    