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
from Model import Model

import cv2
import time
import mmcv
import torch
from mmcv import Config, DictAction
from mmcv.cnn import fuse_conv_bn
from mmcv.parallel import MMDataParallel, MMDistributedDataParallel
from mmcv.runner import get_dist_info, init_dist, load_checkpoint

from mmpose.models import build_posenet

try:
    from mmcv.runner import wrap_fp16_model
except ImportError:
    warnings.warn('auto_fp16 from mmpose will be deprecated from v0.15.0'
                  'Please install mmcv>=1.1.4')
    from mmpose.core import wrap_fp16_model
    

import Constants

MODEL_PATH = './src/ViTPose/vitpose+_large.pth'
CONFIG_PATH = './src/ViTPose/configs/body/2d_kpt_sview_rgb_img/topdown_heatmap/coco/vitPose+_large_coco+aic+mpii+ap10k+apt36k+wholebody_256x192_udp.py'

class pose_model(Model):
    
    def __init__(self):
        cfg = Config.fromfile(CONFIG_PATH)
        self.model = build_posenet(cfg.model)
        fp16_cfg = cfg.get('fp16', None)
        if fp16_cfg is not None:
            wrap_fp16_model(self.model)
        load_checkpoint(self.model, MODEL_PATH, map_location='cpu')
        self.model = fuse_conv_bn(self.model)
        self.model = MMDataParallel(self.model, device_ids=[0])
        
    @torch.no_grad()
    def inference(self, img):
        output = self.model(return_loss=False, **img)
        print(output)
        return output
    
    
if __name__ == "__main__":
    images_dir = "./"# os.path.join(Constants.ACCEPTED_BODY_IMAGES_DIR, 'adventure portrait')
    
    accepted_imgs = ["png", "jpg", "jpeg"]
    
    model = pose_model()
    
    for img_name in ["1196108903_7f3cc2c4ca_o0.jpg"]:
        if img_name.split(".")[-1] not in accepted_imgs:
            continue

        print(img_name)
        img_pth = os.path.join(images_dir, img_name)
        img = cv2.imread(img_pth)
        print("Img shape:",img.shape)

        start = time.time()
        output = model.inference(img)
        # output_img = output_img.detach().cpu().numpy()[0]
        print("Took:", time.time() - start)
        # print("output:", output.shape)
        
        exit()
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
        