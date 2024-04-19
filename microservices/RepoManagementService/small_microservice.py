from flask import Flask, request, jsonify
from tempfile import NamedTemporaryFile
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

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

if __name__ == '__main__':
    app.run(debug=True, port=8004)
