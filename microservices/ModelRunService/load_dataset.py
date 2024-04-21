import requests
import zipfile
import io
import os
import glob
from vmc import download_file
from vmc import DOWNLOAD_FILE_DIR

def LoadDataset(user_id, repo_name, run_id, file_id):
    
    download_file(file_id)

    # Unzip the file
    with zipfile.ZipFile(f"{DOWNLOAD_FILE_DIR}/{file_id}/*.zip", 'r') as zip_ref:
        zip_ref.extractall(f"data/{file_id}")

    # Unzip all .zip files in the directory
    for file in glob.glob(f"download_files/{file_id}/*.zip"):
        print(file)
        with zipfile.ZipFile(file, 'r') as zip_ref:
            zip_ref.extractall(f"data/{file_id}")

    # Remove the .zip files
    for file in glob.glob(f"download_files/{file_id}/*.zip"):
        os.remove(file)
