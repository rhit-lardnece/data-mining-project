from flask import Flask, request, jsonify
from flask_cors import CORS
import chess.pgn
import pandas as pd
import collections
import os

app = Flask(__name__)
CORS(app)

pgn_file = "C:\\Users\\jadejaan\\Downloads\\lichess_db_standard_rated_2013-11.pgn"
# pgn_file = "example.pgn"

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
    print("Getting user stats")
    user_games = df_games[(df_games["White"] == username) | (df_games["Black"] == username)]
    user_games = user_games.copy() 
    user_games.loc[:, "Opponent"] = user_games.apply(lambda row: row["Black"] if row["White"] == username else row["White"], axis=1)

    if user_games.empty:
        return {"error": f"No games found for user: {username}"}

    wins = ((user_games["White"] == username) & (user_games["Result"] == "1-0")).sum() + \
           ((user_games["Black"] == username) & (user_games["Result"] == "0-1")).sum()
    losses = ((user_games["White"] == username) & (user_games["Result"] == "0-1")).sum() + \
             ((user_games["Black"] == username) & (user_games["Result"] == "1-0")).sum()
    draws = (user_games["Result"] == "1/2-1/2").sum()

    total_games = len(user_games)
    win_percentage = (wins / total_games) * 100 if total_games > 0 else 0

    avg_rating = user_games[["WhiteElo", "BlackElo"]].mean().mean()


    openings_count = user_games["Opening"].value_counts().reset_index()
    openings_count.columns = ["name", "count"] 
    openings_data = openings_count.to_dict(orient="records")

    user_games["Opponent"] = user_games.apply(lambda row: row["Black"] if row["White"] == username else row["White"], axis=1)
    most_common_opponent = user_games["Opponent"].value_counts().idxmax() if not user_games["Opponent"].empty else "None"

    return {
        "username": username,
        "total_games": total_games,
        "win_percentage": round(win_percentage, 2),
        "average_opponent_rating": round(avg_rating),
        "most_common_openings": openings_data,
        "most_common_opponent": most_common_opponent,
        "game_lengths": user_games["Moves"].tolist()
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
