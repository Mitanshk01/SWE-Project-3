import { useState } from 'react';
import { useRouter } from 'next/router';
import Plot from 'react-plotly.js';
import Papa from 'papaparse';

const VisualizePage = () => {
  const router = useRouter();
  const { repo_id, run_id } = router.query;
  const [data, setData] = useState([]);
  const [xAxis, setXAxis] = useState('');
  const [yAxis, setYAxis] = useState('');
  const [error, setError] = useState('');

  const handleFileUpload = (event) => {
    const file = event.target.files[0];
    if (!file) {
      setError('Please select a file.');
      return;
    }

    Papa.parse(file, {
      complete: function(results) {
        if (results.errors.length > 0) {
          setError('Error parsing file. Please check the format.');
          return;
        }
        setData(results.data);
        setError('');
      }
    });
  };

  const handleXAxisChange = (event) => {
    setXAxis(event.target.value);
  };

  const handleYAxisChange = (event) => {
    setYAxis(event.target.value);
  };

  const plotData = [
    {
      x: data.map(row => row[xAxis] || row[0]),
      y: data.map(row => row[yAxis]),
      type: 'scatter',
      mode: 'lines+markers',
      marker: {color: 'red'},
    }
  ];

  return (
    <div className="container mx-auto mt-8">
      <h1 className="text-center text-2xl font-bold my-4">Visualize Data</h1>
      <input type="file" onChange={handleFileUpload} />
      {error && <p className="text-red-500">{error}</p>}
      <div className="flex mt-4">
        <input type="text" placeholder="X Axis" onChange={handleXAxisChange} className="mr-4 p-2 border border-gray-300 rounded-md" />
        <input type="text" placeholder="Y Axis" onChange={handleYAxisChange} className="p-2 border border-gray-300 rounded-md" />
      </div>
      {data.length > 0 && (
        <div className="mt-8">
          <Plot data={plotData} />
        </div>
      )}
    </div>
  );
};

export default VisualizePage;
