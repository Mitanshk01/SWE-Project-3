from flask import Flask, request, jsonify
from tempfile import NamedTemporaryFile
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import os

CHUNKS_DIR = "chunk_files"

app = Flask(__name__)

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

    def upload_file(self, file_path, file_name=None, parent_id=None):
        # Upload file to Google Drive
        if file_name is None:
            file_name = file_path.split('/')[-1]
        file = self.drive.CreateFile({'title': file_name})

        if parent_id:
            file['parents'] = [{'id': parent_id}]
        file.SetContentFile(file_path)
        file.Upload()
        print(f"File '{file_name}' uploaded successfully to Google Drive")

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


        #### TODO - use userid and repo name in the 

        print(f"Received chunk {current_chunk_index+1}/{total_chunks} of file {file_name} of type {file_type}")
        print(f"Current offset {offset} of total size {total_size}")
        
        # Save the chunk to a temporary file
        chunk_file_path = os.path.join(CHUNKS_DIR, f"{file_name}_{current_chunk_index}")
        with open(chunk_file_path, "wb") as chunk_file:
            chunk_file.write(chunk.read())

        # Check if all chunks have been received
        if current_chunk_index == total_chunks - 1:
            # Concatenate the chunk files
            consolidated_file_path = os.path.join(CHUNKS_DIR, f"{file_name}_consolidated")
            with open(consolidated_file_path, "wb") as consolidated_file:
                for i in range(total_chunks):
                    with open(os.path.join(CHUNKS_DIR, f"{file_name}_{i}"), "rb") as chunk_file:
                        consolidated_file.write(chunk_file.read())
                    
                    # Remove the chunk file after concatenating
                    os.remove(os.path.join(CHUNKS_DIR, f"{file_name}_{i}"))
            
            # Upload the consolidated file to Google Drive
            google_drive_client.upload_file(file_path=consolidated_file_path, file_name=file_name)
            print("Dataset uploaded!\n")

            os.remove(consolidated_file_path)
        
        return jsonify({'message': 'Chunk received successfully'}), 200

    except Exception as e:
        print("Got error!", e)
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    os.makedirs(CHUNKS_DIR, exist_ok=True)
    app.run(debug=True, port=8004)
