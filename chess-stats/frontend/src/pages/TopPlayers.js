import React, { useState, useEffect } from "react";

function TopPlayers() {
  const [topPlayers, setTopPlayers] = useState([]);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchTopPlayers = async () => {
      setLoading(true);
      setError(null);
      try {
        const response = await fetch("/top_players");
        if (!response.ok) {
          throw new Error("Network response was not ok");
        }
        const data = await response.json();
        setTopPlayers(data.top_players);
      } catch (error) {
        setError("Error fetching top players. Please try again.");
      } finally {
        setLoading(false);
      }
    };

    fetchTopPlayers();
  }, []);

  return (
    <div className="max-w-4xl mx-auto">
      <h2 className="text-3xl font-bold mb-4">Top Players</h2>
      {loading && <p>Loading top players...</p>}
      {error && <p className="text-red-500">{error}</p>}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {topPlayers.map((player, index) => (
          <div key={index} className="bg-white p-4 rounded shadow">
            <h3 className="font-bold">{player.username}</h3>
            <p>Total Games: {player.total_games}</p>
            <p>Average Rating: {player.average_rating}</p>
            <p>Wins: {player.wins} | Losses: {player.losses} | Draws: {player.draws}</p>
          </div>
        ))}
      </div>
    </div>
  );
}

export default TopPlayers;
