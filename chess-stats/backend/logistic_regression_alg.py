import re
import pandas as pd
import logging
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import accuracy_score
from personalized_stats_alg import get_detailed_stats

logger = logging.getLogger(__name__)

def prepare_logistic_data(df):
    logger.info("Preparing logistic regression data...")
    valid_games = df[df["Result"].isin(["1-0", "0-1"])].copy()
    features = []
    labels = []
    for idx, row in valid_games.iterrows():
        whiteElo = row["WhiteElo"]
        blackElo = row["BlackElo"]
        diff = whiteElo - blackElo
        opening = re.split(r'[:#,]', row["Opening"])[0].strip()
        num_moves = row["Moves"]
        features.append({"difference": diff, "opening": opening, "num_moves": num_moves})
        labels.append(1 if row["Result"] == "1-0" else 0)
        if idx % 1000 == 0:
            logger.debug(f"Processed game index: {idx}")
    df_features = pd.DataFrame(features)
    df_encoded = pd.get_dummies(df_features, columns=["opening"], drop_first=True)
    logger.info("Logistic regression data prepared with shape: %s", df_encoded.shape)
    return df_encoded, labels

def train_logistic_model(df):
    logger.info("Training logistic regression model...")
    df_encoded, labels = prepare_logistic_data(df)
    scaler = StandardScaler()
    X = scaler.fit_transform(df_encoded)
    X_train, X_test, y_train, y_test = train_test_split(X, labels, test_size=0.2, random_state=42)
    model = LogisticRegression(max_iter=1000)
    model.fit(X_train, y_train)
    train_acc = accuracy_score(y_train, model.predict(X_train))
    test_acc = accuracy_score(y_test, model.predict(X_test))
    cv_scores = cross_val_score(model, X, labels, cv=5)
    feature_importance = model.coef_[0]
    feature_list = df_encoded.columns.tolist()
    metrics = {
        "train_accuracy": train_acc,
        "test_accuracy": test_acc,
        "cv_accuracy": cv_scores.mean(),
        "feature_importance": dict(zip(feature_list, feature_importance)),
        "num_features": len(feature_list),
        "num_training_samples": len(X_train),
        "num_testing_samples": len(X_test)
    }
    logger.info("Model trained. Test accuracy: %.4f", test_acc)
    return model, scaler, feature_list, metrics

def predict_logistic(model, scaler, feature_list, df_games, player1, player2):
    logger.info("Fetching player data and making logistic regression prediction...")
    try:
        player1Stats = get_detailed_stats(df_games, player1)
        player2Stats = get_detailed_stats(df_games, player2)
        if "error" in player1Stats or "error" in player2Stats:
            return {"error": "Error fetching player statistics."}

        def create_feature_row(p_stats, o_stats):
            diff = p_stats["average_rating"] - o_stats["average_rating"]
            row = {col: 0 for col in feature_list}
            row["difference"] = diff
            row["num_moves"] = p_stats["total_games"]

            for op in p_stats.get("most_common_openings", []):
                col = f"opening_{op['name']}"
                if col in row: row[col] = 1
            return row

        base_row1 = create_feature_row(player1Stats, player2Stats)
        base_row2 = create_feature_row(player2Stats, player1Stats)
        df_input1 = pd.DataFrame([base_row1])
        df_input2 = pd.DataFrame([base_row2])
        X_input1 = scaler.transform(df_input1)
        X_input2 = scaler.transform(df_input2)
        pred1 = model.predict(X_input1)[0]
        pred2 = model.predict(X_input2)[0]
        result1 = "Player 1 wins" if pred1 == 1 else "Player 2 wins"
        result2 = "Player 2 wins" if pred2 == 1 else "Player 1 wins"
        overall_winner = "Player 1" if pred1 == 1 else "Player 2"

        feat_imp = model.coef_[0]
        fc1 = {f: imp * val for f, imp, val in zip(feature_list, feat_imp, X_input1[0])}
        fc2 = {f: imp * val for f, imp, val in zip(feature_list, feat_imp, X_input2[0])}
        sorted_fc1 = sorted(fc1.items(), key=lambda x: abs(x[1]), reverse=True)
        sorted_fc2 = sorted(fc2.items(), key=lambda x: abs(x[1]), reverse=True)
        short_fc1 = sorted_fc1[:5]
        short_fc2 = sorted_fc2[:5]

        overall_agnostic = "Player 1 wins" if player1Stats["average_rating"] > player2Stats["average_rating"] else "Player 2 wins"

        def opening_predictions(p_stats, base_row):
            predictions = []
            top_openings = p_stats.get("most_common_openings", [])[:5]
            for op in top_openings:
                wins = op.get("wins", 0)
                losses = op.get("losses", 0)
                predictions.append({"opening": op["name"], "wins": wins, "losses": losses})
            return predictions

        op_preds1 = opening_predictions(player1Stats, base_row1)
        op_preds2 = opening_predictions(player2Stats, base_row2)

        logger.info("Logistic regression prediction: %s", overall_winner)
        return {
            "result1": result1,
            "result2": result2,
            "overall_winner": overall_winner,

            "color_agnostic": {
                "prediction": overall_agnostic,
                "player1_average_rating": player1Stats["average_rating"],
                "player2_average_rating": player2Stats["average_rating"]
            },
            "top_opening_predictions": {
                "player1": op_preds1,
                "player2": op_preds2
            },
            "player1_stats": player1Stats,
            "player2_stats": player2Stats
        }
    except Exception as e:
        logger.exception("Error in predict_logistic function")
        return {"error": str(e)}
