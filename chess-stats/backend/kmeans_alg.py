import matplotlib
matplotlib.use("Agg")
import pandas as pd
import logging
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score
import matplotlib.pyplot as plt
import seaborn as sns
import io, base64
from collections import Counter

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
                    "param1_values": [],
                    "param2_values": [],
                    "openings": [],
                    "game_types": {},
                    "opening_counts": {},  # NEW: store opening counts
                    "variant_counts": {}   # NEW: store variant counts
                }
            stats[player]["games"] += 1
            stats[player]["total_elo"] += player_elo
            stats[player]["total_opp_elo"] += opponent_elo
            stats[player]["param1_values"].append(row.get("Param1", 0))
            stats[player]["param2_values"].append(row.get("Param2", 0))
            if "Opening" in df.columns and pd.notnull(row["Opening"]):
                opening = row["Opening"]
                stats[player]["openings"].append(opening)
                stats[player]["opening_counts"][opening] = stats[player]["opening_counts"].get(opening, 0) + 1
            if "Variant" in df.columns and pd.notnull(row["Variant"]):
                variant = row["Variant"]
                stats[player]["game_types"][variant] = stats[player]["game_types"].get(variant, 0) + 1
                stats[player]["variant_counts"][variant] = stats[player]["variant_counts"].get(variant, 0) + 1
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
            "param1": sum(s["param1_values"]) / s["games"],
            "param2": sum(s["param2_values"]) / s["games"],
            "param1_values": s["param1_values"],
            "param2_values": s["param2_values"],
            "most_common_opening": most_common_opening,
            "game_types": s["game_types"],
            "opening_counts": s["opening_counts"],  
            "variant_counts": s["variant_counts"]   
        })
    df_features = pd.DataFrame(data)
    logger.info("Aggregated player features shape: %s", df_features.shape)
    return df_features

def perform_kmeans(df, num_clusters, x_axis="avg_elo", y_axis="avg_opponent_elo", use_all_features=False):
    logger.info("Performing KMeans clustering with %d clusters", num_clusters)
    if use_all_features:
        import numpy as np
        base_features = ["games", "avg_elo", "avg_opponent_elo"]
        X_list = []
        all_types = set()
        all_openings = set()
        for row in df["game_types"]:
            if isinstance(row, dict):
                all_types.update(row.keys())
        for row in df["opening_counts"]:
            if isinstance(row, dict):
                all_openings.update(row.keys())
        all_types = sorted(list(all_types))
        all_openings = sorted(list(all_openings))
        for idx, row in df.iterrows():
            features = [row[feat] for feat in base_features]
            if isinstance(row["game_types"], dict):
                for gt in all_types:
                    features.append(row["game_types"].get(gt, 0))
            else:
                features.extend([0]*len(all_types))
            if isinstance(row["opening_counts"], dict):
                for op in all_openings:
                    features.append(row["opening_counts"].get(op, 0))
            else:
                features.extend([0]*len(all_openings))
            X_list.append(features)
        X = np.array(X_list)
    else:
        x_col = x_axis.replace("_values", "") if x_axis.endswith("_values") else x_axis
        y_col = y_axis.replace("_values", "") if y_axis.endswith("_values") else y_axis
        if x_col not in df.columns or y_col not in df.columns:
            raise ValueError("Invalid x_axis or y_axis parameter.")
        X = df[[x_col, y_col]].values
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    kmeans = KMeans(n_clusters=num_clusters, init="k-means++", random_state=42)
    labels = kmeans.fit_predict(X_scaled)
    df["cluster"] = labels

    cluster_colors = sns.color_palette("viridis", num_clusters).as_hex()

    sil_score = silhouette_score(X_scaled, labels)
    
    logger.info("Using PCA for dimensionality reduction")
    reducer = PCA(n_components=2, random_state=42)
    X_reduced = reducer.fit_transform(X_scaled)
    df["dim1"] = X_reduced[:, 0]
    df["dim2"] = X_reduced[:, 1]

    logger.info("Generating scatter plot")
    plt.figure(figsize=(8, 6))
    sns.scatterplot(x="dim1", y="dim2", hue="cluster", data=df, palette="viridis")
    plt.title("KMeans Clustering")
    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    plot_base64 = base64.b64encode(buf.getvalue()).decode("utf-8")
    plt.close()

    cluster_summary = df.groupby("cluster").agg(
        avg_elo=("avg_elo", "mean"),
        avg_opponent_elo=("avg_opponent_elo", "mean"),
        player_count=("player", "count")
    ).reset_index().to_dict(orient="records")
    for summary in cluster_summary:
        summary["cluster_color"] = cluster_colors[int(summary["cluster"])]

    numeric_cols = df.select_dtypes("number").columns
    cluster_profiles = df.groupby("cluster")[numeric_cols].mean().to_dict(orient="index")
    global_means = df[numeric_cols].mean()
    cluster_key = {}
    for cluster, profile in cluster_profiles.items():
        key_info = {}
        for col, val in profile.items():
            key_info[col] = "High" if val > global_means[col] else "Low"
        cluster_key[cluster] = key_info

    detailed_cluster_stats = {}
    for cluster in sorted(df["cluster"].unique()):
        cluster_df = df[df["cluster"] == cluster]
        avg_games = cluster_df["games"].mean()
        avg_elo = cluster_df["avg_elo"].mean()
        avg_opponent_elo = cluster_df["avg_opponent_elo"].mean()
        game_types_sum = {}
        opening_counts_sum = {}
        for _, row in cluster_df.iterrows():
            if isinstance(row.get("game_types"), dict):
                for variant, cnt in row["game_types"].items():
                    game_types_sum[variant] = game_types_sum.get(variant, 0) + cnt
            if isinstance(row.get("opening_counts"), dict):
                for opening, cnt in row["opening_counts"].items():
                    opening_counts_sum[opening] = opening_counts_sum.get(opening, 0) + cnt
        avg_game_types = {variant: total/len(cluster_df) for variant, total in game_types_sum.items()}
        avg_opening_counts = {opening: total/len(cluster_df) for opening, total in opening_counts_sum.items()}
        detailed_cluster_stats[cluster] = {
            "avg_games": avg_games,
            "avg_elo": avg_elo,
            "avg_opponent_elo": avg_opponent_elo,
            "avg_game_types": avg_game_types,
            "avg_opening_counts": avg_opening_counts,
            "cluster_color": cluster_colors[int(cluster)]
        }
    logger.info("KMeans clustering complete. Silhouette score: %.4f", sil_score)
    
    cluster_profiles = {str(k): v for k, v in cluster_profiles.items()}
    cluster_key = {str(k): v for k, v in cluster_key.items()}
    detailed_cluster_stats = {str(k): v for k, v in detailed_cluster_stats.items()}
    
    available_features = df.columns.tolist()

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
        "detailed_cluster_stats": detailed_cluster_stats,
        "available_features": available_features  # Include available features
    }
