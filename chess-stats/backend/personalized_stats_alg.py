import re
import logging
import pandas as pd

logger = logging.getLogger(__name__)

def get_detailed_stats(df, username):
    logger.info("Computing detailed stats for user: %s", username)
    user_games = df[(df["White"] == username) | (df["Black"] == username)].copy()
    if user_games.empty:
        logger.warning("No games found for user: %s", username)
        return {"error": f"No games found for user: {username}"}
    
    wins = (
        ((user_games["White"] == username) & (user_games["Result"] == "1-0")).sum() +
        ((user_games["Black"] == username) & (user_games["Result"] == "0-1")).sum()
    )
    losses = (
        ((user_games["White"] == username) & (user_games["Result"] == "0-1")).sum() +
        ((user_games["Black"] == username) & (user_games["Result"] == "1-0")).sum()
    )
    draws = (user_games["Result"] == "1/2-1/2").sum()
    total_games = len(user_games)
    avg_rating = user_games[["WhiteElo", "BlackElo"]].mean().mean()
    
    user_games["MainOpening"] = user_games["Opening"].apply(lambda x: re.split(r'[:#,]', x)[0].strip())
    openings_distribution = user_games["MainOpening"].value_counts().to_dict()
    
    most_common_openings = sorted(
        [{"name": k, "count": v} for k, v in openings_distribution.items()],
        key=lambda x: x["count"],
        reverse=True
    )
    
    opening_wins = {}
    opening_total = {}
    for _, row in user_games.iterrows():
        op = row["MainOpening"]
        opening_total[op] = opening_total.get(op, 0) + 1
        if (row["White"] == username and row["Result"] == "1-0") or \
           (row["Black"] == username and row["Result"] == "0-1"):
            opening_wins[op] = opening_wins.get(op, 0) + 1
    opening_winrates = []
    for op, total in opening_total.items():
        wins_op = opening_wins.get(op, 0)
        winrate = (wins_op / total) * 100
        opening_winrates.append({"name": op, "winrate": winrate})
    
    game_lengths = user_games["Moves"].tolist()
    
    user_games["UserElo"] = user_games.apply(lambda row: row["WhiteElo"] if row["White"] == username else row["BlackElo"], axis=1)
    user_games["OpponentElo"] = user_games.apply(lambda row: row["BlackElo"] if row["White"] == username else row["WhiteElo"], axis=1)
    opponent_ratings = user_games["OpponentElo"]
    average_opponent_rating = opponent_ratings.mean()
    opponents = user_games.apply(lambda row: row["Black"] if row["White"] == username else row["White"], axis=1)
    most_common_opponent = opponents.value_counts().idxmax() if not opponents.empty else None
    
    higher_games = user_games[user_games["OpponentElo"] > user_games["UserElo"]]
    lower_games = user_games[user_games["OpponentElo"] < user_games["UserElo"]]
    higher_wins = (
        ((higher_games["White"] == username) & (higher_games["Result"] == "1-0")).sum() +
        ((higher_games["Black"] == username) & (higher_games["Result"] == "0-1")).sum()
    )
    lower_wins = (
        ((lower_games["White"] == username) & (lower_games["Result"] == "1-0")).sum() +
        ((lower_games["Black"] == username) & (lower_games["Result"] == "0-1")).sum()
    )
    higher_games_count = len(higher_games)
    lower_games_count = len(lower_games)
    higher_elo_losses = higher_games_count - higher_wins
    lower_elo_losses = lower_games_count - lower_wins

    stats = {
        "username": username,
        "total_games": total_games,
        "wins": int(wins),
        "losses": int(losses),
        "draws": int(draws),
        "average_rating": int(round(avg_rating)),
        "openings_distribution": openings_distribution,
        "most_common_openings": most_common_openings,
        "opening_winrates": opening_winrates,
        "game_lengths": game_lengths,
        "average_opponent_rating": average_opponent_rating,
        "most_common_opponent": most_common_opponent,
        "higher_elo_wins": int(higher_wins),
        "higher_elo_losses": int(higher_elo_losses),
        "lower_elo_wins": int(lower_wins),
        "lower_elo_losses": int(lower_elo_losses)
    }
    logger.info("Detailed stats computed for user: %s", username)
    return stats
