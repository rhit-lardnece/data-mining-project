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
    feature_set: "default"
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
          plot_type: "scatter",
          feature_set: params.feature_set   // pass the new parameter
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

  const handlePointClick = async (event) => {
    const pointIndex = event.points[0].pointIndex;
    const playerName = clusteringData.player_features[pointIndex].player;
    try {
      const res = await fetch(`/chess_stats?username=${encodeURIComponent(playerName)}`);
      if (!res.ok) throw new Error("Failed to fetch player details");
      const details = await res.json();
      setSelectedPlayer(details);
    } catch (err) {
      setError("Error fetching detailed player info.");
    }
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
        <select name="feature_set" value={params.feature_set} onChange={handleChange} className="border p-2 m-2">
          <option value="default">Default Features</option>
          <option value="all">All Features (with game types)</option>
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
                  marker: { 
                    size: 14, 
                    color: clusteringData.player_features.map((player) => clusteringData.cluster_summary.find(cluster => cluster.cluster === player.cluster).cluster_color) 
                  },
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
                  <h4 className="font-bold text-xl mb-2">
                    <span style={{ backgroundColor: cluster.cluster_color, display: 'inline-block', width: '10px', height: '10px', marginRight: '8px' }}></span>
                    Cluster {cluster.cluster}
                  </h4>
                  <p className="text-lg">Average ELO: {cluster.avg_elo.toFixed(2)}</p>
                  <p className="text-lg">Average Opponent ELO: {cluster.avg_opponent_elo.toFixed(2)}</p>
                  <p className="text-lg">Players Count: {cluster.player_count}</p>
                </div>
              ))}
            </div>
          </div>
          {/* NEW: Detailed Cluster Stats */}
          <div className="mb-8">
            <h3 className="text-2xl font-semibold mb-4 text-center">Detailed Cluster Stats</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {Object.entries(clusteringData.detailed_cluster_stats).map(([cluster, stats]) => (
                <div key={cluster} className="bg-white p-6 rounded-lg shadow-lg">
                  <h4 className="font-bold text-xl mb-2">
                    <span style={{ backgroundColor: stats.cluster_color, display: 'inline-block', width: '10px', height: '10px', marginRight: '8px' }}></span>
                    Cluster {cluster}
                  </h4>
                  <p className="text-lg">Average Games Played: {stats.avg_games.toFixed(2)}</p>
                  <p className="text-lg">Average ELO: {stats.avg_elo.toFixed(2)}</p>
                  <p className="text-lg">Average Opponent ELO: {stats.avg_opponent_elo.toFixed(2)}</p>
                  {stats.avg_game_types && Object.keys(stats.avg_game_types).length > 0 && (
                    <div className="mt-4">
                      <h5 className="font-semibold text-lg">Average Game Types:</h5>
                      <ul>
                        {Object.entries(stats.avg_game_types).map(([variant, avgCount]) => (
                          <li key={variant} className="text-lg">{variant}: {avgCount.toFixed(2)}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
          {selectedPlayer && (
            <div className="mt-8">
              <h3 className="text-2xl font-semibold mb-4 text-center">Player Details</h3>
              <div className="bg-white p-6 rounded-lg shadow-lg">
                <p className="text-lg"><strong>Player:</strong> {selectedPlayer.username}</p>
                <p className="text-lg"><strong>Total Games:</strong> {selectedPlayer.total_games}</p>
                <p className="text-lg"><strong>Wins:</strong> {selectedPlayer.wins}</p>
                <p className="text-lg"><strong>Losses:</strong> {selectedPlayer.losses}</p>
                <p className="text-lg"><strong>Draws:</strong> {selectedPlayer.draws}</p>
                <p className="text-lg"><strong>Average Rating:</strong> {selectedPlayer.average_rating}</p>
                <p className="text-lg"><strong>Average Opponent Rating:</strong> {selectedPlayer.average_opponent_rating.toFixed(2)}</p>
                <p className="text-lg"><strong>Most Common Opponent:</strong> {selectedPlayer.most_common_opponent}</p>
                {selectedPlayer.opening_winrates && selectedPlayer.opening_winrates.length > 0 && (
                  <div className="mt-4">
                    <h4 className="text-xl font-bold">Opening Winrates:</h4>
                    <ul>
                      {selectedPlayer.opening_winrates.map(op => (
                        <li key={op.name} className="text-lg">{op.name}: {op.winrate.toFixed(2)}%</li>
                      ))}
                    </ul>
                  </div>
                )}
                {selectedPlayer.variant_stats && Object.keys(selectedPlayer.variant_stats).length > 0 && (
                  <div className="mt-4">
                    <h4 className="text-xl font-bold">Variant Stats:</h4>
                    <ul>
                      {Object.entries(selectedPlayer.variant_stats).map(([variant, stats]) => (
                        <li key={variant} className="text-lg">
                          <strong>{variant}:</strong> {stats.total_games} games (W:{stats.wins} / L:{stats.losses} / D:{stats.draws})
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}

export default PlayerClustering;
