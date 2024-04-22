// BarChart.js
import React from 'react';
import Plot from 'react-plotly.js';

const BarChart = ({ data }) => {
  // Create labels for each value (1, 2, 3, ...)
  const labels = data.map((_, index) => index + 1);
  // Use data directly as frequencies
  const frequencies = data;

  // Define data for the Bar Chart
  const chartData = [{
    x: labels,
    y: frequencies,
    type: 'bar'
  }];

  // Define layout for the Bar Chart
  const layout = {
    title: 'Bar Chart',
    xaxis: { title: 'Labels' },
    yaxis: { title: 'Frequencies' }
  };

  return (
    <Plot
      data={chartData}
      layout={layout}
    />
  );
};

export default BarChart;
