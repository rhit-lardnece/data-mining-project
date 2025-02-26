import React, { useState, useCallback } from "react";
import Plot from "react-plotly.js";

function PlayerClustering() {
  const [clusteringData, setClusteringData] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const [selectedPlayer, setSelectedPlayer] = useState(null);
  const [params, setParams] = useState({
    num_clusters: 5,
    x_axis: "avg_elo",
    y_axis: "avg_opponent_elo",
  });

  // Add a mapping for axis labels
  const axisLabels = {
    avg_elo: "Average ELO",
    avg_opponent_elo: "Average Opponent ELO",
    games: "Games Played"
  };

  const handleChange = (e) => {
    setParams({ ...params, [e.target.name]: e.target.value });
  };

  const fetchClustering = useCallback(async () => {
    setError(null);
    setLoading(true);
    try {
      const response = await fetch("/api/kmeans", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          num_clusters: Number(params.num_clusters),
          x_axis: params.x_axis,
          y_axis: params.y_axis,
          reduction_method: "pca",
          plot_type: "scatter"
        }),
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
  }, [params]);

  const handlePointClick = (event) => {
    const pointIndex = event.points[0].pointIndex;
    const playerData = clusteringData.player_features[pointIndex];
    setSelectedPlayer(playerData);
  };

  return (
    <div className="max-w-6xl mx-auto p-6">
      <h2 className="text-4xl font-bold mb-6 text-center">Player Clustering</h2>
      <div className="mb-6 text-center">
        <input name="num_clusters" value={params.num_clusters} onChange={handleChange} placeholder="Number of Clusters" className="border p-2 m-2"/>
        <select name="x_axis" value={params.x_axis} onChange={handleChange} className="border p-2 m-2">
          <option value="avg_elo">Average ELO</option>
          <option value="avg_opponent_elo">Average Opponent ELO</option>
          <option value="games">Games Played</option>
        </select>
        <select name="y_axis" value={params.y_axis} onChange={handleChange} className="border p-2 m-2">
          <option value="avg_elo">Average ELO</option>
          <option value="avg_opponent_elo">Average Opponent ELO</option>
          <option value="games">Games Played</option>
        </select>
        <button onClick={fetchClustering} className="bg-blue-500 text-white p-2 m-2 rounded">Update Plot</button>
      </div>
      {loading && <p className="text-center text-lg">Loading clustering data...</p>}
      {error && <p className="text-center text-red-500 text-lg">{error}</p>}
      {clusteringData && (
        <>
          <div className="mb-8">
            <h3 className="text-2xl font-semibold mb-4 text-center">Clustering Plot</h3>
            <Plot
              data={[
                {
                  x: clusteringData.player_features.map((player) => player[params.x_axis]),
                  y: clusteringData.player_features.map((player) => player[params.y_axis]),
                  text: clusteringData.player_features.map((player) => player.player),
                  mode: "markers",
                  marker: { size: 14, color: clusteringData.player_features.map((player) => player.cluster) },
                  type: "scatter",
                },
              ]}
              layout={{
                title: "Player Clustering",
                hovermode: "closest",
                width: 800,
                height: 600,
                xaxis: { title: { text: axisLabels[params.x_axis] || params.x_axis } },
                yaxis: { title: { text: axisLabels[params.y_axis] || params.y_axis } }
              }}
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
