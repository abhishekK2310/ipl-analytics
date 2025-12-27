from flask import Flask, request, jsonify, render_template
import pandas as pd

app = Flask(__name__)

# =====================================================
# LOAD ONLY CLEANED DATA (SOURCE OF TRUTH)
# =====================================================
deliveries_df = pd.read_csv("data/deliveries_clean.csv")
matches_df = pd.read_csv("data/matches_clean.csv")
batsman_vs_team = pd.read_csv("data/batsman_vs_team.csv")
bowler_vs_team = pd.read_csv("data/bowler_vs_team.csv")
phase_team_summary = pd.read_csv("data/phase_team_summary.csv")

# =====================================================
# GLOBAL CONSTANTS
# =====================================================
BOWLER_WICKETS = {
    "bowled", "caught", "lbw", "stumped", "hit wicket"
}

# dropdowns ke liye (ab yahan duplicate / Bengaluru issue nahi aayega)
ALL_PLAYERS = sorted(deliveries_df["batter"].dropna().unique().tolist())
ALL_TEAMS = sorted(matches_df["team1"].dropna().unique().tolist())

# =====================================================
# WEBSITE ROUTES (SERVER-SIDE, NO JS)
# =====================================================

@app.route("/")
def home():
    return render_template(
        "index.html",
        players=ALL_PLAYERS,
        teams=ALL_TEAMS
    )


@app.route("/player")
def player_page():
    name = request.args.get("name")
    if not name:
        return render_template("error.html", message="Player name required")

    df = deliveries_df[deliveries_df["batter"] == name]
    if df.empty:
        return render_template("error.html", message="Player not found")

    runs = int(df["batsman_runs"].sum())
    balls = len(df)
    strike_rate = round((runs / balls) * 100, 2) if balls > 0 else 0

    wickets = len(
        deliveries_df[
            (deliveries_df["bowler"] == name) &
            (deliveries_df["is_wicket"] == 1)
        ]
    )

    return render_template(
        "player.html",
        player=name,
        runs=runs,
        balls=balls,
        strike_rate=strike_rate,
        wickets=wickets
    )


@app.route("/team")
def team_page():
    team = request.args.get("team")
    if not team:
        return render_template("error.html", message="Team name required")

    team_matches = matches_df[
        (matches_df["team1"] == team) |
        (matches_df["team2"] == team)
    ]

    matches_played = len(team_matches)
    wins = len(team_matches[team_matches["winner"] == team])
    win_percentage = round((wins / matches_played) * 100, 2) if matches_played > 0 else 0

    return render_template(
        "team.html",
        team=team,
        matches=matches_played,
        wins=wins,
        win_percentage=win_percentage
    )


@app.route("/head-to-head-view")
def head_to_head_view():
    team1 = request.args.get("team1")
    team2 = request.args.get("team2")

    if not team1 or not team2:
        return render_template("error.html", message="Both teams required")

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

    return render_template(
        "head_to_head.html",
        team1=team1,
        team2=team2,
        matches=len(df),
        team1_wins=len(df[df["winner"] == team1]),
        team2_wins=len(df[df["winner"] == team2])
    )


@app.route("/batsman-vs-team-view")
def batsman_vs_team_view():
    player = request.args.get("player")
    team = request.args.get("team")

    if not player or not team:
        return render_template("error.html", message="Player and Team required")

    df = deliveries_df[
        (deliveries_df["batter"] == player) &
        (deliveries_df["bowling_team"] == team)
    ]

    if df.empty:
        return render_template("error.html", message="No data found")

    runs = int(df["batsman_runs"].sum())
    balls = len(df)
    strike_rate = round((runs / balls) * 100, 2) if balls > 0 else 0

    return render_template(
        "batsman_vs_team.html",
        player=player,
        team=team,
        runs=runs,
        balls=balls,
        strike_rate=strike_rate
    )


@app.route("/bowler-vs-team-view")
def bowler_vs_team_view():
    bowler = request.args.get("bowler")
    team = request.args.get("team")

    if not bowler or not team:
        return render_template("error.html", message="Bowler and Team required")

    df = deliveries_df[
        (deliveries_df["bowler"] == bowler) &
        (deliveries_df["batting_team"] == team)
    ]

    if df.empty:
        return render_template("error.html", message="No data found")

    balls = len(df)
    runs = int(df["total_runs"].sum())

    wickets = len(
        df[
            (df["is_wicket"] == 1) &
            (df["dismissal_kind"].isin(BOWLER_WICKETS))
        ]
    )

    economy = round(runs / (balls / 6), 2) if balls > 0 else 0

    return render_template(
        "bowler_vs_team.html",
        bowler=bowler,
        team=team,
        balls=balls,
        runs=runs,
        wickets=wickets,
        economy=economy
    )

# =====================================================
# API ROUTES (PUBLIC USE)
# =====================================================

@app.route("/api/player-summary")
def api_player_summary():
    player = request.args.get("player")
    if not player:
        return jsonify({"error": "player required"}), 400

    df = deliveries_df[deliveries_df["batter"] == player]
    if df.empty:
        return jsonify({"error": "player not found"}), 404

    return jsonify({
        "player": player,
        "total_runs": int(df["batsman_runs"].sum()),
        "total_balls": len(df),
        "strike_rate": round((df["batsman_runs"].sum() / len(df)) * 100, 2)
    })


@app.route("/api/top-performers")
def api_top_performers():
    team = request.args.get("team")
    if not team:
        return jsonify({"error": "team required"}), 400

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
        "team": team,
        "top_batsmen": top_batsmen.to_dict(orient="records"),
        "top_bowlers": top_bowlers.to_dict(orient="records")
    })


# =====================================================
# RUN APP
# =====================================================
if __name__ == "__main__":
    app.run(debug=True)
