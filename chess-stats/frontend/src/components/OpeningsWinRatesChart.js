import React from "react";
import { Bar } from "react-chartjs-2";

const OpeningsWinRatesChart = ({ stats }) => {
  return (
    <div className="mt-6">
      <h3 className="text-lg font-semibold mb-2">Most Common Openings and Win Rates</h3>
      <div className="w-full max-w-2xl mx-auto">
        <Bar
          data={{
            labels: stats.most_common_openings.map((o) => o.name),
            datasets: [
              {
                label: "Number of Games",
                data: stats.most_common_openings.map((o) => o.count),
                backgroundColor: "#3498db",
                yAxisID: 'y',
              },
              {
                label: "Win Rate (%)",
                data: stats.opening_winrates.map((o) => o.winrate),
                backgroundColor: "#8e44ad",
                yAxisID: 'y1',
              },
            ],
          }}
          options={{
            scales: {
              y: {
                beginAtZero: true,
                position: 'left',
                title: {
                  display: true,
                  text: 'Number of Games',
                },
              },
              y1: {
                beginAtZero: true,
                position: 'right',
                title: {
                  display: true,
                  text: 'Win Rate (%)',
                },
                grid: {
                  drawOnChartArea: false,
                },
              },
            },
          }}
        />
      </div>
    </div>
  );
};

export default OpeningsWinRatesChart;
