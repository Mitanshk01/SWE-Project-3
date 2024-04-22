import { useEffect, useState } from 'react';
import axios from 'axios';


const RunLogs = ({ runId }) => {
  

  useEffect(() => {
    fetchLogs();
    const interval = setInterval(fetchLogs, 3000); // Fetch logs every minute

    return () => clearInterval(interval); // Clean up on component unmount
  }, [runId]);

  const fetchLogs = async () => {
    // const response = await axios.get(`/run/${runId}/logs`);
    
    // TODO : Fetch logs from backend
  };

  return (
    <div style={{ width: '300px', height: '300px', overflow: 'auto' }}>
      <pre>{logs}</pre>
    </div>
  );
};

const RunResults = ({ runId }) => {
  const [results, setResults] = useState('');

  useEffect(() => {
    fetchResults();
    const interval = setInterval(fetchResults, 3000); // Fetch results every minute

    return () => clearInterval(interval); // Clean up on component unmount
  }, [runId]);

  const fetchResults = async () => {
    // const response = await axios.get(`/run/${runId}/results`);

  };

  return (
    <div style={{ width: '300px', height: '300px', overflow: 'auto' }}>
      <pre>{results}</pre>
    </div>
  );
};

export { RunLogs, RunResults };