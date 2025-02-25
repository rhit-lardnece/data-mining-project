import os
import chess.pgn
import pandas as pd
import logging

df_games = None
PGN_FILE = os.path.join("chess-stats/datasets", "example3.pgn")

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_dataset(pgn_file_path=PGN_FILE):
    """Loads all games from the PGN file into a global DataFrame."""
    global df_games
    games_list = []
    if not os.path.exists(pgn_file_path):
        raise FileNotFoundError(f"PGN file not found at: {pgn_file_path}")
    with open(pgn_file_path, "r", encoding="utf-8") as pgn_file:
        game_count = 0
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
                "WhiteElo": int(headers.get("WhiteElo", 0)) if headers.get("WhiteElo", "0").isdigit() else 0,
                "BlackElo": int(headers.get("BlackElo", 0)) if headers.get("BlackElo", "0").isdigit() else 0,
                "Opening": headers.get("Opening", "Unknown"),
                "Moves": moves
            })
            game_count += 1
            if game_count % 1000 == 0:
                logging.info(f"Loaded {game_count} games so far...")
    df_games = pd.DataFrame(games_list)
    logging.info(f"Loaded {len(df_games)} games from {pgn_file_path}")
    return df_games
