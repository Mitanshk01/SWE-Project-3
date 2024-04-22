import requests
from flask import send_from_directory

class FileTransfer:
    def __init__(self, api_url: str):
        self.system_api_url = api_url

    def download_file_from_API(self, file_name, store_file):
        response = requests.get(f'{self.system_api_url}/{file_name}')

        if response.status_code == 200:
            with open(store_file, 'wb') as file:
                file.write(response.content)
            print("File downloaded successfully")
        else:
            print("File not found on server")

    


