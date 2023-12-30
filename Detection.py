# load libraries
from huggingface_hub import hf_hub_download
from ultralytics import YOLO
from supervision import Detections
from PIL import Image
import cv2

MIN_CONFIDENCE = 0.5

# download model
model_path = hf_hub_download(repo_id="arnabdhar/YOLOv8-Face-Detection", filename="model.pt")

# load model
model = YOLO(model_path, task="detect")

# inference

def output_bb(imgs, confidence = MIN_CONFIDENCE):
    output = model(imgs)[0]
    results = Detections.from_ultralytics(output)
    
    cleaned_boxes = []
    for i in range(len(results.xyxy)):
        if results.confidence[i] > confidence:
            xyxy = results.xyxy[i]
            cleaned_boxes.append((
                int(xyxy[0]), # x
                int(xyxy[1]), # y
                int(xyxy[2]-xyxy[0]), # w
                int(xyxy[3]-xyxy[1]), # h
            ))
    
    return cleaned_boxes

if __name__ == "__main__":

    print(output_bb(cv2.imread("images/raw_images/01211a956e57e04eb992609270334da9.jpg")))