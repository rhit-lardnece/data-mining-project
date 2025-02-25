import re
import pandas as pd
import logging
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import accuracy_score

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

def predict_logistic(model, scaler, feature_list, input_data):
    logger.info("Making logistic regression prediction...")
    try:
        color = input_data["color"].lower()
        opening_input = input_data["opening"]
        whiteElo = float(input_data["whiteElo"])
        blackElo = float(input_data["blackElo"])
        num_moves = float(input_data.get("num_moves", 40))
        diff = whiteElo - blackElo if color == "white" else blackElo - whiteElo
        feature_row = {col: 0 for col in feature_list}
        feature_row["difference"] = diff
        feature_row["num_moves"] = num_moves
        opening_col = f"opening_{opening_input}"
        if opening_col in feature_row:
            feature_row[opening_col] = 1
        df_input = pd.DataFrame([feature_row])
        X_input = scaler.transform(df_input)
        pred = model.predict(X_input)[0]
        result = "White wins" if pred == 1 else "Black wins"
        
        feature_importance = model.coef_[0]
        feature_contributions = {feature: importance * value for feature, importance, value in zip(feature_list, feature_importance, X_input[0])}
        sorted_contributions = sorted(feature_contributions.items(), key=lambda x: abs(x[1]), reverse=True)
        
        opening_effects = {}
        for opening in feature_list:
            if opening.startswith("opening_"):
                temp_feature_row = feature_row.copy()
                temp_feature_row[opening] = 1
                df_temp_input = pd.DataFrame([temp_feature_row])
                X_temp_input = scaler.transform(df_temp_input)
                temp_pred = model.predict(X_temp_input)[0]
                opening_effects[opening] = "White wins" if temp_pred == 1 else "Black wins"
        
        logger.info("Logistic regression prediction: %s", result)
        return {
            "result": result,
            "feature_contributions": sorted_contributions,
            "opening_effects": opening_effects
        }
    except Exception as e:
        logger.exception("Error in predict_logistic function")
        return None
