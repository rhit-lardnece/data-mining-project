import pandas as pd
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import StandardScaler
import chess.pgn
from typing import List, Tuple, Dict

def parse_pgn(file_path: str) -> List[chess.pgn.Game]:
    games = []
    with open(file_path) as pgn:
        while True:
            game = chess.pgn.read_game(pgn)
            if game is None:
                break
            games.append(game)
    return games

def extract_features(games: List[chess.pgn.Game]) -> Tuple[List[Dict], List[int]]:
    features = []
    labels = []
    for game in games:
        result = game.headers["Result"]
        if result == "1-0":
            labels.append(1)
        elif result == "0-1":
            labels.append(0)
        else:
            continue
        
        white_elo = int(game.headers["WhiteElo"]) if game.headers["WhiteElo"].isdigit() else 0
        black_elo = int(game.headers["BlackElo"]) if game.headers["BlackElo"].isdigit() else 0
        opening = game.headers["Opening"]
        
        features.append({
            "white_elo": white_elo,
            "black_elo": black_elo,
            "opening": opening,
        })
    return features, labels

def encode_features(features: List[Dict]) -> pd.DataFrame:
    df = pd.DataFrame(features)
    df = pd.get_dummies(df, columns=["opening"], drop_first=True)
    return df

games = parse_pgn("datasets/example2.pgn")
features, labels = extract_features(games)
df = encode_features(features)

scaler = StandardScaler()
X = scaler.fit_transform(df)
y = labels

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = LogisticRegression(max_iter=1000)
model.fit(X_train, y_train)

cv_scores = cross_val_score(model, X, y, cv=5)
print(f"Cross-Validation Accuracy: {cv_scores.mean() * 100:.2f}%")

y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f"Test Accuracy: {accuracy * 100:.2f}%")

importance = model.coef_[0]
feature_importance = pd.Series(importance, index=df.columns).sort_values(ascending=False)
print("Feature Importance:")
print(feature_importance)

feature_importance.to_csv("feature_importance.csv", header=["importance"])
df.to_csv("features.csv", index=False)
