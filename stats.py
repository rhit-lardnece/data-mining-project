
import chess.pgn
import collections

def find_most_active_player(pgn_file_path):
    player_counts = collections.Counter()

    with open(pgn_file_path, "r", encoding="utf-8") as pgn_file:
        while True:
            game = chess.pgn.read_game(pgn_file)
            if game is None:
                break 

            white_player = game.headers.get("White", "Unknown")
            black_player = game.headers.get("Black", "Unknown")

            player_counts[white_player] += 1
            player_counts[black_player] += 1

    most_active_player, most_games = player_counts.most_common(1)[0]

    return most_active_player, most_games, player_counts

if __name__ == "__main__":
    pgn_file = "example.pgn"  
    most_active, games_played, all_players = find_most_active_player(pgn_file)

    print(f"🎉 The most active player is **{most_active}** with **{games_played}** games played!")

    print("\n🏆 Top 5 Players with Most Games:")
    for player, games in all_players.most_common(5):
        print(f"{player}: {games} games")
