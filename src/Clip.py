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

        self.hair_type = clip.tokenize([
            "braids and dreads", "afro hair", "curly hair", "wavy hair", "straight hair"
        ]).cuda()

        self.hair_color = clip.tokenize([
            "black hair", "dyed hair"
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


class DataClassifierClip(Model):
    
    def __init__(self):
        # load model
        self.model, self.preprocess = clip.load("ViT-B/16", device="cpu")
        self.model = self.model.cuda()
        farl_state = torch.load("./src/model_weights/FaRL-Base-Patch16-LAIONFace20M-ep64.pth")
        self.model.load_state_dict(farl_state["state_dict"], strict=False)

        self.hair_types_list = [
            "braids and dreads", "afro hair", "curly hair", "wavy hair", "straight hair", "hat, beanie, headcover"
        ]

        self.ethnicites_list = [
            "Dark skin", "Light Skin"
        ]

        self.sex_list = [
            "Male", "Female"
        ]
        
        self.hair_type = clip.tokenize(self.hair_types_list).cuda()
        self.ethnicity = clip.tokenize(self.ethnicites_list).cuda()
        self.sex = clip.tokenize(self.sex_list).cuda()
        
    def inference(self, img):
        image = self.preprocess(Image.fromarray(img)).unsqueeze(0).cuda()
    
        with torch.no_grad():
            self.model.encode_image(image)
            
            self.model.encode_text(self.hair_type)
            logits_per_image, logits_per_text = self.model(image, self.hair_type)
            hair_type_probs = logits_per_image.softmax(dim=-1).cpu().numpy()[0]

            self.model.encode_text(self.ethnicity)
            logits_per_image, logits_per_text = self.model(image, self.ethnicity)
            ethnicity_probs = logits_per_image.softmax(dim=-1).cpu().numpy()[0]

            self.model.encode_text(self.sex)
            logits_per_image, logits_per_text = self.model(image, self.sex)
            sex_probs = logits_per_image.softmax(dim=-1).cpu().numpy()[0]

        return {
            "HairType": hair_type_probs,
            "Ethnicity": ethnicity_probs,
            "Sex": sex_probs
        }


if __name__ == "__main__":
    model = DataClassifierClip()
    model_results = model.inference(cv2.imread("./data/clean_images/fitness portrait curly/46684915021_e79b9ea865_o0.jpg"))
    for key in model_results:
        print(key, model_results[key].argmax())
        