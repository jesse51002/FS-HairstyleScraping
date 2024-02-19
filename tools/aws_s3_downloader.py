import os
import shutil

import boto3

import sys
sys.path.insert(0,'./src')
import Constants

from threading import Thread, Lock

# s3 boto documentation
# https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html


# Test it on a service (yours may be different)
s3resource = boto3.client('s3')

BUCKET_NAME = "fs-upper-body-gan-dataset"

MAX_FOLDER_COUNT_DOWNLOAD = 1000

def zip_parser(abs_folder_path, zip_file, finished_download_file=None, file_lock=None):
    if not os.path.isdir(abs_folder_path):
        os.makedirs(abs_folder_path)

    shutil.unpack_archive(zip_file, abs_folder_path)
    os.remove(zip_file)

    if finished_download_file is not None:
        if file_lock is not None:
            file_lock.acquire()

        with open(finished_download_file, 'a') as finished_file:
            finished_file.write(f'\n{abs_folder_path.split("/")[-1]}')

        if file_lock is not None:
            file_lock.release()

    print(f"Finsihed parsing {abs_folder_path}")


def download_aws_folder(abs_folder_path, s3_key, finished_download_file=None, file_lock=None):
    zip_file_pth = abs_folder_path+".zip"

    print(f"Starting {s3_key} download")
    s3resource.download_file(Bucket=BUCKET_NAME, Key=s3_key, Filename=zip_file_pth)
    print(f"Downloaded {s3_key}")

    print(f"Starting zip parsing for {s3_key}")
    zip_process_thread = Thread(target=zip_parser, args=(abs_folder_path, zip_file_pth, finished_download_file, file_lock))
    zip_process_thread.start()

    
    return zip_process_thread
    

def get_download_folders(prefix="", completed_download_file=None):
    s3_list = s3resource.list_objects_v2(Bucket=BUCKET_NAME, Prefix=prefix, MaxKeys=1000)['Contents']
    keys_in_s3 = [x['Key'] for x in s3_list]
    keys_in_s3.remove(prefix)
    
    
    # Gets folders that have already been downloaded
    finished_download = []
    if completed_download_file is not None:
        # Creates file if it doesnt exist
        if not os.path.isfile(completed_download_file):
            file = open(completed_download_file, 'w')
            file.close()
             
        # Instanties the finihsed folders from file
        with open(completed_download_file,'r') as file:
            for x in file.readlines():
                line = x.strip()
                if len(line) == 0:
                    continue
                finished_download.append(line)
   
    
    i = 0
    while i < len(keys_in_s3):
        key = keys_in_s3[i]
        for finished in finished_download:
            if finished in key:
                keys_in_s3.pop(i)
                i -= 1
                break
        i += 1
        
    return keys_in_s3[:min(MAX_FOLDER_COUNT_DOWNLOAD, len(keys_in_s3))]
            
                
def download_from_aws(split_dir, completed_download_file=None):
     # Creates file if it doesnt exist
    if not os.path.isfile(completed_download_file):
        file = open(completed_download_file, 'w')
        file.close()

    
    rel_base = split_dir.split("/")[-1] + "/"
    
    download_folders = get_download_folders(rel_base, completed_download_file)

    threads = []

    file_lock = Lock()
    
    for key in download_folders:
        abs_folder_path = os.path.join(split_dir, key[len(rel_base):-4])
        
        zip_process_thread = download_aws_folder(abs_folder_path, key, completed_download_file, file_lock)
        threads.append(zip_process_thread)

    for t in threads:
        t.join()
    

if __name__ == "__main__":
    download_from_aws(Constants.CLEAN_BODY_IMAGES_DIR, completed_download_file=Constants.FINIHSED_BODY_CLEAN_DOWNLOAD)