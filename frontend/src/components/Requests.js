import axios from 'axios';

// Function to create a new repository
export const createRepository = async (userId, repoName) => {
  try {
    const response = await axios.put('http://localhost:8004/create_repository', {
      user_id: userId,
      repo_name: repoName
    });
    console.log({userId, repoName});
    return response.data;
  } catch (error) {
    console.error(error);
  }
}

// Function to upload code to a repository
export const uploadCodeToRepo = async (userId, repoName, codeFile) => {
  try {
    const formData = new FormData();
    formData.append('user_id', userId);
    formData.append('repo_name', repoName);
    formData.append('code_file', codeFile);

    const response = await axios.post('http://localhost:8004/upload_code_to_repo', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
    return response.data;
  } catch (error) {
    console.error(error);
  }
}


// Function to upload a dataset chunk to a repository
export const uploadDatasetToRepo = async (file, offset, currentChunkIndex, totalChunks, totalSize, filename, filetype, userid, repoName) => {
  try {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('offset', offset);
    formData.append('currentChunkIndex', currentChunkIndex);
    formData.append('totalChunks', totalChunks);
    formData.append('totalSize', totalSize);
    formData.append('filename', filename);
    formData.append('filetype', filetype);
    formData.append('userid', userid);
    formData.append('repoName', repoName);

    const response = await axios.post('http://localhost:8004/upload_dataset_to_repo', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
    return response.data;
  } catch (error) {
    console.error(error);
  }
}

// Function to upload run files to a repository
export const uploadRunToRepo = async (resultsFile, logFile, userid, repoName, runId) => {
  try {
    const formData = new FormData();
    formData.append('results_file', resultsFile);
    formData.append('log_file', logFile);
    formData.append('userid', userid);
    formData.append('repoName', repoName);
    formData.append('run_id', runId);

    const response = await axios.post('http://localhost:8004/upload_run_to_repo', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
    return response.data;
  } catch (error) {
    console.error(error);
  }
}

// Function to download a file from Google Drive by its ID
export const downloadFile = async (fileId) => {
  try {
    const response = await axios.get(`http://localhost:8004/download_file?file_id=${fileId}`, {
      responseType: 'blob' // Important for files
    });
    return response.data;
  } catch (error) {
    console.error(error);
  }
}

// Function to download a folder from Google Drive by its ID
export const downloadFolder = async (folderId) => {
  try {
    const response = await axios.get(`http://localhost:8004/download_folder?folder_id=${folderId}`, {
      responseType: 'blob' // Important for folders
    });
    return response.data;
  } catch (error) {
    console.error(error);
  }
}

// Function to return a small file as a response
export const returnSmallFile = async (fileId) => {
  try {
    const response = await axios.get(`http://localhost:8004/return_small_file?file_id=${fileId}`);
    return response.data;
  } catch (error) {
    console.error(error);
  }
}



// Function to retrieve directory IDs associated with a repository
export const getRepoDirectoryIds = async (userId, repoName) => {
  try {
    const response = await axios.get(`http://localhost:8004/repo_directory_ids?user_id=${userId}&repo_name=${repoName}`);
    return response.data;
  } catch (error) {
    console.error(error);
  }
}

// Function to retrieve a list of repository names associated with a user
export const getUserRepos = async (userId) => {
  try {
    const response = await axios.get(`http://localhost:8004/user_repos?user_id=${userId}`);
    // console.log(response.data);
    return response.data;
  } catch (error) {
    console.error(error);
  }
}

// Function to retrieve metadata of all files in the code directory of a repository
export const getCodeFileMetadataFromRepo = async (userId, repoName) => {
  try {
    const response = await axios.get(`http://localhost:8004/get_code_file_metadata_from_repo?user_id=${userId}&repo_name=${repoName}`);
    return response.data;
  } catch (error) {
    console.error(error);
  }
}

// Function to retrieve metadata of all files in the data directory of a repository
export const getDataFileMetadataFromRepo = async (userId, repoName) => {
  try {
    const response = await axios.get(`http://localhost:8004/get_data_file_metadata_from_repo?user_id=${userId}&repo_name=${repoName}`);
    return response.data;
  } catch (error) {
    console.error(error);
  }
}

// Function to retrieve all run IDs in the runs directory of a repository
export const getRunsFromRepo = async (userId, repoName) => {
  try {
    const response = await axios.get(`http://localhost:8004/get_runs_from_repo?user_id=${userId}&repo_name=${repoName}`);
    return response.data;
  } catch (error) {
    console.error(error);
  }
}

// Function to retrieve metadata of all files in a specific run directory of a repository
export const getFileMetadataFromRun = async (runId) => {
  try {
    const response = await axios.get(`http://localhost:8004/get_file_metadata_from_run?run_id=${runId}`);
    return response.data;
  } catch (error) {
    console.error(error);
  }
}

// Function to delete a repository
export const deleteRepository = async (userId, repoName) => {
  try {
    const response = await axios.delete(`http://localhost:8004/delete_repository?user_id=${userId}&repo_name=${repoName}`);
    return response.data;
  } catch (error) {
    console.error(error);
  }
}

// Function to delete a code file from a repository
export const deleteCodeFromRepo = async (userId, repoName, fileName) => {
  try {
    const response = await axios.delete(`http://localhost:8004/delete_code_from_repo?user_id=${userId}&repo_name=${repoName}&file_name=${fileName}`);
    return response.data;
  } catch (error) {
    console.error(error);
  }
}

// Function to delete a data file from a repository
export const deleteDataFromRepo = async (userId, repoName, fileName) => {
  try {
    const response = await axios.delete(`http://localhost:8004/delete_data_from_repo?user_id=${userId}&repo_name=${repoName}&file_name=${fileName}`);
    return response.data;
  } catch (error) {
    console.error(error);
  }
}


// Function to delete a run from a repository
export const deleteRunFromRepo = async (userId, repoName, runId) => {
  try {
    const response = await axios.delete(`http://localhost:8004/delete_run_from_repo?user_id=${userId}&repo_name=${repoName}&run_id=${runId}`);
    return response.data;
  } catch (error) {
    console.error(error);
  }
}

export const getResultsandLogsfromRun = async (run_id) => {
  try {
    const response = await axios.post('http://localhost:8004/get_results', { run_id: run_id });
    return response.data;
  } catch (error) {
    console.error(error);
  }
}