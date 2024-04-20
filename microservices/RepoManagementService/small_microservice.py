from flask import Flask, request, jsonify, send_file
from tempfile import NamedTemporaryFile
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import os, shutil, io

CHUNKS_DIR = "chunk_files"
DOWNLOAD_FILE_DIR  = "download_files"
SMALL_FILE_THRESH = 30 * 1024 * 1024  # 30MB in bytes

app = Flask(__name__)

def create_or_clear_directory(directory):
    if os.path.exists(directory):
        # If the directory already exists, delete its contents
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f"Failed to delete {file_path}. Reason: {e}")
    else:
        # If the directory does not exist, create it
        os.makedirs(directory)

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

google_drive_client = GoogleDriveClient()

@app.route('/upload_file_to_drive', methods=['POST'])
def handle_upload():
    file = request.files['file']
    print("\n\tReceived a file upload request")

    # seeing mame
    filename = request.form.get('filename')
    print("File name", filename)

    # Accessing size
    file.seek(0, 2) 
    file_size = file.tell() 
    print("File size:", file_size, "bytes")

    file.seek(0)

    try:
        # Save the file temporarily
        with NamedTemporaryFile(delete=False) as temp_file:
            file.save(temp_file.name)
            temp_file_path = temp_file.name
            
            # Upload the file to Google Drive
            google_drive_client.upload_file(file_path=temp_file_path, file_name=filename)
            print("File uploaded!\n")
            return jsonify({'message': 'File uploaded successfully to Google Drive'}), 200
    except Exception as e:
        print("File NOT uploaded!\n")
        return jsonify({'error': str(e)}), 500
    
@app.route('/create_repository', methods=['PUT'])
def create_repository():
    try:
        user_id = request.form["user_id"]
        repo_name = request.form["repo_name"]

        print(f"Received request from user {user_id} is creating a repo {repo_name}")

        user_directory_id = google_drive_client.create_folder(folder_name=user_id)

        # checking if the repository exists
        if google_drive_client.get_folder_id(repo_name, user_directory_id):
            return jsonify({'error': "Repository with same name already exists"}), 500        

        repo_directory_id = google_drive_client.create_folder(folder_name=repo_name, parent_id=user_directory_id)

        print(f"Created repository with id {repo_directory_id}")

        # creating data, code and runs directory
        run_directory_id = google_drive_client.create_folder(folder_name="runs", parent_id=repo_directory_id)
        data_directory_id = google_drive_client.create_folder(folder_name="data", parent_id=repo_directory_id)
        code_directory_id = google_drive_client.create_folder(folder_name="codes", parent_id=repo_directory_id)

        print(f"Created runs, code and data directories with ids {run_directory_id}, {data_directory_id}, {code_directory_id}")

        return jsonify({'message': 'Repository made successfully'}), 200

    except Exception as e:
        print("Got error!", e)
        return jsonify({'error': str(e)}), 500        
    
@app.route('/upload_dataset_chunk', methods=['POST'])
def upload_dataset_chunk():
    print("\n\tReceived a dataset upload request")
    try:
        chunk = request.files['file']
        offset = int(request.form['offset'])
        current_chunk_index = int(request.form['currentChunkIndex'])
        total_chunks = int(request.form['totalChunks'])
        total_size = int(request.form['totalSize'])
        file_name = request.form['filename']
        file_type = request.form['filetype']
        user_id = request.form['userid']
        repo_name = request.form['repoName']

        print(f"Received chunk {current_chunk_index+1}/{total_chunks} of file {file_name} of type {file_type}")
        print(f"Current offset {offset} of total size {total_size}")
        
        # Save the chunk to a temporary file
        chunk_file_path = os.path.join(CHUNKS_DIR, f"{user_id}_{repo_name}_{file_name}_{current_chunk_index}")
        with open(chunk_file_path, "wb") as chunk_file:
            chunk_file.write(chunk.read())

        print("Saved chunk to", chunk_file_path)

        # Check if all chunks have been received
        if current_chunk_index == total_chunks - 1:
            # Concatenate the chunk files
            consolidated_file_path = os.path.join(CHUNKS_DIR, f"{user_id}_{repo_name}_{file_name}_consolidated")
            with open(consolidated_file_path, "wb") as consolidated_file:
                for i in range(total_chunks):
                    with open(os.path.join(CHUNKS_DIR, f"{user_id}_{repo_name}_{file_name}_{i}"), "rb") as chunk_file:
                        consolidated_file.write(chunk_file.read())
                    
                    # Remove the chunk file after concatenating
                    os.remove(os.path.join(CHUNKS_DIR, f"{user_id}_{repo_name}_{file_name}_{i}"))
            
            # Upload the consolidated file to Google Drive
            google_drive_client.upload_file(file_path=consolidated_file_path, file_name=file_name)
            print("Dataset uploaded!\n")

            os.remove(consolidated_file_path)
        
        return jsonify({'message': 'Chunk received successfully'}), 200

    except Exception as e:
        print("Got error!", e)
        return jsonify({'error': str(e)}), 500 

@app.route('/download_file', methods=['GET'])
def download_file():
    """
        The way this is stored is
        DOWNLOAD_FILE_DIR/file_id/file_name.extension

        So, this handles if you download files with different names as well
    """
    try:
        file_id = request.args.get('file_id')
        
        if not file_id:
            return jsonify({'error': 'File ID is missing in the request parameters'}), 400

        download_dir_path = os.path.join(DOWNLOAD_FILE_DIR, file_id)
        create_or_clear_directory(download_dir_path)

        file_save_path = google_drive_client.download_file_by_id(file_id, download_dir_path)

        return jsonify({'downloaded_file_path': file_save_path}), 200
    except Exception as e:
        print("Got error!", e)
        return jsonify({'error': str(e)}), 500
    
@app.route('/download_folder', methods=['GET'])
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
    

@app.route('/return_small_file', methods=['GET'])
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

if __name__ == '__main__':
    create_or_clear_directory(CHUNKS_DIR)
    create_or_clear_directory(DOWNLOAD_FILE_DIR)

    app.run(debug=True, port=8004)
