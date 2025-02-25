import React from "react";
import { Pie } from "react-chartjs-2";

const LowerEloWinPercentageChart = ({ stats }) => {
  return (
    <div className="mt-6">
      <h3 className="text-lg font-semibold mb-2">Win Percentage Against Lower Elo Players</h3>
      <div className="w-full max-w-md mx-auto">
        <Pie
          data={{
            labels: ["Wins", "Losses"],
            datasets: [
              {
                data: [stats.lower_elo_wins, stats.lower_elo_losses],
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
                    return `${label}: ${value}`;
                  }
                }
              },
            }
          }}
        />
      </div>
    </div>
  );
};

export default LowerEloWinPercentageChart;
