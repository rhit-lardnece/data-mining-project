import os
import chess.pgn
import pandas as pd
import logging

df_games = None
PGN_FILE = os.path.join("chess-stats/datasets", "example3.pgn")

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_variant(time_control):
    """Determine the variant based on the time control."""
    if "+" in time_control:
        base, increment = map(int, time_control.split("+"))
    elif time_control == '-':
        base, increment = 0, 0
    else:
        base, increment = int(time_control), 0

    total_time = base + increment * 40  # Assume 40 moves for increment calculation

    if total_time >= 1800:
        return "Classical"
    elif total_time >= 600:
        return "Rapid"
    elif total_time >= 180:
        return "Blitz"
    else:
        return "Bullet"

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
            time_control = headers.get("TimeControl", "0+0")
            variant = get_variant(time_control)
            event = headers.get("Event", "Unknown")
            event_type = event.split()[1] if len(event.split()) > 1 else "Unknown"
            games_list.append({
                "Event": event,
                "EventType": event_type,
                "Site": headers.get("Site", "Unknown"),
                "White": headers.get("White", "Unknown"),
                "Black": headers.get("Black", "Unknown"),
                "Result": headers.get("Result", ""),
                "UTCDate": headers.get("UTCDate", "Unknown"),
                "UTCTime": headers.get("UTCTime", "Unknown"),
                "WhiteElo": int(headers.get("WhiteElo", 0)) if headers.get("WhiteElo", "0").isdigit() else 0,
                "BlackElo": int(headers.get("BlackElo", 0)) if headers.get("BlackElo", "0").isdigit() else 0,
                "WhiteRatingDiff": int(headers.get("WhiteRatingDiff", 0)) if headers.get("WhiteRatingDiff", "0").isdigit() else 0,
                "BlackRatingDiff": int(headers.get("BlackRatingDiff", 0)) if headers.get("BlackRatingDiff", "0").isdigit() else 0,
                "ECO": headers.get("ECO", "Unknown"),
                "Opening": headers.get("Opening", "Unknown"),
                "TimeControl": time_control,
                "Termination": headers.get("Termination", "Unknown"),
                "Moves": moves,
                "Variant": variant
            })
            game_count += 1
            if game_count % 1000 == 0:
                logging.info(f"Loaded {game_count} games so far...")
    df_games = pd.DataFrame(games_list)
    df_games.dropna(inplace=True)  
    df_games = df_games[(df_games['WhiteElo'] != 0) & (df_games['BlackElo'] != 0)]  
    logging.info(f"Loaded {len(df_games)} games from {pgn_file_path}")
    return df_games
