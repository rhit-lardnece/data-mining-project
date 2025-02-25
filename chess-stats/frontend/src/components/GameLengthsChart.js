import React from "react";
import { Bar } from "react-chartjs-2";

const GameLengthsChart = ({ stats }) => {
  return (
    <div className="mt-6">
      <h3 className="text-lg font-semibold mb-2">Game Lengths (Moves)</h3>
      <div className="w-full max-w-2xl mx-auto">
        <Bar
          data={{
            labels: stats.game_lengths.map((_, index) => `Game ${index + 1}`),
            datasets: [
              {
                label: "Moves",
                data: stats.game_lengths,
                backgroundColor: "#2c3e50",
              },
            ],
          }}
          options={{ scales: { y: { beginAtZero: true } } }}
        />
      </div>
    </div>
  );
};

export default GameLengthsChart;
