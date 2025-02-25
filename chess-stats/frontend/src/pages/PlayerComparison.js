import React, { useState, useEffect } from "react";
import axios from "axios";
import ExampleUsernames from "../components/ExampleUsernames";

function PlayerComparison() {
  const [player1, setPlayer1] = useState("");
  const [player2, setPlayer2] = useState("");
  const [comparisonResult, setComparisonResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [examples, setExamples] = useState([]);
  const [error, setError] = useState(null);

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

  const setUsername = (username, player) => {
    if (player === 1) {
      setPlayer1(username);
    } else if (player === 2) {
      setPlayer2(username);
    }
  };

  const handleCompare = async () => {
    setError(null);
    setLoading(true);
    try {
      const response = await fetch("/api/compare_players", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ player1, player2 }),
      });
      if (!response.ok) {
        throw new Error("Network response was not ok");
      }
      const data = await response.json();
      setComparisonResult(data);
    } catch (error) {
      setError("Error fetching comparison data. Please try again.");
      setComparisonResult(null);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto">
      <h2 className="text-3xl font-bold mb-4">Player Comparison</h2>
      <div className="flex flex-col md:flex-row md:space-x-4 mb-4">
        <input
          type="text"
          placeholder="Player 1"
          value={player1}
          onChange={(e) => setPlayer1(e.target.value)}
          className="p-2 border rounded mb-2 md:mb-0 flex-1"
        />
        <input
          type="text"
          placeholder="Player 2"
          value={player2}
          onChange={(e) => setPlayer2(e.target.value)}
          className="p-2 border rounded flex-1"
        />
      </div>
      <ExampleUsernames examples={examples} setUsername={setUsername} />

      <button
        onClick={handleCompare}
        className="p-2 bg-blue-500 text-white rounded hover:bg-blue-700"
      >
        Compare
      </button>
      {loading && <p className="mt-4">Comparing players...</p>}
      {error && <p className="mt-4 text-red-500">{error}</p>}
      {comparisonResult && (
        <div className="mt-6 bg-white p-4 rounded shadow">
          <h3 className="text-xl font-bold mb-2">Comparison Result</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <h4 className="font-semibold">{comparisonResult.player1.username}</h4>
              <p>Total Games: {comparisonResult.player1.total_games}</p>
              <p>Average Rating: {comparisonResult.player1.average_rating}</p>
              <p>Wins: {comparisonResult.player1.wins}</p>
              <p>Losses: {comparisonResult.player1.losses}</p>
              <p>Draws: {comparisonResult.player1.draws}</p>
              <h5 className="font-semibold mt-2">Prediction Details:</h5>
              <p>Result: {comparisonResult.prediction_details_player1.result}</p>
              <p>Feature Contributions:</p>
              <ul>
                {comparisonResult.prediction_details_player1.feature_contributions.map(([feature, value]) => (
                  <li key={feature}>{feature}: {value.toFixed(4)}</li>
                ))}
              </ul>
              {comparisonResult.prediction_details_player1.opening_effects && (
                <div className="mt-4">
                  <h4 className="font-semibold">Opening Effects on Prediction (Player 1):</h4>
                  <ul>
                    {Object.entries(comparisonResult.prediction_details_player1.opening_effects).map(([opening, result]) => (
                      <li key={opening}>{opening}: {result}</li>
                    ))}
                  </ul>
                </div>
              )}
              {comparisonResult && comparisonResult.prediction_details_player1 && (
                <div className="mt-4">
                  <h4 className="font-semibold">Opening Effects on Prediction (Player 1):</h4>
                  <ul>
                    {Object.entries(comparisonResult.prediction_details_player1.opening_effects).map(([opening, result]) => (
                      <li key={opening}>{opening}: {result}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
            <div>
              <h4 className="font-semibold">{comparisonResult.player2.username}</h4>
              <p>Total Games: {comparisonResult.player2.total_games}</p>
              <p>Average Rating: {comparisonResult.player2.average_rating}</p>
              <p>Wins: {comparisonResult.player2.wins}</p>
              <p>Losses: {comparisonResult.player2.losses}</p>
              <p>Draws: {comparisonResult.player2.draws}</p>
              <h5 className="font-semibold mt-2">Prediction Details:</h5>
              <p>Result: {comparisonResult.prediction_details_player2.result}</p>
              <p>Feature Contributions:</p>
              <ul>
                {comparisonResult.prediction_details_player2.feature_contributions.map(([feature, value]) => (
                  <li key={feature}>{feature}: {value.toFixed(4)}</li>
                ))}
              </ul>
              {comparisonResult.prediction_details_player2.opening_effects && (
                <div className="mt-4">
                  <h4 className="font-semibold">Opening Effects on Prediction (Player 2):</h4>
                  <ul>
                    {Object.entries(comparisonResult.prediction_details_player2.opening_effects).map(([opening, result]) => (
                      <li key={opening}>{opening}: {result}</li>
                    ))}
                  </ul>
                </div>
              )}
              {comparisonResult && comparisonResult.prediction_details_player2 && (
                <div className="mt-4">
                  <h4 className="font-semibold">Opening Effects on Prediction (Player 2):</h4>
                  <ul>
                    {Object.entries(comparisonResult.prediction_details_player2.opening_effects).map(([opening, result]) => (
                      <li key={opening}>{opening}: {result}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </div>
          <div className="mt-4">
            <p className="font-bold">Predicted Winner: {comparisonResult.predicted_winner}</p>
            <p>Basis: {comparisonResult.comparison_basis}</p>
          </div>
        </div>
      )}
    </div>
  );
}

export default PlayerComparison;
