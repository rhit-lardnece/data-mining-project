import React, { useState } from "react";
import axios from "axios";
import { Pie, Bar } from "react-chartjs-2";
import { Chart, ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement } from "chart.js";

// Register required Chart.js components
Chart.register(ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement);

const ChessStats = () => {
  const [username, setUsername] = useState("");
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchStats = async () => {
    if (!username) {
      setError("Please enter a username");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await axios.get(`http://127.0.0.1:5000/chess_stats?username=${username}`);
      setStats(response.data);
    } catch (err) {
      setError("Error fetching data. Make sure the username exists.");
      setStats(null);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gray-100 p-4">
      <h1 className="text-2xl font-bold mb-4">Chess Stats Finder</h1>

      <div className="flex gap-2 mb-4">
        <input
          type="text"
          placeholder="Enter Chess Username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          className="p-2 border rounded-lg"
        />
        <button
          onClick={fetchStats}
          className="p-2 bg-blue-500 text-white rounded-lg hover:bg-blue-700"
        >
          Get Stats
        </button>
      </div>

      {loading && <p>Loading...</p>}
      {error && <p className="text-red-500">{error}</p>}

      {stats && (
        <div className="bg-white p-4 rounded-lg shadow-lg w-96">
          <h2 className="text-xl font-semibold">Stats for {stats.username}</h2>
          <p><strong>Total Games:</strong> {stats.total_games}</p>
          <p><strong>Win Percentage:</strong> {stats.win_percentage}%</p>
          <p><strong>Avg Opponent Rating:</strong> {stats.average_opponent_rating}</p>
          <p><strong>Most Frequent Opponent:</strong> {stats.most_common_opponent}</p>

          {/* PIE CHART: Win Percentage */}
          <div className="mt-4">
            <h3 className="text-lg font-semibold">Win Percentage</h3>
            <Pie
              data={{
                labels: ["Wins", "Losses"],
                datasets: [
                  {
                    data: [stats.win_percentage, 100 - stats.win_percentage],
                    backgroundColor: ["#4CAF50", "#F44336"],
                  },
                ],
              }}
            />
          </div>

          {/* BAR CHART: Most Common Openings */}
          <div className="mt-4">
            <h3 className="text-lg font-semibold">Most Common Openings</h3>
            <Bar
              data={{
                labels: stats.most_common_openings.map((o) => o.name),
                datasets: [
                  {
                    label: "Number of Games",
                    data: stats.most_common_openings.map((o) => o.count),
                    backgroundColor: "#3498db",
                  },
                ],
              }}
              options={{ scales: { y: { beginAtZero: true } } }}
            />
          </div>

          {/* BAR CHART: Game Lengths */}
          <div className="mt-4">
            <h3 className="text-lg font-semibold">Game Lengths (Moves)</h3>
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
      )}
    </div>
  );
};

export default ChessStats;
