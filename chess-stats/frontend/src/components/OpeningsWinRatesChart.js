import React from "react";
import { Bar } from "react-chartjs-2";

const OpeningsWinRatesChart = ({ stats }) => {
  const topOpenings = stats.most_common_openings.slice(0, 20);
  const topWinRates = stats.opening_winrates.slice(0, 20);

  return (
    <div className="mt-6">
      <h3 className="text-lg font-semibold mb-2">Most Common Openings and Win Rates</h3>
      <div className="w-full max-w-2xl mx-auto">
        <Bar
          data={{
            labels: topOpenings.map((o) => o.name),
            datasets: [
              {
                label: "Number of Games",
                data: topOpenings.map((o) => o.count),
                backgroundColor: "#3498db",
                yAxisID: 'y',
              },
              {
                label: "Win Rate (%)",
                data: topWinRates.map((o) => o.winrate),
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
