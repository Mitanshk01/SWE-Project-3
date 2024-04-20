import { useRouter } from 'next/router';
import { useEffect, useState } from 'react';
import axios from 'axios';
import { RunLogs } from '@/components/Run';
import { RunResults } from '@/components/Run';

const RunPage = () => {
  const router = useRouter();
  const { run_id } = router.query;

  const [run, setRun] = useState(null);

  useEffect(() => {
    if (run_id) {
      // setRun(true);
      fetchRun();
    }
  }, [run_id]);

  const fetchRun = () => {
    //TODO : get run details using run_id from backend

    const dummy_data = {
      run_id : run_id,
      description : "dummy run", 
      status : "in progress"
    }

    setRun(dummy_data);
  };

  const handleVisualize = () => {
    router.push(`/visualize/${run_id}`);
  }; 

  return (
    <div>
      {run && (
        <>
          <h4> Status : {run.status} </h4>
          <div style={{ display: 'flex', justifyContent: 'center' }}>
            <div >
                <h4>Logs</h4>
                <RunLogs runId={run_id} />
            </div>
            <div>
                <h4>Results</h4>
                <RunResults runId={run_id} />
            </div>
          </div>
          <button onClick={handleVisualize}>Visualize</button>
        </>
      )}
    </div>
  );
};

export default RunPage;