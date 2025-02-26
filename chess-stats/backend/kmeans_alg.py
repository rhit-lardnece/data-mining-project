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
from collections import Counter  # new import

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
                stats[player] = {
                    "games": 0,
                    "total_elo": 0,
                    "total_opp_elo": 0,
                    "openings": [],       # accumulate openings
                    "game_types": {}      # new field to count game variants
                }
            stats[player]["games"] += 1
            stats[player]["total_elo"] += player_elo
            stats[player]["total_opp_elo"] += opponent_elo
            # Accumulate openings if available
            if "Opening" in df.columns and pd.notnull(row["Opening"]):
                stats[player]["openings"].append(row["Opening"])
            # Accumulate game variant counts if available
            if "Variant" in df.columns and pd.notnull(row["Variant"]):
                variant = row["Variant"]
                stats[player]["game_types"][variant] = stats[player]["game_types"].get(variant, 0) + 1
        if idx % 1000 == 0:
            logger.debug(f"Aggregated features for {idx} games")
    data = []
    for player, s in stats.items():
        most_common_opening = None
        if s["openings"]:
            counter = Counter(s["openings"])
            most_common_opening, _ = counter.most_common(1)[0]
        data.append({
            "player": player,
            "games": s["games"],
            "avg_elo": s["total_elo"] / s["games"],
            "avg_opponent_elo": s["total_opp_elo"] / s["games"],
            "most_common_opening": most_common_opening,  # new feature
            "game_types": s["game_types"]                 # new feature for game variants
        })
    df_features = pd.DataFrame(data)
    logger.info("Aggregated player features shape: %s", df_features.shape)
    return df_features

def perform_kmeans(df, num_clusters, x_axis="avg_elo", y_axis="avg_opponent_elo", reduction_method="pca", plot_type="scatter", use_all_features=False):
    logger.info("Performing KMeans clustering with %d clusters", num_clusters)
    if use_all_features:
        # Build full feature matrix with default numeric features and game type counts.
        import numpy as np
        base_features = ["games", "avg_elo", "avg_opponent_elo"]
        X_list = []
        # First, build a set of all game types
        all_types = set()
        for row in df["game_types"]:
            if isinstance(row, dict):
                all_types.update(row.keys())
        all_types = sorted(list(all_types))
        # For each record, combine base features with game type counts (0 if not present)
        for idx, row in df.iterrows():
            features = [row[feat] for feat in base_features]
            if isinstance(row["game_types"], dict):
                for gt in all_types:
                    features.append(row["game_types"].get(gt, 0))
            else:
                features.extend([0]*len(all_types))
            X_list.append(features)
        X = np.array(X_list)
    else:
        if x_axis not in df.columns or y_axis not in df.columns:
            raise ValueError("Invalid x_axis or y_axis parameter.")
        X = df[[x_axis, y_axis]].values
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    # Use kmeans++ initialization.
    kmeans = KMeans(n_clusters=num_clusters, init="k-means++", random_state=42)
    labels = kmeans.fit_predict(X_scaled)
    df["cluster"] = labels

    # NEW: Generate cluster colors using the viridis palette
    cluster_colors = sns.color_palette("viridis", num_clusters).as_hex()  # list of hex colors

    sil_score = silhouette_score(X_scaled, labels)
    
    # Dimensionality reduction using PCA.
    logger.info("Using PCA for dimensionality reduction")
    reducer = PCA(n_components=2, random_state=42)
    X_reduced = reducer.fit_transform(X_scaled)
    df["dim1"] = X_reduced[:, 0]
    df["dim2"] = X_reduced[:, 1]

    # Generate scatter plot.
    logger.info("Generating scatter plot")
    plt.figure(figsize=(8, 6))
    sns.scatterplot(x="dim1", y="dim2", hue="cluster", data=df, palette="viridis")
    plt.title("KMeans Clustering")
    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    plot_base64 = base64.b64encode(buf.getvalue()).decode("utf-8")
    plt.close()

    # Create a summary using the default numeric columns.
    cluster_summary = df.groupby("cluster").agg(
        avg_elo=("avg_elo", "mean"),
        avg_opponent_elo=("avg_opponent_elo", "mean"),
        player_count=("player", "count")
    ).reset_index().to_dict(orient="records")
    # NEW: Append cluster color to each summary
    for summary in cluster_summary:
        summary["cluster_color"] = cluster_colors[int(summary["cluster"])]

    # New code to compute all clusters' numeric profiles and a simple cluster key.
    numeric_cols = df.select_dtypes("number").columns
    cluster_profiles = df.groupby("cluster")[numeric_cols].mean().to_dict(orient="index")
    global_means = df[numeric_cols].mean()
    cluster_key = {}
    for cluster, profile in cluster_profiles.items():
        key_info = {}
        for col, val in profile.items():
            # Compare cluster average to global average.
            key_info[col] = "High" if val > global_means[col] else "Low"
        cluster_key[cluster] = key_info

    # NEW: Compute detailed cluster statistics (including averages for games and game variant counts)
    detailed_cluster_stats = {}
    for cluster in sorted(df["cluster"].unique()):
        cluster_df = df[df["cluster"] == cluster]
        avg_games = cluster_df["games"].mean()
        avg_elo = cluster_df["avg_elo"].mean()
        avg_opponent_elo = cluster_df["avg_opponent_elo"].mean()
        game_types_sum = {}
        for _, row in cluster_df.iterrows():
            if isinstance(row.get("game_types"), dict):
                for variant, cnt in row["game_types"].items():
                    game_types_sum[variant] = game_types_sum.get(variant, 0) + cnt
        # Compute average count per game type
        avg_game_types = {variant: total/len(cluster_df) for variant, total in game_types_sum.items()}
        # NEW: Include cluster_color in detailed stats
        detailed_cluster_stats[cluster] = {
            "avg_games": avg_games,
            "avg_elo": avg_elo,
            "avg_opponent_elo": avg_opponent_elo,
            "avg_game_types": avg_game_types,
            "cluster_color": cluster_colors[int(cluster)]
        }
    logger.info("KMeans clustering complete. Silhouette score: %.4f", sil_score)
    
    # Convert keys to strings for JSON serialization
    cluster_profiles = {str(k): v for k, v in cluster_profiles.items()}
    cluster_key = {str(k): v for k, v in cluster_key.items()}
    detailed_cluster_stats = {str(k): v for k, v in detailed_cluster_stats.items()}
    
    return {
        "clusters": labels.tolist(),
        "silhouette_score": sil_score,
        "player_features": df.to_dict(orient="records"),
        "centroids": kmeans.cluster_centers_.tolist(),
        "dimension_reduction": "pca",
        "plot_type": "scatter",
        "scatter_plot": plot_base64,
        "cluster_summary": cluster_summary,
        "cluster_profiles": cluster_profiles,      
        "cluster_key": cluster_key,                    
        "detailed_cluster_stats": detailed_cluster_stats 
    }
