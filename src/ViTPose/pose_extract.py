import sys
sys.path.insert(0,'./src')
sys.path.insert(0,'./src/ViTPose')

# This error  subprocess.CalledProcessError: Command '['where', 'cl']' returned non-zero exit status 1.
# This has the fix https://github.com/HRNet/HRNet-Semantic-Segmentation/issues/39
# Then restart your vscode

import argparse
import os
import os.path as osp
import warnings

import mmcv
import torch
from mmcv import Config, DictAction
from mmcv.cnn import fuse_conv_bn
from mmcv.parallel import MMDataParallel, MMDistributedDataParallel
from mmcv.runner import get_dist_info, init_dist, load_checkpoint

from mmpose.models import build_posenet
from mmpose.apis import MMPoseInferencer

try:
    from mmcv.runner import wrap_fp16_model
except ImportError:
    warnings.warn('auto_fp16 from mmpose will be deprecated from v0.15.0'
                  'Please install mmcv>=1.1.4')
    from mmpose.core import wrap_fp16_model
    

import Constants


MODEL_PATH = './src/HumanParsing/checkpoints/exp-schp-201908261155-lip.pth'

class body_model(Model):
    
    def __init__(self):
        model = build_posenet(cfg.model)
        fp16_cfg = cfg.get('fp16', None)
        if fp16_cfg is not None:
            wrap_fp16_model(model)
        load_checkpoint(model, MODEL_PATH, map_location='cpu')

        model = MMDataParallel(model, device_ids=[0])
        
    @torch.no_grad()
    def inference(self, img):
        
        
        return output, output_perc
    
    
if __name__ == "__main__":
    face_dir = os.path.join(Constants.RAW_BODY_IMAGES_DIR, 'test')
    mask_dir = os.path.join(Constants.RAW_BODY_IMAGES_DIR, 'masks')
    
    accepted_imgs = ["png", "jpg", "jpeg"]
    
    model = body_model()
    
    torch.no_grad()
    for img_name in os.listdir(face_dir):
        if img_name.split(".")[-1] not in accepted_imgs:
            continue

        print(img_name)
        img_pth = os.path.join(face_dir, img_name)
        img = cv2.imread(img_pth)
        print("Img shape:",img.shape)

        start = time.time()
        output_img, output_perc = model.inference(img)
        output_img = output_img.detach().cpu().numpy()[0]
        print("Took:", time.time() - start)
        print("output:", output_img.shape)
        
        # setting values to rows and column variables 
        rows = 1
        columns = 2
        
        # create figure 
        fig = plt.figure(figsize=(10, 7)) 
        # Adds a subplot at the 1st position 
        fig.add_subplot(1, 2, 1) 
        
        # showing image 
        plt.imshow(img[:,:,::-1]) 
        plt.axis('off') 
        plt.title("Image") 
        
        # Adds a subplot at the 2nd position 
        fig.add_subplot(rows, columns, 2) 
        
        # showing image 
        plt.imshow(vis_seg(output_img))
        plt.axis('off') 
        plt.title("mask") 
        
        plt.savefig(os.path.join(mask_dir, img_name))
        # plt.show()
        