# RepoManagement Microservice

## API Endpoints

### create_repository
- **Method:** PUT
- **Description:** Creates a new repository in Google Drive and inserts corresponding records into the UserRepo table.
- **Parameters:**
  - `user_id`: User ID
  - `repo_name`: Repository name
- **Response:**
  - `200 OK`: Repository created successfully
  - `500 Internal Server Error`: Error occurred while creating repository

### upload_code_to_repo
- **Method:** POST
- **Description:** Uploads a code file to the specified repository's code directory in Google Drive and inserts a record into the CodeContents table.
- **Parameters:**
  - `file`: Code file to upload
  - `userid`: User ID
  - `repoName`: Repository name
  - `filename`: Name of the file
- **Response:**
  - `200 OK`: File uploaded successfully
  - `404 Not Found`: Repository not found
  - `500 Internal Server Error`: Error occurred while uploading file

### upload_dataset_to_repo
- **Method:** POST
- **Description:** Uploads a dataset chunk to the specified repository's data directory in Google Drive and inserts a record into the DataContents table.
- **Parameters:**
  - `file`: Dataset chunk file
  - `offset`: Offset value
  - `currentChunkIndex`: Current chunk index
  - `totalChunks`: Total number of chunks
  - `totalSize`: Total size of dataset
  - `filename`: Name of the file
  - `filetype`: Type of file
  - `userid`: User ID
  - `repoName`: Repository name
- **Response:**
  - `200 OK`: Chunk received successfully
  - `404 Not Found`: Repository not found
  - `500 Internal Server Error`: Error occurred while uploading chunk

### upload_run_to_repo
- **Method:** POST
- **Description:** Uploads run files (results and log) to the specified repository's runs directory in Google Drive and inserts a record into the Runs table.
- **Parameters:**
  - `results_file`: Results file
  - `log_file`: Log file
  - `userid`: User ID
  - `repoName`: Repository name
  - `run_id`: Run ID
- **Response:**
  - `200 OK`: Run files uploaded successfully
  - `404 Not Found`: Repository not found
  - `500 Internal Server Error`: Error occurred while uploading run files

### download_file
- **Method:** GET
- **Description:** Downloads a file from Google Drive by its ID.
- **Parameters:**
  - `file_id`: ID of the file to download
- **Response:**
  - `200 OK`: File downloaded successfully
  - `400 Bad Request`: File ID missing in request parameters
  - `500 Internal Server Error`: Error occurred while downloading file

### download_folder
- **Method:** GET
- **Description:** Downloads a folder from Google Drive by its ID.
- **Parameters:**
  - `folder_id`: ID of the folder to download
- **Response:**
  - `200 OK`: Folder downloaded successfully
  - `400 Bad Request`: Folder ID missing in request parameters
  - `500 Internal Server Error`: Error occurred while downloading folder

### return_small_file
- **Method:** GET
- **Description:** Returns a small file as a response. Used for files below a certain size threshold.
- **Parameters:**
  - `file_id`: ID of the file to return
- **Response:**
  - `200 OK`: File returned successfully
  - `400 Bad Request`: File ID missing in request parameters
  - `500 Internal Server Error`: Error occurred while returning file

### repo_directory_ids
- **Method:** GET
- **Description:** Retrieves directory IDs associated with a repository.
- **Parameters:**
  - `user_id`: User ID
  - `repo_name`: Repository name
- **Response:**
  - `200 OK`: Directory IDs retrieved successfully
  - `404 Not Found`: Repository not found
  - `500 Internal Server Error`: Error occurred while retrieving directory IDs

### user_repos
- **Method:** GET
- **Description:** Retrieves a list of repository names associated with a user.
- **Parameters:**
  - `user_id`: User ID
- **Response:**
  - `200 OK`: Repository names retrieved successfully
  - `500 Internal Server Error`: Error occurred while retrieving repository names

### get_code_file_metadata_from_repo
- **Method:** GET
- **Description:** Retrieves metadata (name, id, file_size) of all files in the code directory of a repository.
- **Parameters:**
  - `user_id`: User ID
  - `repo_name`: Repository name
- **Response:**
  - `200 OK`: Metadata retrieved successfully
  - `404 Not Found`: Repository not found
  - `500 Internal Server Error`: Error occurred while retrieving metadata

### get_data_file_metadata_from_repo
- **Method:** GET
- **Description:** Retrieves metadata (name, id, file_size) of all files in the data directory of a repository.
- **Parameters:**
  - `user_id`: User ID
  - `repo_name`: Repository name
- **Response:**
  - `200 OK`: Metadata retrieved successfully
  - `404 Not Found`: Repository not found
  - `500 Internal Server Error`: Error occurred while retrieving metadata

### get_runs_from_repo
- **Method:** GET
- **Description:** Retrieves all run IDs in the runs directory of a repository.
- **Parameters:**
  - `user_id`: User ID
  - `repo_name`: Repository name
- **Response:**
  - `200 OK`: Runs retrieved successfully
  - `404 Not Found`: Repository not found
  - `500 Internal Server Error`: Error occurred while retrieving runs

### get_file_metadata_from_run
- **Method:** GET
- **Description:** Retrieves metadata (name, id, file_size) of all files in a specific run directory of a repository.
- **Parameters:**
  - `user_id`: User ID
  - `repo_name`: Repository name
  - `run_id`: Run ID
- **Response:**
  - `200 OK`: Metadata retrieved successfully
  - `404 Not Found`: Repository not found
  - `500 Internal Server Error`: Error occurred while retrieving metadata

### delete_repository
- **Method:** DELETE
- **Description:** Deletes a repository and its contents from Google Drive and associated records from the database.
- **Parameters:**
  - `user_id`: User ID
  - `repo_name`: Repository name
- **Response:**
  - `200 OK`: Repository deleted successfully
  - `404 Not Found`: Repository not found
  - `500 Internal Server Error`: Error occurred while deleting repository

### delete_code_from_repo
- **Method:** DELETE
- **Description:** Deletes a code file from the code directory of a repository and removes its entry from the CodeContents table.
- **Parameters:**
  - `user_id`: User ID
  - `repo_name`: Repository name
  - `file_name`: Name of the file to delete
- **Response:**
  - `200 OK`: File deleted successfully
  - `404 Not Found`: Repository or file not found
  - `500 Internal Server Error`: Error occurred while deleting file

### delete_data_from_repo
- **Method:** DELETE
- **Description:** Deletes a data file from the data directory of a repository and removes its entry from the DataContents table.
- **Parameters:**
  - `user_id`: User ID
  - `repo_name`: Repository name
  - `file_name`: Name of the file to delete
- **Response:**
  - `200 OK`: File deleted successfully
  - `404 Not Found`: Repository or file not found
  - `500 Internal Server Error`: Error occurred while deleting file

### delete_run_from_repo
- **Method:** DELETE
- **Description:** Deletes a run directory from the runs directory of a repository and removes its entry from the Runs table.
- **Parameters:**
  - `user_id`: User ID
  - `repo_name`: Repository name
  - `run_id`: Run ID
- **Response:**
  - `200 OK`: Run deleted successfully
  - `404 Not Found`: Repository or run not found
  - `500 Internal Server Error`: Error occurred while deleting run
