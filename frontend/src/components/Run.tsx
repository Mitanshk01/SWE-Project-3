import { useEffect, useState } from 'react';
import axios from 'axios';

//TODO :remove this
var dummy_data = `
Accuracy : 88,
Accuracy : 92,
Accuracy : 96,
Accuracy : 98,
Accuracy : 99,
Accuracy : 88,
Accuracy : 92,
Accuracy : 96,
Accuracy : 98,
Accuracy : 99,
Accuracy : 88,
Accuracy : 92,
Accuracy : 96,
Accuracy : 98,
Accuracy : 99,
Accuracy : 88,
Accuracy : 92,
Accuracy : 96,
Accuracy : 98,
Accuracy : 99,
Accuracy : 88,
Accuracy : 92,
Accuracy : 96,
Accuracy : 98,
Accuracy : 99,
`;

const RunLogs = ({ runId }) => {
  const [logs, setLogs] = useState('');

  useEffect(() => {
    fetchLogs();
    const interval = setInterval(fetchLogs, 3000); // Fetch logs every minute

    return () => clearInterval(interval); // Clean up on component unmount
  }, [runId]);

  const fetchLogs = async () => {
    // const response = await axios.get(`/run/${runId}/logs`);
    
    // TODO : Fetch logs from backend

    const dummy_data = `
        loss : 1.1,
        loss : 1.2
        `;
    setLogs(dummy_data);
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

    // TODO : Fetch logs from backend
    dummy_data = dummy_data + `Accuracy : 99,\n`;

    setResults(dummy_data);
  };

  return (
    <div style={{ width: '300px', height: '300px', overflow: 'auto' }}>
      <pre>{results}</pre>
    </div>
  );
};

export { RunLogs, RunResults };