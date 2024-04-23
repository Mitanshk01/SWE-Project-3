from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from model_run import train_model
from visualize_data import fetch_table_headings, fetch_column_details
from model_run import global_model_name, global_repo_name, global_run_id, global_user_id

from tempfile import NamedTemporaryFile
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import os, shutil, io
import sqlite3
from werkzeug.utils import secure_filename
import json

app = Flask(__name__)
CORS(app, supports_credentials=True, resources={r"/*": {"origins": "*"}})
# CORS(app, resources={r"/*": {"origins": "*", "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"]}})

CHUNKS_DIR = "./chunk_files"
DOWNLOAD_FILE_DIR  = "./download_files"
SMALL_FILE_THRESH = 30 * 1024 * 1024  # 30MB in bytes

# SQLite database file path
DATABASE_FILE = "database.db"

app = Flask(__name__)
CORS(app, supports_credentials=True, resources={r"/*": {"origins": "*"}})
# CORS(app, resources={r"/*": {"origins": "*", "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"]}})

# Function to create SQLite tables if they don't exist
def create_tables():
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS UserRepo (
        user_id TEXT NOT NULL,
        repo_name TEXT NOT NULL,
        repo_directory_id TEXT,
        code_directory_id TEXT,
        data_directory_id TEXT,
        runs_directory_id TEXT,
        PRIMARY KEY (user_id, repo_name)
    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS DataContents (
        data_directory_id TEXT NOT NULL,
        file_name TEXT NOT NULL,
        file_id TEXT,
        PRIMARY KEY (data_directory_id, file_name)
    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS CodeContents (
        code_directory_id TEXT NOT NULL,
        file_name TEXT NOT NULL,
        file_id TEXT,
        PRIMARY KEY (code_directory_id, file_name)
    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS Runs (
        runs_directory_id TEXT NOT NULL,
        run_id TEXT NOT NULL,
        specific_run_directory_id TEXT,
        results_file_id TEXT,
        log_file_id TEXT,
        PRIMARY KEY (runs_directory_id, run_id)
    )''')

    conn.commit()
    conn.close()

# Function to clear SQLite tables
def clear_tables():
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()

    # Delete all records from tables
    cursor.execute("DELETE FROM UserRepo")
    cursor.execute("DELETE FROM DataContents")
    cursor.execute("DELETE FROM CodeContents")
    cursor.execute("DELETE FROM Runs")

    conn.commit()
    conn.close()

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
    def __init__(self, credentials_file="repo_credentials.json"):
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
    
@app.route('/create_repository', methods=['PUT'])
def create_repository():
    try:
        print("In create repository")
        print("request = ",request)
        print("request.form = ",request.form)
        print("request.data = ",request.data)
        print("request.json = ",request.json)
        user_id = request.json["user_id"]
        repo_name = request.json["repo_name"]

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

        print(f"Created runs, code and data directories with ids {run_directory_id}, {code_directory_id}, {data_directory_id}")

        # Inserting into UserRepo table
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO UserRepo (user_id, repo_name, repo_directory_id, code_directory_id, data_directory_id, runs_directory_id) VALUES (?, ?, ?, ?, ?, ?)",
                        (user_id, repo_name, repo_directory_id, code_directory_id, data_directory_id, run_directory_id))
        conn.commit()
        conn.close()

        return jsonify({'message': 'Repository made successfully'}), 200

    except Exception as e:
        print("Got error!", e)
        return jsonify({'error': str(e)}), 500
    
@app.route('/upload_code_to_repo', methods=['POST'])
def handle_upload():
    try:
        print(request.files)
        file = request.files['file']
        user_id = request.form['userid']
        repo_name = request.form['repoName']
        print("User: ", user_id)
        print("Repo: ", repo_name)
        print(f"Received a code upload request from {user_id} for repo {repo_name}")
        print("File: aayi hai: ", file)


        # Seeing name
        filename = request.form.get('filename')
        print("File name", filename)

        # Accessing size
        file.seek(0, 2) 
        file_size = file.tell() 
        print("File size:", file_size, "bytes")

        file.seek(0)

        # Get the code directory ID associated with the repository
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        # execute a query to see all contents of UserRepo
        cursor.execute("SELECT * FROM UserRepo")
        print(cursor.fetchall())
        print("************************")
        # I want to extract the code_directory_id from UserRepo for the user_id and repo_name
        cursor.execute("SELECT code_directory_id FROM UserRepo WHERE user_id = ? AND repo_name = ?", (user_id, repo_name))
        result = cursor.fetchone()
        print(result)
        if not result:
            print("Failed on line 336 :(  ")
            conn.close()
            return jsonify({'error': 'Repository not found'}), 404
        
        code_directory_id = result[0]
        print("Code directory id: ", code_directory_id)
        
        try:
            # Save the file temporarily
            with NamedTemporaryFile(delete=False) as temp_file:
                file.save(temp_file.name)
                temp_file_path = temp_file.name
                
                # Upload the file to Google Drive with code directory as parent
                file_id = google_drive_client.upload_file(file_path=temp_file_path, file_name=filename, parent_id=code_directory_id)
                print("File uploaded!\n")
                
                # Insert the record into the CodeContents table
                cursor.execute("INSERT INTO CodeContents (code_directory_id, file_name, file_id) VALUES (?, ?, ?)", (code_directory_id, filename, file_id))
                conn.commit()

                return jsonify({'message': 'File uploaded successfully to Google Drive'}), 200
        except Exception as e:
            print("File NOT uploaded!\n")
            return jsonify({'error': str(e)}), 500
        finally:
            conn.close()
    except Exception as e:
        print("Got error!", e)
        return jsonify({'error': str(e)}), 500


@app.route('/upload_dataset_to_repo', methods=['POST'])
def upload_dataset_chunk():
    print("\n\tReceived a dataset upload request")
    print("request = ",request)
    print("request.form = ",request.form)
    print("request.files = ",request.files)
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

        print(f"Received a data upload request from {user_id} for repo {repo_name}")

        print(f"Received chunk {current_chunk_index+1}/{total_chunks} of file {file_name} of type {file_type}")
        print(f"Current offset {offset} of total size {total_size}")

        # Get the data directory ID associated with the repository
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT data_directory_id FROM UserRepo WHERE user_id = ? AND repo_name = ?", (user_id, repo_name))
        result = cursor.fetchone()
        
        if not result:
            conn.close()
            return jsonify({'error': 'Repository not found'}), 404
        
        data_directory_id = result[0]
        
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
            
            # Upload the consolidated file to Google Drive with data directory as parent
            file_id = google_drive_client.upload_file(file_path=consolidated_file_path, file_name=file_name, parent_id=data_directory_id)
            print("Dataset uploaded!\n")

            # Insert the record into the DataContents table
            cursor.execute("INSERT INTO DataContents (data_directory_id, file_name, file_id) VALUES (?, ?, ?)", (data_directory_id, file_name, file_id))
            conn.commit()

            os.remove(consolidated_file_path)
        
        conn.close()
        return jsonify({'message': 'Chunk received successfully'}), 200

    except Exception as e:
        print("Got error!", e)
        return jsonify({'error': str(e)}), 500
    
@app.route('/upload_run_to_repo', methods=['POST'])
def upload_run_to_repo():
    print("Got a request to upload run files")
    try:
        print("Request: ", request)
        user_id = request.form['userid']
        repo_name = request.form['repo_name']
        run_id = request.form['run_id']
        
        results_file = request.files['results_file']
        log_file = request.files['log_file']

        print(f"Received a run upload request from {user_id} for repo {repo_name} with run_id {run_id}")

        # Get the runs directory ID associated with the repository
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT runs_directory_id FROM UserRepo WHERE user_id = ? AND repo_name = ?", (user_id, repo_name))
        result = cursor.fetchone()
        
        if not result:
            conn.close()
            return jsonify({'error': 'Repository not found'}), 404
        
        runs_directory_id = result[0]

        print("Run directory id: ", runs_directory_id)
        
        try:
            temp_dir = '/tmp'
            results_file_path = os.path.join(temp_dir, secure_filename(results_file.filename))
            log_file_path = os.path.join(temp_dir, secure_filename(log_file.filename))
            results_file.save(results_file_path)
            log_file.save(log_file_path)
            # Create a folder with the same name as run_id in the runs directory
            run_folder_id = google_drive_client.create_folder(folder_name=run_id, parent_id=runs_directory_id)
            print(f"Created folder for run {run_id} in the runs directory")

            # Upload results file to the run_id folder
            results_file_id = google_drive_client.upload_file(file_path=results_file_path, file_name=results_file.filename, parent_id=run_folder_id)
            print(f"Uploaded results file to run folder: {results_file.filename}")

            # Upload log file to the run_id folder
            log_file_id = google_drive_client.upload_file(file_path=log_file_path, file_name=log_file.filename, parent_id=run_folder_id)
            print(f"Uploaded log file to run folder: {log_file.filename}")

            # Insert the record into the Runs table
            cursor.execute("INSERT INTO Runs (runs_directory_id, run_id, specific_run_directory_id, results_file_id, log_file_id) VALUES (?, ?, ?, ?, ?)",
                           (runs_directory_id, run_id, run_folder_id, results_file_id, log_file_id))
            conn.commit()

            return jsonify({'message': 'Run files uploaded successfully to Google Drive'}), 200
        except Exception as e:
            print("Run files NOT uploaded!\n")
            return jsonify({'error': str(e)}), 500
        finally:
            if os.path.exists(results_file_path):
                os.remove(results_file_path)
            if os.path.exists(log_file_path):
                os.remove(log_file_path)
            conn.close()
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
        print("Request on download_file route: ", file_id)
        
        if not file_id:
            return jsonify({'error': 'File ID is missing in the request parameters'}), 400

        download_dir_path = os.path.join(DOWNLOAD_FILE_DIR, file_id)
        print("The download directory path: ", download_dir_path)
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
    
@app.route('/repo_directory_ids', methods=['GET'])
def get_repo_directory_ids():
    try:
        user_id = request.args.get('user_id')
        repo_name = request.args.get('repo_name')

        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()

        cursor.execute("SELECT repo_directory_id, runs_directory_id, data_directory_id, code_directory_id FROM UserRepo WHERE user_id = ? AND repo_name = ?", (user_id, repo_name))
        result = cursor.fetchone()

        conn.close()

        if result:
            repo_directory_id, runs_directory_id, data_directory_id, code_directory_id = result
            return jsonify({
                'repo_directory_id': repo_directory_id,
                'runs_directory_id': runs_directory_id,
                'data_directory_id': data_directory_id,
                'code_directory_id': code_directory_id
            }), 200
        else:
            return jsonify({'error': "Repository not found"}), 404

    except Exception as e:
        print("Got error!", e)
        return jsonify({'error': str(e)}), 500

@app.route('/user_repos', methods=['GET'])
def get_user_repos():
    try:
        user_id = request.args.get('user_id')

        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()

        cursor.execute("SELECT repo_name FROM UserRepo WHERE user_id = ?", (user_id,))
        result = cursor.fetchall()

        conn.close()

        if result:
            repo_names = [row[0] for row in result]
            return jsonify({'repos': repo_names}), 200
        else:
            return jsonify({'repos': []}), 200

    except Exception as e:
        print("Got error!", e)
        return jsonify({'error': str(e)}), 500


@app.route('/get_code_file_metadata_from_repo', methods=['GET'])
def get_code_file_metadata_from_repo():
    try:
        user_id = request.args.get('user_id')
        repo_name = request.args.get('repo_name')

        print(f"Received request to get code file metadata from repo '{repo_name}' for user '{user_id}'")

        # Get the code directory ID associated with the repository
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT code_directory_id FROM UserRepo WHERE user_id = ? AND repo_name = ?", (user_id, repo_name))
        result = cursor.fetchone()

        if not result:
            conn.close()
            return jsonify({'error': 'Repository not found'}), 404
        
        code_directory_id = result[0]

        # Fetch metadata of all files in the code directory
        query = f"'{code_directory_id}' in parents and trashed=false"
        file_list = google_drive_client.drive.ListFile({'q': query}).GetList()

        # Extract relevant metadata for each file
        code_files_metadata = []
        for file in file_list:
            code_files_metadata.append({
                'name': file['title'],
                'id': file['id'],
                'file_size': file['fileSize']
            })

        conn.close()

        print(f"Code file metadata retrieved successfully from repo '{repo_name}' for user '{user_id}'")

        return jsonify(code_files_metadata), 200

    except Exception as e:
        print("Got error!", e)
        return jsonify({'error': str(e)}), 500

@app.route('/get_data_file_metadata_from_repo', methods=['GET'])
def get_data_file_metadata_from_repo():
    try:
        user_id = request.args.get('user_id')
        repo_name = request.args.get('repo_name')

        print(f"Received request to get data file metadata from repo '{repo_name}' for user '{user_id}'")

        # Get the data directory ID associated with the repository
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT data_directory_id FROM UserRepo WHERE user_id = ? AND repo_name = ?", (user_id, repo_name))
        result = cursor.fetchone()

        if not result:
            conn.close()
            return jsonify({'error': 'Repository not found'}), 404
        
        data_directory_id = result[0]

        # Fetch metadata of all files in the data directory
        query = f"'{data_directory_id}' in parents and trashed=false"
        file_list = google_drive_client.drive.ListFile({'q': query}).GetList()

        # Extract relevant metadata for each file
        data_files_metadata = []
        for file in file_list:
            data_files_metadata.append({
                'name': file['title'],
                'id': file['id'],
                'file_size': file['fileSize']
            })

        conn.close()

        print(f"Data file metadata retrieved successfully from repo '{repo_name}' for user '{user_id}'")

        return jsonify(data_files_metadata), 200

    except Exception as e:
        print("Got error!", e)
        return jsonify({'error': str(e)}), 500

@app.route('/get_runs_from_repo', methods=['GET'])
def get_runs_from_repo():
    try:
        user_id = request.args.get('user_id')
        repo_name = request.args.get('repo_name')

        print(f"Received request to get runs from repo '{repo_name}' for user '{user_id}'")

        # Get the runs directory ID associated with the repository
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT runs_directory_id FROM UserRepo WHERE user_id = ? AND repo_name = ?", (user_id, repo_name))
        result = cursor.fetchone()

        if not result:
            conn.close()
            return jsonify({'error': 'Repository not found'}), 404
        
        runs_directory_id = result[0]

        # Fetch metadata of all folders (runs) in the runs directory
        query = f"'{runs_directory_id}' in parents and trashed=false"
        folder_list = google_drive_client.drive.ListFile({'q': query}).GetList()

        # Extract run_ids
        run_ids = [folder['title'] for folder in folder_list]

        conn.close()

        print(f"Runs retrieved successfully from repo '{repo_name}' for user '{user_id}'")

        return jsonify(run_ids), 200

    except Exception as e:
        print("Got error!", e)
        return jsonify({'error': str(e)}), 500

@app.route('/get_file_metadata_from_run', methods=['GET'])
def get_file_metadata_from_run():
    try:
        user_id = request.args.get('user_id')
        repo_name = request.args.get('repo_name')
        run_id = request.args.get('run_id')

        print(f"Received request to get file metadata from run '{run_id}' of repo '{repo_name}' for user '{user_id}'")

        # Get the runs directory ID associated with the repository
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT runs_directory_id FROM UserRepo WHERE user_id = ? AND repo_name = ?", (user_id, repo_name))
        result = cursor.fetchone()

        if not result:
            conn.close()
            return jsonify({'error': 'Repository not found'}), 404
        
        runs_directory_id = result[0]

        # Fetch metadata of all files in the run directory
        query = f"title = '{run_id}' and '{runs_directory_id}' in parents and trashed=false"
        file_list = google_drive_client.drive.ListFile({'q': query}).GetList()

        # Extract relevant metadata for each file
        run_files_metadata = []
        for file in file_list:
            run_files_metadata.append({
                'name': file['title'],
                'id': file['id'],
                'file_size': file['fileSize']
            })

        conn.close()

        print(f"File metadata retrieved successfully from run '{run_id}' of repo '{repo_name}' for user '{user_id}'")

        return jsonify(run_files_metadata), 200

    except Exception as e:
        print("Got error!", e)
        return jsonify({'error': str(e)}), 500

@app.route('/delete_repository', methods=['DELETE'])
def delete_repository():
    try:
        user_id = request.form["user_id"]
        repo_name = request.form["repo_name"]

        print(f"Received request to delete repository '{repo_name}' of user '{user_id}'")

        # Get the repository's directories IDs
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT repo_directory_id, data_directory_id, code_directory_id, runs_directory_id FROM UserRepo WHERE user_id = ? AND repo_name = ?", (user_id, repo_name))
        result = cursor.fetchone()

        if not result:
            conn.close()
            return jsonify({'error': 'Repository not found'}), 404
        
        repo_directory_id, data_directory_id, code_directory_id, runs_directory_id = result

        # Delete the repository directory and its contents from Google Drive
        google_drive_client.delete_folder_by_id(repo_directory_id)

        # Remove all entries associated with the repository from the tables
        cursor.execute("DELETE FROM UserRepo WHERE user_id = ? AND repo_name = ?", (user_id, repo_name))
        cursor.execute("DELETE FROM DataContents WHERE data_directory_id = ?", (data_directory_id,))
        cursor.execute("DELETE FROM CodeContents WHERE code_directory_id = ?", (code_directory_id,))
        cursor.execute("DELETE FROM Runs WHERE runs_directory_id = ?", (runs_directory_id,))

        conn.commit()
        conn.close()

        print(f"Repository '{repo_name}' of user '{user_id}' deleted successfully")

        return jsonify({'message': 'Repository deleted successfully'}), 200

    except Exception as e:
        print("Got error!", e)
        return jsonify({'error': str(e)}), 500

@app.route('/delete_code_from_repo', methods=['DELETE'])
def delete_code_from_repo():
    try:
        user_id = request.form['user_id']
        repo_name = request.form['repo_name']
        file_name = request.form['file_name']

        print(f"Received request to delete file '{file_name}' from code directory of repo '{repo_name}' for user '{user_id}'")

        # Get the code directory ID associated with the repository
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT code_directory_id FROM UserRepo WHERE user_id = ? AND repo_name = ?", (user_id, repo_name))
        result = cursor.fetchone()

        if not result:
            conn.close()
            return jsonify({'error': 'Repository not found'}), 404
        
        code_directory_id = result[0]

        # Delete the file from Google Drive
        query = f"title = '{file_name}' and '{code_directory_id}' in parents and trashed=false"
        file_list = google_drive_client.drive.ListFile({'q': query}).GetList()
        if file_list:
            file_id = file_list[0]['id']
            google_drive_client.delete_file_by_id(file_id)
        else:
            conn.close()
            return jsonify({'error': 'File not found in code directory'}), 404

        # Remove the corresponding entry from the CodeContents table
        cursor.execute("DELETE FROM CodeContents WHERE code_directory_id = ? AND file_name = ?", (code_directory_id, file_name))

        conn.commit()
        conn.close()

        print(f"File '{file_name}' deleted from code directory of repo '{repo_name}' for user '{user_id}'")

        return jsonify({'message': 'File deleted successfully'}), 200

    except Exception as e:
        print("Got error!", e)
        return jsonify({'error': str(e)}), 500

@app.route('/delete_data_from_repo', methods=['DELETE'])
def delete_data_from_repo():
    try:
        user_id = request.form['user_id']
        repo_name = request.form['repo_name']
        file_name = request.form['file_name']

        print(f"Received request to delete file '{file_name}' from data directory of repo '{repo_name}' for user '{user_id}'")

        # Get the data directory ID associated with the repository
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT data_directory_id FROM UserRepo WHERE user_id = ? AND repo_name = ?", (user_id, repo_name))
        result = cursor.fetchone()

        if not result:
            conn.close()
            return jsonify({'error': 'Repository not found'}), 404
        
        data_directory_id = result[0]

        # Delete the file from Google Drive
        query = f"title = '{file_name}' and '{data_directory_id}' in parents and trashed=false"
        file_list = google_drive_client.drive.ListFile({'q': query}).GetList()
        if file_list:
            file_id = file_list[0]['id']
            google_drive_client.delete_file_by_id(file_id)
        else:
            conn.close()
            return jsonify({'error': 'File not found in data directory'}), 404

        # Remove the corresponding entry from the DataContents table
        cursor.execute("DELETE FROM DataContents WHERE data_directory_id = ? AND file_name = ?", (data_directory_id, file_name))

        conn.commit()
        conn.close()

        print(f"File '{file_name}' deleted from data directory of repo '{repo_name}' for user '{user_id}'")

        return jsonify({'message': 'File deleted successfully'}), 200

    except Exception as e:
        print("Got error!", e)
        return jsonify({'error': str(e)}), 500

@app.route('/delete_run_from_repo', methods=['DELETE'])
def delete_run_from_repo():
    try:
        user_id = request.form['user_id']
        repo_name = request.form['repo_name']
        run_id = request.form['run_id']

        print(f"Received request to delete run '{run_id}' from runs directory of repo '{repo_name}' for user '{user_id}'")

        # Get the runs directory ID associated with the repository
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT runs_directory_id FROM UserRepo WHERE user_id = ? AND repo_name = ?", (user_id, repo_name))
        result = cursor.fetchone()

        if not result:
            conn.close()
            return jsonify({'error': 'Repository not found'}), 404
        
        runs_directory_id = result[0]

        # Delete the run directory from Google Drive
        query = f"title = '{run_id}' and '{runs_directory_id}' in parents and trashed=false"
        file_list = google_drive_client.drive.ListFile({'q': query}).GetList()
        if file_list:
            file_id = file_list[0]['id']
            google_drive_client.delete_folder_by_id(file_id)
        else:
            conn.close()
            return jsonify({'error': 'Run folder not found in runs directory'}), 404

        # Remove the corresponding entry from the Runs table
        cursor.execute("DELETE FROM Runs WHERE runs_directory_id = ? AND run_id = ?", (runs_directory_id, run_id))

        conn.commit()
        conn.close()

        print(f"Run '{run_id}' deleted from runs directory of repo '{repo_name}' for user '{user_id}'")

        return jsonify({'message': 'Run deleted successfully'}), 200

    except Exception as e:
        print("Got error!", e)
        return jsonify({'error': str(e)}), 500

####################################################################################
####################################################################################
####################################################################################
####################################################################################
####################################################################################
####################################################################################
####################################################################################
####################################################################################
####################################################################################
####################################################################################
####################################################################################
####################################################################################
####################################################################################
####################################################################################
####################################################################################
####################### ADDING CODE FOR MODEL MANAGEMENT NOW #######################
####################################################################################
####################################################################################
####################################################################################
####################################################################################
####################################################################################
####################################################################################
####################################################################################
####################################################################################
####################################################################################
####################################################################################
####################################################################################
####################################################################################
####################################################################################
####################################################################################
####################################################################################



@app.route('/train_model', methods=['POST'])
def train():
    print("Inside Train")
    print("Received training request sirji: ", request.json)
    request_data = request.json
    print("[In 8004] : ", request_data)
    user_id = request_data['user_id']
    repo_name = request_data['repo_name']  # format repo/model
    run_id = request_data['run_name']
    model_file_id = request_data['model_file_id']
    data_file_id = request_data['data_file_id']
    model_run = train_model(user_id, repo_name, run_id, model_file_id, data_file_id)

    print(f"Trained model for user {user_id}, repo {repo_name}, run {run_id}")

    return jsonify({'status': 'success'})
    # return jsonify(result)


@app.route('/fetch_headings', methods=['GET'])
def fetch_headings():
    print("Inside Fetch")
    user_id = request.args.get('user_id')
    repo_name = request.args.get('repo_name')
    data_file_id = request.args.get('data_file_id')

    column_names = fetch_table_headings(user_id, repo_name, data_file_id)
    
    return jsonify(column_names)

@app.route('/fetch_column', methods=['GET'])
def fetch_col_details():
    print("Fetching Columns!!!")
    user_id = request.args.get('user_id')
    repo_name = request.args.get('repo_name')
    data_file_id = request.args.get('data_file_id')
    col_name = request.args.get('col')

    column = fetch_column_details(user_id, repo_name, data_file_id, col_name)
    
    if column:
        # Extract data for the specified column
        return jsonify(column)
    else:
        return jsonify({"error": "Column not found"}), 404
    

@app.route('/get_results', methods=['POST'])
def get_results():
    print("Inside get_results")
    request_data = request.json
    run_id = request_data['run_id']

    results_path = f'results/{run_id}/results.txt'
    log_path = f'results/{run_id}/logs.csv'

    results = { "results": "", "logs": "" }

    if os.path.exists(results_path):
        with open(results_path, "r") as file:
            results["results"] = file.read()

    if os.path.exists(log_path):
        with open(log_path, "r") as file:
            results["logs"] = file.read()
            
    return jsonify(results)

if __name__ == '__main__':
    create_or_clear_directory(CHUNKS_DIR)
    create_or_clear_directory(DOWNLOAD_FILE_DIR)

    create_tables()
    app.run(host='localhost',port=8004)


