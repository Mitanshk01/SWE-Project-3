// LineChart.js
import React from 'react';
import Plot from 'react-plotly.js';

const LineChart = ({ data }) => {
  // Create labels for each value (1, 2, 3, ...)
  const labels = data.map((_, index) => index + 1);
  // Use data directly as values for the line chart
  const values = data;

  // Define data for the Line Chart
  const chartData = [{
    x: labels,
    y: values,
    type: 'line'
  }];

  // Define layout for the Line Chart
  const layout = {
    title: 'Line Chart',
    xaxis: { title: 'Labels' },
    yaxis: { title: 'Values' }
  };

  return (
    <Plot
      data={chartData}
      layout={layout}
    />
  );
};

export default LineChart;
