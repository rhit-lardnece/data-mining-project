import pandas as pd
import numpy as np
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import LineString, Point


player_countries = {
    'minya1961': 'Russia',
    'shueardm': 'Australia',
    'pablotorre': 'Argentina',
    'KonstantinKornienko': 'Guinea-Bissau',
    'augustus_hill': 'Israel',
    'DzonYx': 'Serbia',
    'dakaissa_25': 'Germany'
}

opponents_map = {
    'Yudhisthira': ['netsah08'],
    'netsah08': ['Yudhisthira'],
    'Daler': ['kualalumpur'],
    'kualalumpur': ['Daler'],
    'senip': ['Richard_XII'],
    'Richard_XII': ['senip'],
    'van9': ['shueardm'],
    'shueardm': ['minya1961', 'van9'],
    'pablotorre': ['Tortfeasor'],
    'Tortfeasor': ['pablotorre'],
    'augustus_hill': ['Urusov'],
    'Urusov': ['augustus_hill'],
    'adil': ['DzonYx'],
    'DzonYx': ['minya1961', 'adil', 'KonstantinKornienko'],
    'minya1961': ['shueardm', 'DzonYx', 'Tischenko_V'],
    'Tischenko_V': ['minya1961'],
    'KonstantinKornienko': ['dakaissa_25', 'DzonYx'],
    'dakaissa_25': ['KonstantinKornienko']
}

print("Player Countries:")
print(player_countries)

country_coords = pd.read_csv('country-coordinates-world.csv')

def get_coordinates(country_name):
    """Exact case-insensitive match with CSV's Country column"""
    # Clean input and find match
    clean_name = country_name.strip().lower()
    match = country_coords[
        country_coords['Country'].str.strip().str.lower() == clean_name
    ]
    
    if not match.empty:
        return (match['latitude'].iloc[0], match['longitude'].iloc[0])
    print(f"Coordinates not found for: {country_name}")
    return (None, None)

def jitter_coordinates(lat, lon, player, scale=0.3):
    np.random.seed(abs(hash(player)) % (2**32))  # Deterministic seed
    return (
        lat + np.random.uniform(-scale, scale),
        lon + np.random.uniform(-scale, scale)
    )

player_coords = {}
for player, country in player_countries.items():
    if country == 'Unknown':
        continue
    base_lat, base_lon = get_coordinates(country)
    if base_lat and base_lon:
        player_coords[player] = jitter_coordinates(base_lat, base_lon, player)

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