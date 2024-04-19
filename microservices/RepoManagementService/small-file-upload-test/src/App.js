import React, { useState } from 'react';
import axios from 'axios';

const FileUpload = () => {
  // for uploading file
  const [file, setFile] = useState(null);
  // for uploading dataset
  const [datasetFile, setDatasetFile] = useState(null);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleDatasetFileChange = (e) => {
    setDatasetFile(e.target.files[0]);
  };

  const handleFileUpload = async () => {
    try {
      const formData = new FormData();
      formData.append('file', file);
      await axios.post('http://localhost:8003/upload_file_to_drive', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      console.log('File uploaded successfully');
    } catch (error) {
      console.error('Error uploading file:', error);
    }
  };

  const handleDatasetUpload = async () => {
    const chunkSize = 1024 * 1024; // 1MB chunk size
    const totalSize = datasetFile.size;
    const totalChunks = Math.ceil(totalSize / chunkSize);

    console.log("Uploading file", datasetFile, "with", totalChunks, "chunks");

    let currentChunkIndex = 0;

    const readNextChunk = async () => {
      console.log("Reading chunk index", currentChunkIndex);

      const fileReader = new FileReader();
      const offset = currentChunkIndex * chunkSize;
      const blob = datasetFile.slice(offset, offset + chunkSize);
      
      fileReader.onload = async () => {
        const chunk = fileReader.result;
        const blobChunk = new Blob([chunk]); // Convert ArrayBuffer to Blob
        const fileChunk = new File([blobChunk], datasetFile.name); // Convert Blob to File

        const formData = new FormData();
        formData.append('file', fileChunk);
        formData.append('offset', offset);
        formData.append('currentChunkIndex', currentChunkIndex);
        formData.append('totalChunks', totalChunks);
        formData.append('totalSize', totalSize);
        formData.append('filename', datasetFile.name);
        formData.append("filetype", datasetFile.type);
        
        try {
          await axios.post('http://localhost:8003/upload_dataset_chunk', formData);
          currentChunkIndex++;

          if (currentChunkIndex < totalChunks) {
            readNextChunk();
          } else {
            console.log('Dataset uploaded successfully');
          }
        } catch (error) {
          console.error('Error uploading dataset chunk:', error);
        }
      };

      fileReader.readAsArrayBuffer(blob);
    };

    readNextChunk();
  };

  return (
    <div>
      <div>
        <input type="file" onChange={handleFileChange} />
        <button onClick={handleFileUpload}>Upload File</button>
      </div>

      <div>
        <input type="file" onChange={handleDatasetFileChange} />
        <button onClick={handleDatasetUpload}>Upload Dataset</button>
      </div>
    </div>
  );
};

export default FileUpload;
