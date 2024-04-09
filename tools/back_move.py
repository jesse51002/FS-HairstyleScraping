import os
import sys
sys.path.insert(0,'./src')
import Constants


if not os.path.isdir(Constants.ACCEPT_BODY_BACK_REM_IMAGES_DIR):
    os.makedirs(Constants.ACCEPT_BODY_BACK_REM_IMAGES_DIR)


clean_back_rem_folders = os.listdir(Constants.CLEAN_BODY_BACK_REM_IMAGES_DIR)
for i, folder in enumerate(clean_back_rem_folders):
    folder_pth = os.path.join(Constants.CLEAN_BODY_BACK_REM_IMAGES_DIR, folder)
    
    accecpt_back_rm_dir = os.path.join(Constants.ACCEPT_BODY_BACK_REM_IMAGES_DIR, folder)
    
    for img in os.listdir(folder_pth):
        accept_back_rem_pth = os.path.join(Constants.ACCEPT_BODY_BACK_REM_IMAGES_DIR, folder, img)
        clean_back_rem_pth = os.path.join(Constants.CLEAN_BODY_BACK_REM_IMAGES_DIR, folder, img)
        
        if not os.path.isfile(clean_back_rem_pth):
            continue
        
        clean_pth = os.path.join(Constants.CLEAN_BODY_IMAGES_DIR, folder, img)
        accept_pth = os.path.join(Constants.ACCEPTED_BODY_IMAGES_DIR, folder, img)
        
        if os.path.isfile(accept_pth):
            if not os.path.isdir(accecpt_back_rm_dir):
                os.makedirs(accecpt_back_rm_dir)
            
            os.rename(clean_back_rem_pth, accept_back_rem_pth)
            print(f"Moved to {accept_back_rem_pth}")
        elif not os.path.isfile(clean_pth):
            os.remove(clean_back_rem_pth)
            print(f"Removed {clean_back_rem_pth}")
    
    print(f"Finished {i + 1} / {len(clean_back_rem_folders)} folders")
    
    
    