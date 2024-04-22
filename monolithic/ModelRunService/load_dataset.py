import requests
import zipfile
import io
import os
import glob
from vmc import download_file
from vmc import DOWNLOAD_FILE_DIR

def LoadDataset(user_id, repo_name, run_id, file_id):

    try:
        download_file(file_id)
    except Exception as e:
        print("Error downloading file", e)
        return 

    # Unzip all .zip files in the directory
    for file in glob.glob(f"download_files/{file_id}/*.zip"):
        print(file)
        with zipfile.ZipFile(file, 'r') as zip_ref:
            os.makedirs(f"repos/{repo_name}/data", exist_ok=True)
            zip_ref.extractall(f"repos/{repo_name}/data")
            print(f"Unzipped {file} to repos/{repo_name}/data")

    # Remove the .zip files
    for file in glob.glob(f"download_files/{file_id}/*.zip"):
        os.remove(file)
