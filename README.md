# 🏏 IPL Analytics Platform

An end-to-end IPL Analytics web application built using **Python, Pandas, and Flask** that provides insightful analysis of IPL player and team performance through a clean web interface and REST APIs.

---

## 🚀 Features

- 📊 **Player Analytics**
  - Total runs, balls faced, strike rate, and wickets
- 🏏 **Team Analytics**
  - Matches played, wins, and win percentage
- 🔁 **Head-to-Head Analysis**
  - Compare two IPL teams based on historical matches
- ⚔️ **Batsman vs Team**
  - Performance of a batsman against a specific team
- 🎯 **Bowler vs Team**
  - Economy, wickets, balls bowled against a team
- 🌐 **REST APIs**
  - Public APIs for player summaries and top performers
- 🧹 **Data Cleaning & Normalization**
  - Standardized historical IPL team names for consistency

---

## 🛠️ Tech Stack

- **Backend:** Flask (Python)
- **Data Analysis:** Pandas, NumPy
- **Frontend:** HTML, CSS (Jinja2 Templates)
- **APIs:** Flask REST APIs
- **Version Control:** Git & GitHub
- **Deployment Ready:** Gunicorn + Render

---

## 📂 Project Structure

ipl_analytics/
│
├── app.py
├── requirements.txt
├── data/
│ ├── matches.csv
│ ├── deliveries.csv
│ ├── batsman_vs_team.csv
│ ├── bowler_vs_team.csv
│ └── phase_team_summary.csv
│
├── templates/
│ ├── base.html
│ ├── index.html
│ ├── player.html
│ ├── team.html
│ ├── head_to_head.html
│ ├── batsman_vs_team.html
│ └── bowler_vs_team.html
│
├── static/
│ └── style.css
└── README.md
