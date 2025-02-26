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

  const setUsername = (username) => {
    if (!player1) {
      setPlayer1(username);
    } else if (!player2) {
      setPlayer2(username);
    }
  };

  const handleCompare = async () => {
    setError(null);
    setLoading(true);
    try {
      const response = await axios.post("/compare_players", {
        player1,
        player2
      });
      if (response.status !== 200) {
        throw new Error("Network response was not ok");
      }
      setComparisonResult(response.data);
    } catch (error) {
      setError("Error fetching comparison data. Please try again.");
      setComparisonResult(null);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-4">
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
      <ExampleUsernames examples={examples} setUsername={setUsername} player1={player1} player2={player2} />

      <button
        onClick={handleCompare}
        className="p-2 bg-blue-500 text-white rounded hover:bg-blue-700"
      >
        Compare
      </button>
      {loading && <p className="mt-4">Comparing players...</p>}
      {error && <p className="mt-4 text-red-500">{error}</p>}
      {comparisonResult && (
        <div className="mt-6 bg-white p-4 rounded shadow space-y-6">
          {/* Color-specific predictions */}
          <div>
            <h3 className="text-xl font-bold mb-2">Color-Specific Prediction</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <h4 className="font-semibold">{player1} as White</h4>
                <p>Prediction: {comparisonResult.color_specific.player1_as_white.prediction}</p>
                <p>Top 5 Feature Contributions:</p>
                <ul>
                  {comparisonResult.color_specific.player1_as_white.short_feature_contributions.map(([feature, value]) => (
                    <li key={feature}>{feature}: {value.toFixed(4)}</li>
                  ))}
                </ul>
              </div>
              <div>
                <h4 className="font-semibold">{player2} as Black</h4>
                <p>Prediction: {comparisonResult.color_specific.player2_as_black.prediction}</p>
                <p>Top 5 Feature Contributions:</p>
                <ul>
                  {comparisonResult.color_specific.player2_as_black.short_feature_contributions.map(([feature, value]) => (
                    <li key={feature}>{feature}: {value.toFixed(4)}</li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
          {/* Color-agnostic prediction */}
          <div>
            <h3 className="text-xl font-bold mb-2">Color-Agnostic Prediction</h3>
            <p>Based solely on average ratings:</p>
            <p>{player1} Average Rating: {comparisonResult.color_agnostic.player1_average_rating}</p>
            <p>{player2} Average Rating: {comparisonResult.color_agnostic.player2_average_rating}</p>
            <p>Prediction: {comparisonResult.color_agnostic.prediction}</p>
          </div>
          {/* Top openings predictions */}
          {/* <div>
            <h3 className="text-xl font-bold mb-2">Top Openings Wins and Losses</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <h4 className="font-semibold">{player1} Top Openings</h4>
                <ul>
                  {comparisonResult.top_opening_predictions.player1.map(item => (
                    <li key={item.opening}>
                      {item.opening}: {item.wins} wins, {item.losses} losses
                    </li>
                  ))}
                </ul>
              </div>
              <div>
                <h4 className="font-semibold">{player2} Top Openings</h4>
                <ul>
                  {comparisonResult.top_opening_predictions.player2.map(item => (
                    <li key={item.opening}>
                      {item.opening}: {item.wins} wins, {item.losses} losses
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </div> */}
          {/* Additional info if needed */}
          <div>
            <p className="font-bold">Additional details:</p>
            <p>Comparison Basis: {comparisonResult.comparison_basis}</p>
            <p>Model Accuracy: {comparisonResult.model_accuracy}</p>
            <p>Cross Validation Score: {comparisonResult.cross_validation_score}</p>
          </div>
        </div>
      )}
    </div>
  );
}

export default PlayerComparison;
