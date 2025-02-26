import matplotlib
matplotlib.use("Agg")
import pandas as pd
import logging
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE  # new import
from sklearn.metrics import silhouette_score
import matplotlib.pyplot as plt
import seaborn as sns
import io, base64

logger = logging.getLogger(__name__)

def aggregate_player_features(df):
    logger.info("Aggregating player features for KMeans clustering...")
    stats = {}
    for idx, row in df.iterrows():
        for side in ["White", "Black"]:
            player = row[side]
            opponent_elo = row["BlackElo"] if side == "White" else row["WhiteElo"]
            player_elo = row["WhiteElo"] if side == "White" else row["BlackElo"]
            if player not in stats:
                stats[player] = {"games": 0, "total_elo": 0, "total_opp_elo": 0}
            stats[player]["games"] += 1
            stats[player]["total_elo"] += player_elo
            stats[player]["total_opp_elo"] += opponent_elo
        if idx % 1000 == 0:
            logger.debug(f"Aggregated features for {idx} games")
    data = []
    for player, s in stats.items():
        data.append({
            "player": player,
            "games": s["games"],
            "avg_elo": s["total_elo"] / s["games"],
            "avg_opponent_elo": s["total_opp_elo"] / s["games"]
        })
    df_features = pd.DataFrame(data)
    logger.info("Aggregated player features shape: %s", df_features.shape)
    return df_features

def perform_kmeans(df, num_clusters, x_axis="avg_elo", y_axis="avg_opponent_elo", reduction_method="pca", plot_type="scatter"):
    logger.info("Performing KMeans clustering on %s and %s with %d clusters", x_axis, y_axis, num_clusters)
    if x_axis not in df.columns or y_axis not in df.columns:
        raise ValueError("Invalid x_axis or y_axis parameter.")
    X = df[[x_axis, y_axis]].values
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    # Use kmeans++ initialization.
    kmeans = KMeans(n_clusters=num_clusters, init="k-means++", random_state=42)
    labels = kmeans.fit_predict(X_scaled)
    df["cluster"] = labels

    sil_score = silhouette_score(X_scaled, labels)
    
    # Always use PCA for dimensionality reduction.
    logger.info("Using PCA for dimensionality reduction")
    reducer = PCA(n_components=2, random_state=42)
    X_reduced = reducer.fit_transform(X_scaled)
    df["dim1"] = X_reduced[:, 0]
    df["dim2"] = X_reduced[:, 1]

    # Always generate a scatter plot.
    logger.info("Generating scatter plot")
    plt.figure(figsize=(8, 6))
    sns.scatterplot(x=x_axis, y=y_axis, hue="cluster", data=df, palette="viridis")
    plt.title("KMeans Clustering")
    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    plot_base64 = base64.b64encode(buf.getvalue()).decode("utf-8")
    plt.close()

    cluster_summary = df.groupby("cluster").agg(
        avg_elo=(x_axis, "mean"),
        avg_opponent_elo=(y_axis, "mean"),
        player_count=("player", "count")
    ).reset_index().to_dict(orient="records")
    
    logger.info("KMeans clustering complete. Silhouette score: %.4f", sil_score)
    return {
        "clusters": labels.tolist(),
        "silhouette_score": sil_score,
        "player_features": df.to_dict(orient="records"),
        "centroids": kmeans.cluster_centers_.tolist(),
        "dimension_reduction": "pca",
        "plot_type": "scatter",
        "scatter_plot": plot_base64,
        "cluster_summary": cluster_summary
    }
