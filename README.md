# GitHub Dev Dashboard

This project generates dynamic HTML dashboards showcasing GitHub repositories related to [The Graph](https://thegraph.com/) ecosystem.
It includes separate dashboards for **Subgraphs** and **Substreams**, featuring stats like stars, owners, and last update times.

**Live Dashboard:**  
🔗 [graphtools.pro/github](https://graphtools.pro/github)

🧪 This dashboard is part of [**Graph Tools Pro**](https://graphtools.pro), a community-driven initiative to provide useful, independent analytics tools for The Graph ecosystem.

## 🔧 Features

- Daily-generated dashboards using local `.csv` and `.json` files
- Visualized with Bootstrap and DataTables
- Dark/light theme toggle with persistent design
- SEO and social sharing metadata (Open Graph & Twitter cards)
- Clean archiving of previous dashboard versions

## 📁 File Structure
📦 reports/
- 📜 index.html              # Subgraphs dashboard
- 📜 index2.html             # Substreams dashboard
- 📜 subgraph_metadata.json
- 📜 substreams_metadata.json
- 📜 subgraph_repositories_filtered.csv
- 📜 substreams_repositories_filtered.csv

📦 archive/
- 📜 index_05082025.html     # Archived previous dashboard

- 📜 generate_dashboards_dynamic.py
- 📜 .gitignore
- 📜 README.md

## 🚀 How to Use

1. Place the updated CSV and metadata files in the `reports/` folder.
2. Run the script:

`python3 generate_dashboards_dynamic.py`

3. Find the generated dashboards in the `reports/` folder. Older dashboards are archived in `archive/`

## 🛡️ GitHub Integration
- Avatar fetching from GitHub CDN
- Dynamic filtering & search for repositories
- Automatic .env exclusion via .gitignore

## 📊 Powered By
- 🧩 Python 3.x, HTML5 + CSS 
- ⚙️ GitHub API, jQuery & DataTables.js
