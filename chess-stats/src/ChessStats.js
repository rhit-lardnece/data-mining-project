import React, { useState } from "react";
import axios from "axios";
import { Pie, Bar } from "react-chartjs-2";
import { Chart, ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement } from "chart.js";

Chart.register(ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement);

const ChessStats = () => {
  const [username, setUsername] = useState("");
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchStats = async () => {
    if (!username.trim()) {
      setError("Please enter a valid username.");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await axios.get(`http://127.0.0.1:5000/chess_stats?username=${username}`);
      
      if (!response.data || Object.keys(response.data).length === 0) {
        setError("No data found for this user.");
        setStats(null);
        return;
      }

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
      <h1 className="text-2xl font-bold mb-4">Chess Stats</h1>

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
          <p><strong>Total Games:</strong> {stats.total_games || "N/A"}</p>
          <p><strong>Win Percentage:</strong> {stats.win_percentage ? `${stats.win_percentage}%` : "N/A"}</p>
          <p><strong>Avg Opponent Rating:</strong> {stats.average_opponent_rating || "N/A"}</p>
          <p><strong>Most Frequent Opponent:</strong> {stats.most_common_opponent || "N/A"}</p>

          {stats.wins !== undefined && stats.draws !== undefined && stats.losses !== undefined ? (
            <div className="mt-4">
              <h3 className="text-lg font-semibold">Game Outcomes</h3>
              <Pie
                data={{
                  labels: ["Wins", "Draws", "Losses"],
                  datasets: [
                    {
                      data: [stats.wins, stats.draws, stats.losses],
                      backgroundColor: ["#4CAF50", "#FFC107", "#F44336"],
                    },
                  ],
                }}
              />
            </div>
          ) : (
            <p className="text-gray-500">No game outcome data available.</p>
          )}

          {stats.most_common_openings && stats.most_common_openings.length > 0 ? (
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
          ) : (
            <p className="text-gray-500">No opening data available.</p>
          )}

          {stats.game_lengths && stats.game_lengths.length > 0 ? (
            <div className="mt-4">
              <h3 className="text-lg font-semibold">Game Length Frequency</h3>
              <Bar
                data={{
                  labels: [...new Set(stats.game_lengths)].sort((a, b) => a - b),
                  datasets: [
                    {
                      label: "Frequency",
                      data: Object.values(
                        stats.game_lengths.reduce((acc, move) => {
                          acc[move] = (acc[move] || 0) + 1;
                          return acc;
                        }, {})
                      ),
                      backgroundColor: "#2c3e50",
                    },
                  ],
                }}
                options={{
                  scales: {
                    x: {
                      title: {
                        display: true,
                        text: "Number of Moves",
                      },
                    },
                    y: {
                      title: {
                        display: true,
                        text: "Frequency",
                      },
                      beginAtZero: true,
                    },
                  },
                }}
              />
            </div>
          ) : (
            <p className="text-gray-500">No game length data available.</p>
          )}
        </div>
      )}
    </div>
  );
};

export default ChessStats;
