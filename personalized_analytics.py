from flask import Flask, request, jsonify
from flask_cors import CORS
import chess.pgn
import pandas as pd
import collections
import os
import re
import numpy as np  

app = Flask(__name__)
CORS(app)

pgn_file = "datasets/example2.pgn"
df_games = None

def safe_int(value, default=0):
    """Convert value to int, handling errors gracefully."""
    try:
        return int(value)
    except ValueError:
        return default

def load_pgn_to_dataframe(pgn_file_path):
    global df_games
    games_list = []
    game_count = 0
    checkpoint = 50000 

    if not os.path.exists(pgn_file_path):
        print(f"PGN file not found at: {pgn_file_path}")
        return pd.DataFrame()

    with open(pgn_file_path, "r", encoding="utf-8") as pgn_file:
        while True:
            game = chess.pgn.read_game(pgn_file)
            if game is None:
                break

            headers = game.headers
            moves = len(list(game.mainline_moves())) 

            games_list.append({
                "White": headers.get("White", "Unknown"),
                "Black": headers.get("Black", "Unknown"),
                "Result": headers.get("Result", ""),
                "WhiteElo": safe_int(headers.get("WhiteElo", 0)),
                "BlackElo": safe_int(headers.get("BlackElo", 0)),  
                "Opening": headers.get("Opening", "Unknown"),
                "Moves": moves
            })
            game_count += 1

            if game_count % checkpoint == 0:
                print(f"Processed {game_count} games...")

    df_games = pd.DataFrame(games_list)
    print(f"Processing finished! Loaded {len(df_games)} games into DataFrame.")

def get_user_stats(username):
    """Retrieve statistics for a specific player from the DataFrame."""
    global df_games

    if df_games is None or df_games.empty:
        return {"error": "No data loaded. Check the PGN file."}

    user_games = df_games[(df_games["White"] == username) | (df_games["Black"] == username)].copy()
    user_games.loc[:, "Opponent"] = user_games.apply(lambda row: row["Black"] if row["White"] == username else row["White"], axis=1)

    if user_games.empty:
        return {"error": f"No games found for user: {username}"}

    wins = ((user_games["White"] == username) & (user_games["Result"] == "1-0")).sum() + \
           ((user_games["Black"] == username) & (user_games["Result"] == "0-1")).sum()
    losses = ((user_games["White"] == username) & (user_games["Result"] == "0-1")).sum() + \
             ((user_games["Black"] == username) & (user_games["Result"] == "1-0")).sum()
    draws = (user_games["Result"] == "1/2-1/2").sum()

    total_games = len(user_games)
    avg_rating = user_games[["WhiteElo", "BlackElo"]].mean().mean()

    user_games["MainOpening"] = user_games["Opening"].apply(lambda x: re.split(r'[:#,]', x)[0].strip())

    openings_count = user_games["MainOpening"].value_counts().reset_index()
    openings_count.columns = ["name", "count"] 
    openings_data = openings_count.to_dict(orient="records")

    opening_winrates = user_games.groupby("MainOpening").apply(
        lambda x: ((x["White"] == username) & (x["Result"] == "1-0")).sum() + 
                  ((x["Black"] == username) & (x["Result"] == "0-1")).sum() / len(x) * 100
    ).reset_index()
    opening_winrates.columns = ["name", "winrate"]
    
    # Convert to native Python types for JSON serialization
    opening_winrates["winrate"] = opening_winrates["winrate"].astype(float)  
    opening_winrates_data = opening_winrates.to_dict(orient="records")

    most_common_opponent = user_games["Opponent"].value_counts().idxmax() if not user_games["Opponent"].empty else "None"

    user_games["OpponentElo"] = user_games.apply(lambda row: row["BlackElo"] if row["White"] == username else row["WhiteElo"], axis=1)
    user_games["UserElo"] = user_games.apply(lambda row: row["WhiteElo"] if row["White"] == username else row["BlackElo"], axis=1)

    higher_elo_games = user_games[user_games["OpponentElo"] > user_games["UserElo"]]
    lower_elo_games = user_games[user_games["OpponentElo"] < user_games["UserElo"]]

    higher_elo_wins = ((higher_elo_games["White"] == username) & (higher_elo_games["Result"] == "1-0")).sum() + \
                      ((higher_elo_games["Black"] == username) & (higher_elo_games["Result"] == "0-1")).sum()
    higher_elo_losses = ((higher_elo_games["White"] == username) & (higher_elo_games["Result"] == "0-1")).sum() + \
                        ((higher_elo_games["Black"] == username) & (higher_elo_games["Result"] == "1-0")).sum()

    lower_elo_wins = ((lower_elo_games["White"] == username) & (lower_elo_games["Result"] == "1-0")).sum() + \
                     ((lower_elo_games["Black"] == username) & (lower_elo_games["Result"] == "0-1")).sum()
    lower_elo_losses = ((lower_elo_games["White"] == username) & (lower_elo_games["Result"] == "0-1")).sum() + \
                       ((lower_elo_games["Black"] == username) & (lower_elo_games["Result"] == "1-0")).sum()

    return {
        "username": username,
        "total_games": int(total_games),
        "wins": int(wins),
        "losses": int(losses),
        "average_opponent_rating": int(round(avg_rating)),
        "most_common_openings": openings_data,
        "opening_winrates": opening_winrates_data,
        "most_common_opponent": most_common_opponent,
        "game_lengths": [int(moves) for moves in user_games["Moves"].tolist()],
        "higher_elo_wins": int(higher_elo_wins),
        "higher_elo_losses": int(higher_elo_losses),
        "lower_elo_wins": int(lower_elo_wins),
        "lower_elo_losses": int(lower_elo_losses)
    }

@app.route('/chess_stats', methods=['GET'])
def chess_stats():
    username = request.args.get("username")
    if not username:
        return jsonify({"error": "Username parameter is required"}), 400

    stats = get_user_stats(username)
    return jsonify(stats)

if __name__ == '__main__':
    load_pgn_to_dataframe(pgn_file)
    app.run(debug=True, host="0.0.0.0", port=5000)
