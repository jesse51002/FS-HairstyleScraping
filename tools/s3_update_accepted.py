import shutil
import sys
sys.path.insert(0,'./src')

import os
import json

from aws_s3_downloader import download_aws_folder, get_download_folders
from aws_s3_uploader import upload_aws_folder

import Constants

JSON_OUTPUT = "data/pose_insights_json.json"
bases_to_run = [Constants.ACCEPT_BODY_BACK_REM_IMAGES_DIR, Constants.ACCEPTED_BODY_IMAGES_DIR]


def updated_accepted():
    
    with open(JSON_OUTPUT, "r") as f:
        output_dict = json.load(f)
        
    for root_dir in bases_to_run:
        rel_base = root_dir.split("/")[-1] + "/"

        folders_to_anaylze = []
        
        # Adds folders on local
        folders_to_anaylze += os.listdir(root_dir)
        
        # Adds folders in AWS S3
        s3_folders = get_download_folders(rel_base)
        for i in range(len(s3_folders)):
            s3_folders[i] = s3_folders[i].split("/")[-1][:-4]
        folders_to_anaylze += s3_folders
        
        folders_to_anaylze = set(folders_to_anaylze)
        
        for folder in folders_to_anaylze:
            folder_path = os.path.join(root_dir, folder)
            
            key = rel_base + folder + ".zip"
            zip_process_thread = download_aws_folder(folder_path, key)
            zip_process_thread.join()
            
            for img_name in os.listdir(folder_path):
                img_pth = os.path.join(folder_path, img_name)
                
                save_pth = "/".join(img_pth.replace("\\", "/").split("/")[-2:])
                
                if save_pth in output_dict["rejected"]:
                    os.remove(img_pth)
                    print("Removed {}".format(img_pth))
                    
            upload_aws_folder(folder_path, key[:-4])
            
            shutil.rmtree(folder_path)
            
if __name__ == "__main__":
    updated_accepted()