import React from "react";
import { Pie } from "react-chartjs-2";

const WinPercentageChart = ({ stats }) => {
  return (
    <div className="mt-6">
      <h3 className="text-lg font-semibold mb-2">Win Percentage</h3>
      <div className="w-full max-w-lg mx-auto">
        <Pie
          data={{
            labels: ["Wins", "Losses"],
            datasets: [
              {
                data: [stats.wins, stats.losses],
                backgroundColor: ["#4CAF50", "#F44336"],
              },
            ],
          }}
          options={{
            plugins: {
              tooltip: {
                callbacks: {
                  label: function (context) {
                    const label = context.label || '';
                    const value = context.raw;
                    const total = context.dataset.data.reduce((acc, val) => acc + val, 0);
                    const percentage = ((value / total) * 100).toFixed(2);
                    return `${label}: ${value} (${percentage}%)`;
                  }
                }
              }
            }
          }}
        />
      </div>
    </div>
  );
};

export default WinPercentageChart;