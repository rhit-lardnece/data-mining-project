import React from "react";
import { Pie, Bar } from "react-chartjs-2";

const StatsCharts = ({ stats }) => {
  return (
    <div className="bg-white p-6 rounded-lg shadow-lg">
      <h2 className="text-2xl font-semibold mb-4">Stats for {stats.username}</h2>
      <p><strong>Total Games:</strong> {stats.total_games}</p>
      <p><strong>Win Percentage:</strong> {((stats.wins / (stats.wins + stats.losses)) * 100).toFixed(2)}%</p>
      <p><strong>Avg Opponent Rating:</strong> {stats.average_opponent_rating}</p>
      <p><strong>Most Frequent Opponent:</strong> {stats.most_common_opponent}</p>

      {/* PIE CHART: Win Percentage */}
      <div className="mt-6">
        <h3 className="text-lg font-semibold mb-2">Win Percentage</h3>
        <div className="w-full max-w-md mx-auto">
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
                      return `${label}: ${value}`;
                    }
                  }
                },
              }
            }}
          />
        </div>
      </div>

      {/* Combined Chart: Most Common Openings and Win Rates */}
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

      {/* BAR CHART: Game Lengths */}
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

      {/* PIE CHART: Higher Elo Win Percentage */}
      <div className="mt-6">
        <h3 className="text-lg font-semibold mb-2">Win Percentage Against Higher Elo Players</h3>
        <div className="w-full max-w-md mx-auto">
          <Pie
            data={{
              labels: ["Wins", "Losses"],
              datasets: [
                {
                  data: [stats.higher_elo_wins, stats.higher_elo_losses],
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

      {/* PIE CHART: Lower Elo Win Percentage */}
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
    </div>
  );
};

export default StatsCharts;
