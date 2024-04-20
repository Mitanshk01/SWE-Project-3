import { useState } from 'react';
import Link from 'next/link';

export default function Upload() {
  const [message, setMessage] = useState(null);

  const handleUpload = async (event) => {
    event.preventDefault();

    const formData = new FormData();
    formData.append('file', event.target.file.files[0]);

    // Simulating upload process
    try {
      // Here you can add code to handle the file upload process,
      // such as sending the file to a server or processing it in some way.
      // Since we're not including a backend in this example, we'll just display a success message.
      setMessage('File uploaded successfully');
    } catch (error) {
      console.error('Error uploading file: ', error);
      setMessage('Error uploading file');
    }
  };

  return (
    <div>
      <h1>Upload File</h1>
      <form onSubmit={handleUpload} encType="multipart/form-data">
        <input type="file" name="file" />
        <button type="submit">Upload</button>
      </form>
      {message && <p>{message}</p>}
    </div>
  );
}
