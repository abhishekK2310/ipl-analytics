from flask import Flask, request, jsonify
import pandas as pd

app = Flask(__name__)

batsman_vs_team = pd.read_csv("data/batsman_vs_team.csv")
bowler_vs_team = pd.read_csv("data/bowler_vs_team.csv")
h2h_summary = pd.read_csv("data/h2h_summary.csv")
phase_team_summary = pd.read_csv("data/phase_team_summary.csv")
matches_df = pd.read_csv("data/matches.csv")
deliveries_df = pd.read_csv("data/deliveries.csv")
BOWLER_WICKETS = [
    "bowled",
    "caught",
    "lbw",
    "stumped",
    "hit wicket"
]




@app.route("/api/head-to-head")
def head_to_head():
    team1 = request.args.get("team1")
    team2 = request.args.get("team2")

    if not team1 or not team2:
        return jsonify({"error": "team1 and team2 are required"}), 400

    df = matches_df[
        (
            (matches_df["team1"] == team1) &
            (matches_df["team2"] == team2)
        ) |
        (
            (matches_df["team1"] == team2) &
            (matches_df["team2"] == team1)
        )
    ]

    if df.empty:
        return jsonify({"message": "No head-to-head data found"}), 404

    team1_wins = len(df[df["winner"] == team1])
    team2_wins = len(df[df["winner"] == team2])

    return jsonify({
        "team1": team1,
        "team2": team2,
        "matches_played": len(df),
        "team1_wins": team1_wins,
        "team2_wins": team2_wins
    })


@app.route("/api/batsman-vs-team")
def batsman_vs_team_api():
    player = request.args.get("player")
    team = request.args.get("team")

    if not player or not team:
        return jsonify({
            "error": "player and team query parameters are required"
        }), 400

    df = deliveries_df[
        (deliveries_df["batter"] == player) &
        (deliveries_df["bowling_team"] == team)
    ]

    if df.empty:
        return jsonify({"message": "No data found"}), 404

    balls = len(df)
    runs = int(df["batsman_runs"].sum())

    strike_rate = round((runs / balls) * 100, 2) if balls > 0 else 0

    dismissals = len(
        df[
            (df["is_wicket"] == 1) &
            (df["player_dismissed"] == player)
        ]
    )

    return jsonify({
        "batsman": player,
        "against_team": team,
        "balls_faced": balls,
        "runs_scored": runs,
        "strike_rate": strike_rate,
        "dismissals": dismissals
    })


@app.route("/api/bowler-vs-team")
def bowler_vs_team():
    bowler = request.args.get("bowler")
    team = request.args.get("team")

    if not bowler or not team:
        return jsonify({"error": "bowler and team are required"}), 400

    df = deliveries_df[
        (deliveries_df["bowler"] == bowler) &
        (deliveries_df["batting_team"] == team)
    ]

    if df.empty:
        return jsonify({"error": "no data found"}), 404

    balls = len(df)
    runs_conceded = int(df["total_runs"].sum())

    wickets = len(
        df[
            (df["is_wicket"] == 1) &
            (df["dismissal_kind"].isin(BOWLER_WICKETS))
        ]
    )

    overs = balls / 6
    economy = round(runs_conceded / overs, 2) if overs > 0 else 0

    return jsonify({
        "bowler": bowler,
        "batting_team": team,
        "balls": balls,
        "runs_conceded": runs_conceded,
        "wickets": wickets,
        "economy": economy
    })


@app.route("/api/phase")
def phase_analysis():
    team = request.args.get("team")
    data = phase_team_summary[
        phase_team_summary['batting_team'] == team
    ]
    if data.empty:
        return jsonify({"message": "No data found"}), 404

    return jsonify(data.to_dict(orient="records"))

@app.route("/api/player-summary")
def player_summary():
    player = request.args.get("player")

    if not player:
        return jsonify({"error": "player name is required"}), 400

    # Batting data (career)
    batting_df = deliveries_df[deliveries_df["batter"] == player]

    if batting_df.empty:
        return jsonify({"error": "player not found"}), 404

    total_runs = int(batting_df["batsman_runs"].sum())
    total_balls = len(batting_df)
    strike_rate = round((total_runs / total_balls) * 100, 2) if total_balls > 0 else 0

    # Bowling data (career)
    bowling_df = deliveries_df[
        (deliveries_df["bowler"] == player) &
        (deliveries_df["is_wicket"] == 1)
    ]

    total_wickets = int(len(bowling_df))

    return jsonify({
        "player": player,
        "total_runs": total_runs,
        "total_balls": total_balls,
        "strike_rate": strike_rate,
        "total_wickets": total_wickets
    })


@app.route("/api/team-summary")
def team_summary():
    team = request.args.get("team")

    if not team:
        return jsonify({"error": "team name is required"}), 400

    # Matches played (from matches.csv)
    team_matches = matches_df[
        (matches_df["team1"] == team) |
        (matches_df["team2"] == team)
    ]

    matches_played = len(team_matches)

    # Wins (from winner column)
    wins = len(team_matches[team_matches["winner"] == team])

    # Seasons played
    seasons_played = sorted(team_matches["season"].dropna().unique().tolist())

    # Win percentage
    win_percentage = round((wins / matches_played) * 100, 2) if matches_played > 0 else 0

    return jsonify({
        "team": team,
        "matches_played": matches_played,
        "wins": wins,
        "win_percentage": win_percentage,
        "seasons_played": seasons_played
    })







@app.route("/api/top-performers")
def top_performers():
    team = request.args.get("team")

    if not team:
        return jsonify({"error": "team is required"}), 400

    top_batsmen = (
        batsman_vs_team[batsman_vs_team["bowling_team"] == team]
        .groupby("batter")["runs"]
        .sum()
        .sort_values(ascending=False)
        .head(5)
        .reset_index()
    )

    top_bowlers = (
        bowler_vs_team[bowler_vs_team["batting_team"] == team]
        .groupby("bowler")["wickets"]
        .sum()
        .sort_values(ascending=False)
        .head(5)
        .reset_index()
    )

    return jsonify({
        "against_team": team,
        "top_batsmen": top_batsmen.to_dict(orient="records"),
        "top_bowlers": top_bowlers.to_dict(orient="records")
    })


if __name__ == "__main__":
    app.run(debug=True)

