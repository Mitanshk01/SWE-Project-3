from flask import Flask, request, jsonify
import requests
from flask_cors import CORS

app = Flask(__name__)
CORS(app) 

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
        print("Got error!", e)
        return jsonify({'error': str(e)}), 500
    
@app.route('/upload_dataset_chunk', methods=['POST'])
def upload_dataset_chunk():
    print("\n\tReceived a dataset upload request")
    try:
        print(request.files)

        chunk = request.files['file']
        offset = int(request.form['offset'])
        current_chunk_index = int(request.form['currentChunkIndex'])
        total_chunks = int(request.form['totalChunks'])
        total_size = int(request.form['totalSize'])
        file_name = request.form['filename']
        file_type = request.form['filetype']

        print(f"Received chunk {current_chunk_index+1}/{total_chunks} of file {file_name} of type {file_type}")
        print(f"Current offset {offset} of total size {total_size}")

        return

        # Define a directory to temporarily store chunk files
        temp_dir = 'temp'
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)

        # Save the chunk to a temporary file
        temp_filename = os.path.join(temp_dir, f'chunk_{current_chunk_index}')
        with open(temp_filename, 'ab') as temp_file:
            temp_file.write(chunk.read())

        # If all chunks have been received, reconstruct the file
        if current_chunk_index == total_chunks - 1:
            with open('dataset_file.dat', 'wb') as dataset_file:
                for i in range(total_chunks):
                    chunk_filename = os.path.join(temp_dir, f'chunk_{i}')
                    with open(chunk_filename, 'rb') as chunk_file:
                        dataset_file.write(chunk_file.read())
                    # Remove the temporary chunk file
                    os.remove(chunk_filename)
            print('Dataset file reconstructed successfully')

        return jsonify({'message': 'Dataset chunk uploaded successfully'})
    except Exception as e:
        print("Got error!", e)
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=8003)
