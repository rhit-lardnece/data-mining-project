import React, { useState, useEffect } from "react";
import Plot from "react-plotly.js";

function PlayerClustering() {
  const [clusteringData, setClusteringData] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const [selectedPlayer, setSelectedPlayer] = useState(null);

  useEffect(() => {
    const performClustering = async () => {
      setError(null);
      setLoading(true);
      try {
        const response = await fetch("/api/kmeans", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ num_clusters: 5 }),
        });
        if (!response.ok) {
          throw new Error("Network response was not ok");
        }
        const data = await response.json();
        setClusteringData(data);
      } catch (error) {
        setError("Error fetching clustering data. Please try again.");
      } finally {
        setLoading(false);
      }
    };

    performClustering();
  }, []);

  const handlePointClick = (event) => {
    const pointIndex = event.points[0].pointIndex;
    const playerData = clusteringData.player_features[pointIndex];
    setSelectedPlayer(playerData);
  };

  return (
    <div className="max-w-6xl mx-auto p-6">
      <h2 className="text-4xl font-bold mb-6 text-center">Player Clustering</h2>
      {loading && <p className="text-center text-lg">Loading clustering data...</p>}
      {error && <p className="text-center text-red-500 text-lg">{error}</p>}
      {clusteringData && (
        <>
          <div className="mb-8">
            <h3 className="text-2xl font-semibold mb-4 text-center">Clustering Scatter Plot</h3>
            <Plot
              data={[
                {
                  x: clusteringData.player_features.map((player) => player.avg_elo),
                  y: clusteringData.player_features.map((player) => player.avg_opponent_elo),
                  text: clusteringData.player_features.map((player) => player.player),
                  mode: "markers",
                  marker: { size: 14, color: clusteringData.player_features.map((player) => player.cluster) },
                  type: "scatter",
                },
              ]}
              layout={{ title: "Player Clustering", hovermode: "closest", width: 800, height: 600 }}
              onClick={handlePointClick}
            />
          </div>
          <div className="mb-8">
            <h3 className="text-2xl font-semibold mb-4 text-center">Cluster Summaries</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {clusteringData.cluster_summary.map((cluster, index) => (
                <div key={index} className="bg-white p-6 rounded-lg shadow-lg">
                  <h4 className="font-bold text-xl mb-2">Cluster {cluster.cluster}</h4>
                  <p className="text-lg">Average ELO: {cluster.avg_elo.toFixed(2)}</p>
                  <p className="text-lg">Average Opponent ELO: {cluster.avg_opponent_elo.toFixed(2)}</p>
                  <p className="text-lg">Players Count: {cluster.player_count}</p>
                </div>
              ))}
            </div>
          </div>
          {selectedPlayer && (
            <div className="mt-8">
              <h3 className="text-2xl font-semibold mb-4 text-center">Player Details</h3>
              <div className="bg-white p-6 rounded-lg shadow-lg">
                <p className="text-lg"><strong>Player:</strong> {selectedPlayer.player}</p>
                <p className="text-lg"><strong>Games:</strong> {selectedPlayer.games}</p>
                <p className="text-lg"><strong>Average ELO:</strong> {selectedPlayer.avg_elo.toFixed(2)}</p>
                <p className="text-lg"><strong>Average Opponent ELO:</strong> {selectedPlayer.avg_opponent_elo.toFixed(2)}</p>
                <p className="text-lg"><strong>Cluster:</strong> {selectedPlayer.cluster}</p>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}

export default PlayerClustering;
