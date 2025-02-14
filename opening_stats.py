import chess.pgn
import pandas as pd
from collections import defaultdict

def parse_pgn(file_path, max_games=1000000):
    opening_stats = defaultdict(lambda: {'wins': 0, 'losses': 0, 'draws': 0, 'total': 0})
    game_lengths = []
    
    with open(file_path) as pgn:
        for _ in range(max_games):
            game = chess.pgn.read_game(pgn)
            if game is None:
                break
            
            opening = game.headers.get("ECO", "Unknown")
            result = game.headers.get("Result")
            opening_stats[opening]['total'] += 1
            
            if result == "1-0":
                opening_stats[opening]['wins'] += 1
            elif result == "0-1":
                opening_stats[opening]['losses'] += 1
            elif result == "1/2-1/2":
                opening_stats[opening]['draws'] += 1
            
            moves = len(list(game.mainline_moves()))
            game_lengths.append((moves, game))
    
    return opening_stats, game_lengths

def analyze_openings(opening_stats):
    data = []
    for opening, stats in opening_stats.items():
        win_rate = stats['wins'] / stats['total'] * 100 if stats['total'] > 0 else 0
        loss_rate = stats['losses'] / stats['total'] * 100 if stats['total'] > 0 else 0
        draw_rate = stats['draws'] / stats['total'] * 100 if stats['total'] > 0 else 0
        
        data.append([opening, stats['total'], win_rate, loss_rate, draw_rate])
    
    df = pd.DataFrame(data, columns=["Opening", "Games Played", "Win %", "Loss %", "Draw %"])
    return df.sort_values(by="Games Played", ascending=False)

def analyze_game_lengths(game_lengths):
    if not game_lengths:
        return None, None
    
    shortest_game = min(game_lengths, key=lambda x: x[0])
    longest_game = max(game_lengths, key=lambda x: x[0])
    
    return shortest_game, longest_game

pgn_file = "example.pgn"  
opening_stats, game_lengths = parse_pgn(pgn_file)
df = analyze_openings(opening_stats)
shortest_game, longest_game = analyze_game_lengths(game_lengths)

print("Opening Performance Analysis", df)

if shortest_game:
    print(f"Shortest game: {shortest_game[0]} moves")
if longest_game:
    print(f"Longest game: {longest_game[0]} moves")
