import { useRouter } from 'next/router';
import { useEffect, useState } from 'react';
import axios from 'axios';
import { RunLogs } from '@/components/Run';
import { RunResults } from '@/components/Run';
import { getFileMetadataFromRun, getResultsandLogsfromRun } from '@/components/Requests';

const RunPage = () => {
  const router = useRouter();
  const { run_id } = router.query;

  const [run, setRun] = useState(null);
  const [logs, setLogs] = useState('');
  const [results, setResults] = useState('');

  useEffect(() => {
    if (run_id) {
      // setRun(true);
      fetchRun();
    }
  }, [run_id]);

  const fetchRun = async () => {
    
    const data = await getResultsandLogsfromRun(run_id);

    console.log(data.logs);

    setLogs(data.logs);
    setResults(data.results);
    setRun(data);
  };

  const handleVisualize = () => {
    router.push(`/visualize/${run_id}`);
  }; 

  return (
    <div>
      {run && (
        <>
          <h4> Status : Completed  </h4>
          <div style={{ display: 'flex', justifyContent: 'center' }}>
            <div >
                <h4>Logs</h4>
                <div style={{ width: '300px', height: '300px', overflow: 'auto' }}>
                  <pre>{logs}</pre>
                </div>
            </div>
            <div>
                <h4>Results</h4>
                <div style={{ width: '300px', height: '300px', overflow: 'auto' }}>
                  <pre>{results}</pre>
                </div>
            </div>
          </div>
          <button onClick={handleVisualize}>Visualize</button>
        </>
      )}
    </div>
  );
};

export default RunPage;