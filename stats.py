import chess.pgn
import collections

def find_most_active_player(pgn_file_path):
    player_counts = collections.Counter()
    game_count = 0
    checkpoint = 5000 

    with open(pgn_file_path, "r", encoding="utf-8") as pgn_file:
        while True:
            game = chess.pgn.read_game(pgn_file)
            if game is None:
                break  

            white_player = game.headers.get("White", "Unknown")
            black_player = game.headers.get("Black", "Unknown")

            player_counts[white_player] += 1
            player_counts[black_player] += 1

            game_count += 1

            if game_count % checkpoint == 0:
                print(f"Processed {game_count} games...")

    most_active_player, most_games = player_counts.most_common(1)[0]

    return most_active_player, most_games, player_counts

if __name__ == "__main__":
    # pgn_file = "C:\\Users\\jadejaan\\Downloads\\lichess_db_standard_rated_2013-11.pgn"
    pgn_file = "datasets/example2.pgn"

    print(" Processing PGN file... This may take some time for large files.")
    most_active, games_played, all_players = find_most_active_player(pgn_file)

    print(f"\nThe most active player is **{most_active}** with **{games_played}** games played!")

    print("\n Top 5 Players with Most Games:")
    for player, games in all_players.most_common(5):
        print(f"{player}: {games} games")

    print("\n Processing complete!")
