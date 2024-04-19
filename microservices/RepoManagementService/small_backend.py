from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

@app.route('/upload_file_to_drive', methods=['POST'])
def upload_file():

    print("\n\tReceived a file upload request")
    file = request.files['file']

    # Accessing filename
    filename = file.filename
    print("Filename:", filename)

    # Accessing size
    file.seek(0, 2) 
    file_size = file.tell() 
    print("File size:", file_size, "bytes")

    file.seek(0)

    # Forward the file to the OneDrive microservice
    try:
        data = {'filename': filename}
        files = {'file': file}  # Assuming 'filename' is the name of the file
        response = requests.post('http://localhost:8004/upload_file_to_drive', data=data, files=files)
        if response.status_code == 200:
            print("File uploaded!\n")
            return jsonify({'message': 'File uploaded successfully to OneDrive'})
        else:
            print("File NOT uploaded!\n")
            return jsonify({'error': 'Failed to upload file to OneDrive'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=8003)
