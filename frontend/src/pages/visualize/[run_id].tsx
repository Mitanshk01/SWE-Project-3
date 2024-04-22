import { useState, useEffect } from 'react';
import dynamic from "next/dynamic";
const Plot = dynamic(() => import("react-plotly.js"), { ssr: false, })
import Papa from 'papaparse';
import { getResultsandLogsfromRun } from '@/components/Requests';
import { useRouter } from 'next/router';

const VisualizePage = () => {
  const router = useRouter();
  const { run_id } = router.query;
  const [data, setData] = useState([]);
  const [xAxis, setXAxis] = useState('');
  const [yAxis, setYAxis] = useState('');
  const [error, setError] = useState('');
  const [columnNames, setColumnNames] = useState([]);
  const [csvData, setCsvData] = useState('');

  useEffect(() => {
    // Fetch data when run_id changes
    if (run_id) {
      fetchdata(run_id);
    }
  }, [run_id]);

  const fetchdata = async (run_id) => {
    try {
      const data = await getResultsandLogsfromRun(run_id);
      if (data) {
        setCsvData(data.logs);
        console.log(data.logs); 
      }
    } catch (error) {
      setError('Error fetching data');
    }
  };

  useEffect(() => {
    // Parse CSV data when csvData changes
    if (csvData) {
      parseCsvData(csvData);
    }
  }, [csvData]);

  const parseCsvData = (csvString) => {
    // Trim leading and trailing whitespace including newline characters
    csvString = csvString.trim();
    Papa.parse(csvString, {
      header: true,
      complete: function(results) {
        if (results.errors.length > 0) {
          setError('Error parsing file. Please check the format.');
          return;
        }
        setData(results.data);
        // Set column names
        if (results.meta && results.meta.fields) {
          setColumnNames(results.meta.fields);
        } else if (results.data.length > 0) {
          setColumnNames(Object.keys(results.data[0]));
        } else {
          setColumnNames([]);
        }
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

  return (
    <div className="container mx-auto mt-8">
      <h1 className="text-center text-2xl font-bold my-4">Visualize Data</h1>
      <div className="flex mt-4">
        <select value={xAxis} onChange={handleXAxisChange} className="mr-4 p-2 border border-gray-300 rounded-md">
          <option value="">Select X Axis</option>
          {columnNames.map((columnName, index) => (
            <option key={index} value={columnName}>{columnName}</option>
          ))}
        </select>
        <select value={yAxis} onChange={handleYAxisChange} className="p-2 border border-gray-300 rounded-md">
          <option value="">Select Y Axis</option>
          {columnNames.map((columnName, index) => (
            <option key={index} value={columnName}>{columnName}</option>
          ))}
        </select>
      </div>
      {error && <p className="text-red-500">{error}</p>}
      {data.length > 0 && xAxis && yAxis && (
        <div className="mt-8">
          <Plot
            data={[
              {
                x: data.map(row => row[xAxis]),
                y: data.map(row => row[yAxis]),
                type: 'scatter',
                mode: 'lines+markers',
                marker: {color: 'red'},
              }
            ]}
          />
        </div>
      )}
    </div>
  );
};

export default VisualizePage;
