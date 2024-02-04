import os

import boto3
from boto3.s3.transfer import TransferConfig
import shutil

import sys
sys.path.insert(0,'./src')
import Constants

# s3 boto documentation
# https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html


# Test it on a service (yours may be different)
s3resource = boto3.client('s3')

BUCKET_NAME = "fs-upper-body-gan-dataset"

def create_aws_folder(folder_rel_path):
    key = folder_rel_path.replace("\\", "/")
    if key[-1] != "/":
        key += "/"
       
    # If folder alraedy exists then put it otherwise dont
    try: 
        s3resource.get_object(Bucket=BUCKET_NAME, Key=key)
        print(folder_rel_path, "already exists")
    except:
        s3resource.put_object(Bucket=BUCKET_NAME, Key=key)
        print(folder_rel_path, "was created")

def upload_aws_folder(abs_folder_path, rel_path):
    config = TransferConfig(multipart_threshold=1024*25, max_concurrency=10,
                        multipart_chunksize=1024*25, use_threads=True)
    
    abs_folder_path = abs_folder_path.replace("\\", "/")
    rel_path = rel_path.replace("\\", "/")
    
    zip_output_location = abs_folder_path + ".zip"
    
    print(f"making zip for {rel_path}")
    shutil.make_archive(abs_folder_path, 'zip', abs_folder_path)
    print(f"finished zipping for {rel_path}")
    
    print(f"uploading {rel_path}.zip")
    s3resource.upload_file(zip_output_location, BUCKET_NAME, rel_path + ".zip",
    ExtraArgs={ 'ACL': 'public-read', 'ContentType': 'video/mp4'},
    Config = config,
    )
    print(f"Finished uploading {rel_path}.zip")
    
    
    print(f"Deleting {rel_path} from local")
    os.remove(zip_output_location)
    """
    for i, img_file in enumerate(os.listdir(abs_folder_path)):
        #__s3file = os.path.normpath(dest_path + '/' + file)
        local_file = os.path.join(abs_folder_path, img_file)

        rel_file = os.path.join(rel_folder_path, img_file).replace("\\", "/")
            
        s3resource.upload_file(local_file, BUCKET_NAME, rel_file)
        print(f"Uploaded {rel_folder_path}: image {i}")
    """



def get_upload_folders(split_dir, finished_file=None, completed_scrape_file=None):
    finished_upload = []
    
    if finished_file is not None:
        # Creates file if it doesnt exist
        if not os.path.isfile(finished_file):
            file = open(finished_file, 'w')
            file.close()
            
            
        # Instanties the finihsed folders from file
        with open(finished_file,'r') as file:
            for x in file.readlines():
                line = x.strip()
                finished_upload.append(line)
    
    completed_scape = None
    if completed_scrape_file is not None and os.path.isfile(completed_scrape_file):
        completed_scape = []
        # Instanties the finihsed folders from file
        with open(completed_scrape_file,'r') as file:
            for x in file.readlines():
                line = x.strip()
                completed_scape.append(line)
    
    upload_folders = []
    
    for query_folder in os.listdir(split_dir):
        # only adds folders
        if not os.path.isdir(os.path.join(split_dir, query_folder)):
            continue
        
        # Skips folders that have alraedy been uploaded
        if query_folder in finished_upload:
            print(f"Already uploaded {query_folder}")
            continue
        
        
        if completed_scape is not None and query_folder not in completed_scape:
            print(f"Hasnt completed scrape, {query_folder}")
            continue
        
        upload_folders.append(query_folder)
        

    return upload_folders
            
                
def upload_to_aws(split_dir, finished_file=None, completed_scrape_file=None):
    
    upload_folders = get_upload_folders(split_dir, finished_file, completed_scrape_file)
    
    rel_base = split_dir.split("/")[-1]
    create_aws_folder(rel_base)
    
    for query_folder in upload_folders:
        rel_folder_path = os.path.join(rel_base, query_folder)
        abs_folder_path = os.path.join(split_dir, query_folder)
        
        if not os.path.isdir(abs_folder_path):
            continue
        
        upload_aws_folder(abs_folder_path, rel_folder_path)
                
            
        


if __name__ == "__main__":
    upload_to_aws(Constants.RAW_BODY_IMAGES_DIR, finished_file=Constants.FINIHSED_BODY_RAW_UPLOAD, completed_scrape_file=Constants.FINIHSED_BODY_RAW_TXT)