import pandas as pd 
import chess.pgn
import os
import requests
from concurrent.futures import ThreadPoolExecutor
from collections import defaultdict

def parse_pgn(file_path):
    games = []
    try:
        with open(file_path, 'r', encoding='utf-8') as pgn:
            while game := chess.pgn.read_game(pgn):
                games.append({
                    "White": game.headers.get("White", "Unknown"),
                    "Black": game.headers.get("Black", "Unknown"),
                })
    except FileNotFoundError:
        print(f"Error: File not found - {file_path}")
    except Exception as e:
        print(f"Error parsing PGN: {e}")
    return games

def get_player_country(username, session):
    url = f"https://lichess.org/api/user/{username}"
    headers = {"Accept": "application/json"}
    try:
        response = session.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json()
            # Check if the user's profile contains a 'flag' field.
            if "profile" in data and "flag" in data["profile"]:
                return data["profile"]["flag"]  # This returns a country code (e.g., "IN")
    except requests.RequestException as e:
        print(f"Error fetching Lichess profile for {username}: {e}")
 
    return 'Unknown'
    

def fetch_countries_parallel(players):
    player_countries = {}
    with requests.Session() as session:
        with ThreadPoolExecutor(max_workers=10) as executor:
            results = executor.map(lambda user: (user, get_player_country(user, session)), players)
            for user, country in results:
                if country != 'Unknown':
                    player_countries[user] = country
    return player_countries

def build_opponents_map(df, valid_players):
    opponents_map = defaultdict(set)
    for _, row in df.iterrows():
        white, black = row["White"], row["Black"]
        if white in valid_players and black in valid_players:
            opponents_map[white].add(black)
            opponents_map[black].add(white)
    return {player: list(opponents) for player, opponents in opponents_map.items()}

file_path = os.path.join(os.path.dirname(__file__), 'example.pgn')
games = parse_pgn(file_path)
df = pd.DataFrame(games)
unique_players = set(df["White"]).union(set(df["Black"]))
player_countries = fetch_countries_parallel(unique_players)
opponents_map = build_opponents_map(df, unique_players)

print("Player Countries:")
print(player_countries)

print("\nOpponents Map:")
print(opponents_map)
