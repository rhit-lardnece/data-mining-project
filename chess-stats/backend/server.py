import os
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
from flask_caching import Cache

logging.basicConfig(level=logging.DEBUG,
                    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)

app = Flask(__name__)  
CORS(app)

cache = Cache(app, config={'CACHE_TYPE': 'simple'})

from load_data import load_dataset, PGN_FILE
from logistic_regression_alg import train_logistic_model, predict_logistic, prepare_logistic_data
from kmeans_alg import aggregate_player_features, perform_kmeans
from personalized_stats_alg import get_detailed_stats

logger.info("Loading dataset...")
df_games = load_dataset(PGN_FILE) 
logger.info("Dataset loaded successfully.")
logger.debug("df_games sample:\n%s", df_games.head())

logger.info("Precomputing logistic regression model...")
try:
    model, scaler, feature_list, metrics = train_logistic_model(df_games)
    cache.set("logistic_model", (model, scaler, feature_list, metrics), timeout=60*60*24)  
    logger.info("Logistic regression model cached successfully.")
except Exception as e:
    logger.exception("Error precomputing logistic regression model")

logger.info("Precomputing k-means clustering...")
try:
    df_features = aggregate_player_features(df_games)
    common_params = [
        (3, "avg_elo", "avg_opponent_elo"),
        (4, "avg_elo", "avg_opponent_elo"),
        (5, "avg_elo", "avg_opponent_elo")
    ]
    for num_clusters, x_axis, y_axis in common_params:
        kmeans_result = perform_kmeans(df_features, num_clusters, x_axis, y_axis)
        cache_key = f"kmeans_{num_clusters}_{x_axis}_{y_axis}"
        cache.set(cache_key, kmeans_result, timeout=60*60*24)  
    logger.info("K-means clustering cached successfully.")
except Exception as e:
    logger.exception("Error precomputing k-means clustering")

logger.info("Precomputing personalized statistics for example usernames...")
try:
    all_users = pd.concat([df_games["White"], df_games["Black"]])
    example_users = all_users.value_counts().head(5).index.tolist()
    for username in example_users:
        stats = get_detailed_stats(df_games, username)
        cache.set(f"chess_stats_{username}", stats, timeout=60*60*24)  
    cache.set("example_users", example_users, timeout=60*60*24)  
    logger.info("Personalized statistics cached successfully.")
except Exception as e:
    logger.exception("Error precomputing personalized statistics")

logger.info("Precomputing top players...")
try:
    all_users = pd.concat([df_games["White"], df_games["Black"]])
    game_counts = all_users.value_counts()
    threshold = 50  
    selected_players = game_counts[game_counts >= threshold].index.tolist()
    top_players_stats = []
    for player in selected_players:
        stats = get_detailed_stats(df_games, player)
        if "error" not in stats:
            top_players_stats.append(stats)
    cache.set("top_players", {"top_players": top_players_stats}, timeout=60*60*24)  
    logger.info("Top players cached successfully.")
except Exception as e:
    logger.exception("Error precomputing top players")

@app.route("/chess_stats", methods=["GET"])
def chess_stats():
    username = request.args.get("username")
    if not username:
        return jsonify({"error": "Username parameter is required"}), 400
    try:
        cache_key = f"chess_stats_{username}"
        cached_stats = cache.get(cache_key)
        if cached_stats:
            return jsonify(cached_stats)
        else:
            return jsonify({"error": "Statistics not found for the given username."}), 404
    except Exception as e:
        logger.exception("Error in /chess_stats endpoint")
        return jsonify({"error": str(e)}), 500

@app.route("/example_usernames", methods=["GET"])
def example_usernames():
    try:
        example_users = cache.get("example_users")
        if example_users:
            return jsonify({"examples": example_users})
        else:
            return jsonify({"error": "Example usernames not found."}), 404
    except Exception as e:
        logger.exception("Error in /example_usernames endpoint")
        return jsonify({"error": str(e)}), 500

@app.route("/api/kmeans", methods=["POST"])
def kmeans_endpoint():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body must be JSON."}), 415
    num_clusters = int(data.get("num_clusters", 3))
    x_axis = data.get("x_axis", "avg_elo")
    y_axis = data.get("y_axis", "avg_opponent_elo")
    reduction_method = data.get("reduction_method", "pca")
    plot_type = data.get("plot_type", "scatter")
    try:
        cache_key = f"kmeans_{num_clusters}_{x_axis}_{y_axis}_{reduction_method}_{plot_type}"
        cached_result = cache.get(cache_key)
        if cached_result:
            return jsonify(cached_result)
        df_features = aggregate_player_features(df_games)
        kmeans_result = perform_kmeans(df_features, num_clusters, x_axis, y_axis, reduction_method, plot_type)
        cache.set(cache_key, kmeans_result, timeout=60*60*24)  
        return jsonify(kmeans_result)
    except Exception as e:
        logger.exception("Error in /api/kmeans endpoint")
        return jsonify({"error": str(e)}), 500

@app.route("/top_players", methods=["GET"])
def top_players():
    try:
        cached_result = cache.get("top_players")
        if cached_result:
            return jsonify(cached_result)
        else:
            return jsonify({"error": "Top players not found."}), 404
    except Exception as e:
        logger.exception("Error in /top_players endpoint")
        return jsonify({"error": str(e)}), 500

@app.route("/compare_players", methods=["POST"])
def logistic_regression_endpoint():
    data = request.get_json()
    required = ["player1", "player2"]
    if not data or not all(field in data for field in required):
        return jsonify({"error": f"Missing required fields: {required}"}), 400
    try:
        player1 = data["player1"]
        player2 = data["player2"]

        model, scaler, feature_list, metrics = cache.get("logistic_model")
        if not model or not scaler or not feature_list:
            return jsonify({"error": "Logistic model not found in cache."}), 500

        prediction_details = predict_logistic(model, scaler, feature_list, df_games, player1, player2)
        if "error" in prediction_details:
            return jsonify({"error": prediction_details["error"]}), 404

        comparison_result = {
            "color_specific": prediction_details.get("color_specific"),
            "color_agnostic": prediction_details.get("color_agnostic"),
            "top_opening_predictions": prediction_details.get("top_opening_predictions"),
            "player1": prediction_details.get("player1_stats"),
            "player2": prediction_details.get("player2_stats"),
            "comparison_basis": "Logistic regression prediction",
            "model_accuracy": metrics["test_accuracy"],
            "cross_validation_score": metrics["cv_accuracy"],
            "full_feature_importances": metrics["feature_importance"]
        }

        return jsonify(comparison_result)
    except Exception as e:
        logger.exception("Error in /compare_players endpoint")
        return jsonify({"error": "An unexpected error occurred. Please try again later."}), 500

if __name__ == "__main__":
    logger.info("Starting development server with detailed logs on port 5000...")
    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)
