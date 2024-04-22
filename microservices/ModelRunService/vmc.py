from flask import  request, jsonify, send_file
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import os, io

CHUNKS_DIR = "./chunk_files"
DOWNLOAD_FILE_DIR  = "./download_files"
SMALL_FILE_THRESH = 30 * 1024 * 1024  # 30MB in bytes

def create_or_clear_directory(directory):
    if os.path.exists(directory):
        print(f"{directory} directory exists already: yaya:::))) ")
        # TODO: Clear the directory LATER
        # # If the directory already exists, delete its contents
        # for filename in os.listdir(directory):
        #     file_path = os.path.join(directory, filename)
        #     try:
        #         if os.path.isfile(file_path) or os.path.islink(file_path):
        #             os.unlink(file_path)
        #         elif os.path.isdir(file_path):
        #             shutil.rmtree(file_path)
        #     except Exception as e:
        #         print(f"Failed to delete {file_path}. Reason: {e}")
    else:
        # If the directory does not exist, create it
        print("Directory doesn't exist")
        # create this directory wherever this code is being executed from i.e. "./"
        os.makedirs(directory, exist_ok=True)
        print("Directory created")
        # check whether the directory has been created or not
        print("Directory created or not: ", os.path.exists(directory))


class GoogleDriveClient:
    def __init__(self, credentials_file="credentials.json"):
        # Authenticate with Google Drive
        self.gauth = GoogleAuth()
        self.gauth.LoadCredentialsFile(credentials_file)
        if self.gauth.credentials is None:
            self.gauth.LocalWebserverAuth()
        elif self.gauth.access_token_expired:
            self.gauth.Refresh()
        else:
            self.gauth.Authorize()
        self.gauth.SaveCredentialsFile(credentials_file)

        # Initialize GoogleDrive instance
        self.drive = GoogleDrive(self.gauth)

        # getting base folder ID
        self.base_ops_folder = self.get_folder_id("SE-Project")

    def upload_file(self, file_path, file_name=None, parent_id=None):
        if parent_id is None:
            parent_id = self.base_ops_folder

        # Upload file to Google Drive
        if file_name is None:
            file_name = file_path.split('/')[-1]
        file = self.drive.CreateFile({'title': file_name})

        file['parents'] = [{'id': parent_id}]
        file.SetContentFile(file_path)
        file.Upload()
        print(f"File '{file_name}' uploaded successfully to Google Drive with id {file['id']}")

        # Return the ID of the uploaded file
        return file['id']
    
    def download_file_by_id(self, file_id, save_path):
        # 1vZ6pK37KWdG6Olh_CmDmY4ibz4PltD-g
        # Download file given its ID
        file = self.drive.CreateFile({'id': file_id})

        filename = file['title']

        save_path = os.path.join(save_path, filename)

        file.GetContentFile(save_path)
        print(f"File with ID '{file_id}' downloaded successfully to '{save_path}'")

        return save_path

    def download_folder_by_id(self, folder_id, save_path):
        # 1XwkNN9Kmy1i29jEWBw_IVbT7ub1Wa3Q1
        # downloads folder given its ID
        folder_metadata = self.drive.CreateFile({'id': folder_id})
        folder_metadata.FetchMetadata()

        folder_name = folder_metadata['title']
        folder_save_path = os.path.join(save_path, folder_name)

        # create the folder
        os.makedirs(folder_save_path, exist_ok=True)

        query = f"'{folder_id}' in parents and trashed=false"
        file_list = self.drive.ListFile({'q': query}).GetList()

        for file in file_list:
            # Check if the item is a folder
            if file['mimeType'] == 'application/vnd.google-apps.folder':
                # download the folder
                self.download_folder_by_id(folder_id=file['id'], save_path=folder_save_path)
            else:
                # Download the file
                self.download_file_by_id(file_id=file['id'], save_path=folder_save_path)

        return folder_save_path

    def create_folder(self, folder_name, parent_id=None):
        if parent_id is None:
            parent_id = self.base_ops_folder

        # Check if the folder already exists
        existing_folder_id = self.get_folder_id(folder_name, parent_id)
        if existing_folder_id:
            return existing_folder_id
        
        # If the folder doesn't exist, create it
        folder_metadata = {
            'title': folder_name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
            
        folder_metadata['parents'] = [{'id': parent_id}]
        
        folder = self.drive.CreateFile(folder_metadata)
        folder.Upload()
        print(f"Folder '{folder_name}' created successfully in Google Drive")

        return folder['id']

    def get_folder_id(self, folder_name, base_folder_id=None):
        if base_folder_id is None:
            # List all files and folders in the root directory
            query = "'root' in parents and trashed=false"
        else:
            # List all files and folders in the specified base folder
            query = f"'{base_folder_id}' in parents and trashed=false"
        
        file_list = self.drive.ListFile({'q': query}).GetList()
        
        # Search for the folder with the specified name
        for file in file_list:
            if file['title'] == folder_name and file['mimeType'] == 'application/vnd.google-apps.folder':
                return file['id']
        
        # If the folder is not found, return None
        return None
    
    def delete_file_by_id(self, file_id):
        # Delete file given its ID
        try:
            file = self.drive.CreateFile({'id': file_id})
            file.Delete()
            print(f"File with ID '{file_id}' deleted successfully from Google Drive")
            return True
        except Exception as e:
            print(f"Error deleting file with ID '{file_id}': {e}")
            return False

    def delete_folder_by_id(self, folder_id):
        # Delete folder given its ID
        try:
            folder = self.drive.CreateFile({'id': folder_id})
            folder.Delete()
            print(f"Folder with ID '{folder_id}' deleted successfully from Google Drive")
            return True
        except Exception as e:
            print(f"Error deleting folder with ID '{folder_id}': {e}")
            return False

google_drive_client = GoogleDriveClient()

def download_file(file_id):
    """
        The way this is stored is
        DOWNLOAD_FILE_DIR/file_id/file_name.extension

        So, this handles if you download files with different names as well
    """
    try:
        print("Request on download_file route: ", file_id)
        
        if not file_id:
            return jsonify({'error': 'File ID is missing in the request parameters'}), 400
        
        print("Donwload dir: ", DOWNLOAD_FILE_DIR)

        download_dir_path = os.path.join(DOWNLOAD_FILE_DIR, file_id)
        print("The download directory path: ", download_dir_path)
        create_or_clear_directory(download_dir_path)
        file_save_path = google_drive_client.download_file_by_id(file_id, download_dir_path)

    except Exception as e:
        print("Got error!", e)
    

def download_folder():
    """
        The way this is stored is
        DOWNLOAD_FILE_DIR/folder_id/...

        So, this handles if you download folders with different names as well
    """
    try:
        folder_id = request.args.get('folder_id')
        
        if not folder_id:
            return jsonify({'error': 'File ID is missing in the request parameters'}), 400

        download_dir_path = os.path.join(DOWNLOAD_FILE_DIR, folder_id)
        create_or_clear_directory(download_dir_path)

        folder_save_path = google_drive_client.download_folder_by_id(folder_id, download_dir_path)

        return jsonify({'downloaded_folder_path': folder_save_path}), 200
    except Exception as e:
        print("Got error!", e)
        return jsonify({'error': str(e)}), 500
    
def return_small_file():
    try:
        file_id = request.args.get('file_id')
        
        if not file_id:
            return jsonify({'error': 'File ID is missing in the request parameters'}), 400

        download_dir_path = os.path.join(DOWNLOAD_FILE_DIR, file_id)
        create_or_clear_directory(download_dir_path)

        file_save_path = google_drive_client.download_file_by_id(file_id, download_dir_path)

        # Check file size
        file_size = os.path.getsize(file_save_path)
        if file_size > SMALL_FILE_THRESH:
            return jsonify({'error': 'File size exceeds the threshold for small files'}), 400

        # Read the downloaded file as bytes
        with open(file_save_path, 'rb') as file:
            file_bytes = file.read()

        # Return the file as a response
        return send_file(
            io.BytesIO(file_bytes),
            mimetype='application/octet-stream',
            as_attachment=True,
            download_name=os.path.basename(file_save_path)
        )
    except Exception as e:
        print("Got error!", e)
        return jsonify({'error': str(e)}), 500