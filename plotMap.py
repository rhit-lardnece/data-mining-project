import pandas as pd 
import chess.pgn
import os
import requests
from concurrent.futures import ThreadPoolExecutor
from collections import defaultdict
import numpy as np
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import LineString, Point

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


# Load the CSV that contains country codes and coordinates.
country_coords = pd.read_csv('countries_codes_and_coordinates.csv')

# Clean the 'Alpha-2 code' column to remove extra quotes and standardize to uppercase.
country_coords['Alpha-2 code'] = country_coords['Alpha-2 code'].astype(str).str.replace('"', '').str.strip().str.upper()

# For debugging: print unique alpha-2 codes
print("Unique Alpha-2 codes in CSV:", country_coords['Alpha-2 code'].unique())

def get_coordinates(alpha_2_code):
    """Retrieve coordinates based on ISO alpha-2 country code from the CSV."""
    match = country_coords[country_coords['Alpha-2 code'] == alpha_2_code.upper()]
    if not match.empty:
        lat_str = match['Latitude (average)'].iloc[0]
        lon_str = match['Longitude (average)'].iloc[0]
        try:
            lat = float(lat_str.replace('"', '').strip())
            lon = float(lon_str.replace('"', '').strip())
        except ValueError as e:
            print(f"Error converting coordinates for {alpha_2_code}: {e}")
            return (None, None)
        return (lat, lon)
    print(f"Coordinates not found for: {alpha_2_code}")
    return (None, None)

def jitter_coordinates(lat, lon, player, scale=2.3):
    """Applies small random jitter to coordinates for visualization clarity."""
    np.random.seed(abs(hash(player)) % (2**32))  # Deterministic seed based on player name
    return (
        lat + np.random.uniform(-scale, scale),
        lon + np.random.uniform(-scale, scale)
    )

player_coords = {}
# Iterate over player_countries (which hold ISO codes) and retrieve coordinates
for player, country_code in player_countries.items():
    if country_code == 'Unknown':
        continue
    base_lat, base_lon = get_coordinates(country_code)
    if base_lat is not None and base_lon is not None:
        player_coords[player] = jitter_coordinates(base_lat, base_lon, player)

# Create connections between players and their opponents
connections = []
for player, opponents in opponents_map.items():
    if player not in player_coords:
        continue
    player_lon, player_lat = player_coords[player][1], player_coords[player][0]
    for opponent in opponents:
        if opponent in player_coords:
            opponent_lon, opponent_lat = player_coords[opponent][1], player_coords[opponent][0]
            connections.append(LineString([
                (player_lon, player_lat),
                (opponent_lon, opponent_lat)
            ]))

print("Player Coordinates:", player_coords)
print("Connections:", connections)



world = gpd.read_file("ne_110m_admin_0_countries.zip")

# Create plot
fig, ax = plt.subplots(figsize=(18, 12))

# Base world map
world.plot(ax=ax, color='#f0f0f0', edgecolor='#404040')

# Plot connections
gpd.GeoSeries(connections).plot(
    ax=ax,
    color='#ff4444',
    linewidth=0.4,
    alpha=0.3
)

# Plot player locations
player_points = [Point(lon, lat) for lat, lon in player_coords.values()]
gpd.GeoSeries(player_points).plot(
    ax=ax,
    color='#0066cc',
    markersize=8,
    edgecolor='black',
    linewidth=0.3
)

# Customize
plt.title("Chess Player Connections\n(Country Jitter Applied)", fontsize=16)
plt.box(False)
plt.axis('off')

plt.savefig('chess_connections.png', dpi=300, bbox_inches='tight')
plt.show()
