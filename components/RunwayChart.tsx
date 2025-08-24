import React from "react";
import { Bar } from "react-chartjs-2";

const RunwayChart = () => {
  const data = {
    labels: ["Runway 1", "Runway 2", "Runway 3", "Runway 4", "Runway 5"],
    datasets: [
      {
        label: "Utilization (%)",
        data: [75, 60, 90, 50, 80],
        backgroundColor: [
          "#4caf50",
          "#2196f3",
          "#f44336",
          "#ff9800",
          "#9c27b0",
        ],
      },
      {
        label: "Average Delay (minutes)",
        data: [5, 10, 3, 15, 8],
        backgroundColor: [
          "#8bc34a",
          "#03a9f4",
          "#e91e63",
          "#ffc107",
          "#673ab7",
        ],
      },
    ],
  };

  const options = {
    responsive: true,
    plugins: {
      legend: {
        position: "top",
      },
      tooltip: {
        callbacks: {
          label: (context) => `${context.dataset.label}: ${context.raw}`,
        },
      },
    },
    scales: {
      y: {
        beginAtZero: true,
      },
    },
  };

  return <Bar data={data} options={options} />;
};

export default RunwayChart;
