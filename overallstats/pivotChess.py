import pandas as pd
from typing import List, Dict
import re

import chess.pgn

def parse_pgn(file_path: str) -> List[chess.pgn.Game]:
    games = []
    with open(file_path) as pgn:
        while True:
            game = chess.pgn.read_game(pgn)
            if game is None:
                break
            games.append(game)
    return games

def extract_features(games: List[chess.pgn.Game]) -> pd.DataFrame:
    data = []
    for game in games:
        result = game.headers["Result"]
        if result not in ["1-0", "0-1"]:
            continue
        
        white_elo = int(game.headers["WhiteElo"]) if game.headers["WhiteElo"].isdigit() else 0
        black_elo = int(game.headers["BlackElo"]) if game.headers["BlackElo"].isdigit() else 0
        opening = re.split(r'[:#,]', game.headers["Opening"])[0].strip()
        
        data.append({
            "white_elo": white_elo,
            "black_elo": black_elo,
            "opening": opening,
            "result": result
        })
    return pd.DataFrame(data)

def calculate_winrates(df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    df['greater_elo_win'] = df.apply(lambda row: 1 if (row['white_elo'] > row['black_elo'] and row['result'] == '1-0') or (row['black_elo'] > row['white_elo'] and row['result'] == '0-1') else 0, axis=1)
    df['lesser_elo_win'] = df.apply(lambda row: 1 if (row['white_elo'] < row['black_elo'] and row['result'] == '1-0') or (row['black_elo'] < row['white_elo'] and row['result'] == '0-1') else 0, axis=1)
    df['white_win'] = df['result'].apply(lambda x: 1 if x == '1-0' else 0)
    df['black_win'] = df['result'].apply(lambda x: 1 if x == '0-1' else 0)

    white_black_winrate = df['result'].value_counts(normalize=True).to_frame().T
    white_black_winrate['white_win_total'] = df['white_win'].sum()
    white_black_winrate['black_win_total'] = df['black_win'].sum()

    greater_lesser_elo_winrate = df[['greater_elo_win', 'lesser_elo_win']].mean()
    greater_lesser_elo_counts = df[['greater_elo_win', 'lesser_elo_win']].sum()

    opening_winrate = df.groupby('opening').agg({
        'white_win': ['mean', 'sum'],
        'black_win': ['mean', 'sum'],
        'result': 'count'
    }).sort_values(by=('white_win', 'mean'), ascending=False)

    greater_lesser_elo_combined = pd.DataFrame({
        'winrate': greater_lesser_elo_winrate,
        'total_wins': greater_lesser_elo_counts
    })

    return {
        "white_black_winrate": white_black_winrate,
        "greater_lesser_elo": greater_lesser_elo_combined,
        "opening_winrate": opening_winrate
    }

games = parse_pgn("datasets/example2.pgn")
df = extract_features(games)
winrates = calculate_winrates(df)

winrates['white_black_winrate'].to_csv("overallstats/results/white_black_winrate.csv")
winrates['greater_lesser_elo'].to_csv("overallstats/results/greater_lesser_elo.csv")
winrates['opening_winrate'].to_csv("overallstats/results/opening_winrate.csv")
