// src/pages/PlayerClustering.js
import React, { useState, useEffect } from "react";

function PlayerClustering() {
  const [clusteringData, setClusteringData] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

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

  return (
    <div className="max-w-4xl mx-auto">
      <h2 className="text-3xl font-bold mb-4">Player Clustering</h2>
      {loading && <p>Loading clustering data...</p>}
      {error && <p className="text-red-500">{error}</p>}
      {clusteringData && (
        <>
          <div className="mb-6">
            <h3 className="text-xl font-semibold mb-2">Clustering Scatter Plot</h3>
            <img src={`data:image/png;base64,${clusteringData.scatter_plot}`} alt="Clustering Scatter Plot" className="w-full border rounded" />
          </div>
          <div>
            <h3 className="text-xl font-semibold mb-2">Cluster Summaries</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {clusteringData.cluster_summary.map((cluster, index) => (
                <div key={index} className="bg-white p-4 rounded shadow">
                  <h4 className="font-bold">Cluster {cluster.cluster}</h4>
                  <p>Average ELO: {cluster.avg_elo.toFixed(2)}</p>
                  <p>Average Opponent ELO: {cluster.avg_opponent_elo.toFixed(2)}</p>
                  <p>Players Count: {cluster.player_count}</p>
                </div>
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  );
}

export default PlayerClustering;
