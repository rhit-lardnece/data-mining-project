import React, { useState, useEffect } from "react";
import axios from "axios";
import UsernameInput from "../components/UsernameInput";
import ExampleUsernames from "../components/ExampleUsernames";
import WinPercentageChart from "../components/WinPercentageChart";
import OpeningsWinRatesChart from "../components/OpeningsWinRatesChart";
import GameLengthsChart from "../components/GameLengthsChart";
import HigherEloWinPercentageChart from "../components/HigherEloWinPercentageChart";
import LowerEloWinPercentageChart from "../components/LowerEloWinPercentageChart";

const PersonalizedStats = () => {
  const [username, setUsername] = useState("");
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [examples, setExamples] = useState([]);

  useEffect(() => {
    const fetchExamples = async () => {
      try {
        const response = await axios.get("/example_usernames");
        setExamples(response.data.examples);
      } catch (err) {
        console.error("Error fetching example usernames:", err);
      }
    };

    fetchExamples();
  }, []);

  const fetchStats = async () => {
    if (!username) {
      setError("Please enter a username");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await axios.get(`/chess_stats?username=${username}`);
      setStats(response.data);
    } catch (err) {
      setError("Error fetching data. Make sure the username exists.");
      setStats(null);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-6xl mx-auto">
      <h1 className="text-5xl font-bold mb-8">Personalized Chess Stats</h1>
      <div className="mb-4">
        <UsernameInput username={username} setUsername={setUsername} fetchStats={fetchStats} />
        {error && <p className="text-red-500">{error}</p>}
      </div>
      <ExampleUsernames examples={examples} setUsername={setUsername} />
      {loading && <p>Loading...</p>}
      {stats && (
        <div className="mt-8 space-y-8">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-white p-6 rounded shadow">
              <h2 className="font-bold text-xl">Total Games</h2>
              <p className="text-lg">{stats.total_games}</p>
            </div>
            <div className="bg-white p-6 rounded shadow">
              <h2 className="font-bold text-xl">Average Rating</h2>
              <p className="text-lg">{stats.average_rating}</p>
            </div>
            <div className="bg-white p-6 rounded shadow">
              <h2 className="font-bold text-xl">Wins / Losses / Draws</h2>
              <p className="text-lg">{stats.wins} / {stats.losses} / {stats.draws}</p>
            </div>
          </div>
          <div>
            <h2 className="text-3xl font-bold mt-8">Openings Distribution</h2>
            <OpeningsWinRatesChart stats={stats} />
          </div>
          <div>
            <h2 className="text-3xl font-bold mt-8">Win Percentage</h2>
            <WinPercentageChart stats={stats} />
          </div>
          <div>
            <h2 className="text-3xl font-bold mt-8">Game Lengths</h2>
            <GameLengthsChart stats={stats} />
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <HigherEloWinPercentageChart stats={stats} />
            <LowerEloWinPercentageChart stats={stats} />
          </div>
        </div>
      )}
    </div>
  );
};

export default PersonalizedStats;