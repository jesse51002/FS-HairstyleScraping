from PIL import Image
import cv2
import torch
import clip

from Model import Model


class Clip(Model):
    
    def __init__(self):
        # load model
        self.model, self.preprocess = clip.load("ViT-B/16", device="cpu")
        self.model = self.model.cuda()

        # Quality tokenizer
        self.quality_text = clip.tokenize([
            "HD, canon, 8k, high quality, photo",
            # "blurry, greyscale, waterpainting, black and white",
            "water color, painting, blurry, greyscale, waterpainting, black and white, low quality"
        ]).cuda()
    
        self.human_text = clip.tokenize([
            "human, man, woman, boy, girl, kid, baby",
            # "blurry, greyscale, waterpainting, black and white",
            "doll, barbie, toy, 3D render, blender, digital art"
        ]).cuda()
           
    def inference(self, img):
        image = self.preprocess(Image.fromarray(img)).unsqueeze(0).cuda()
    
        with torch.no_grad():
            self.model.encode_image(image)
            
            self.model.encode_text(self.quality_text)
            logits_per_image, logits_per_text = self.model(image, self.quality_text)
            quality_probs = logits_per_image.softmax(dim=-1).cpu().numpy()
    
            self.model.encode_text(self.human_text)
            logits_per_image, logits_per_text = self.model(image, self.human_text)
            human_probs = logits_per_image.softmax(dim=-1).cpu().numpy()

        return {"Quality": quality_probs, "Human": human_probs}


if __name__ == "__main__":
    model = clip_model()
    print(model.inference(cv2.imread("./data/clean_images/Afghanistan portrait/33899154713_ebbdc036e1_b0.jpg")))