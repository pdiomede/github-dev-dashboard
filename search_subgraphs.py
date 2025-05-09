import os
import time
import requests
import pandas as pd
from collections import Counter
from datetime import datetime, timezone
from dotenv import load_dotenv
import json

# v1.0.2 - 6-Apr-2025
# Author: Paolo Diomede

load_dotenv()
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

# Ensure reports folder exists
REPORTS_DIR = "reports"
os.makedirs(REPORTS_DIR, exist_ok=True)

ARCHIVE_DIR = "archive"
os.makedirs(ARCHIVE_DIR, exist_ok=True)
LOG_FILE_PATH = os.path.join(ARCHIVE_DIR, "summary.log")

HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

SEARCH_URL = "https://api.github.com/search/code"
REPO_URL_TEMPLATE = "https://api.github.com/repos/{}"
EXCLUDED_ORGS = ["graphprotocol", "graphops", "edgeandnode", "streamingfast","pinax-network"]

def get_repo_metadata(full_name):
    url = REPO_URL_TEMPLATE.format(full_name)
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        data = response.json()
        return data.get("stargazers_count", 0), data.get("pushed_at", "")
    return 0, ""

def search_repositories(label, query, per_page=100, max_pages=5):
    print(f"🔍 Starting search for {label}...")
    repo_info = {}
    total_count_known = None

    for page in range(1, max_pages + 1):
        print(f"📄 Page {page}...")
        params = {"q": query, "per_page": per_page, "page": page}
        response = requests.get(SEARCH_URL, headers=HEADERS, params=params)

        if response.status_code == 403:
            print("⚠️  Rate limit hit. Waiting 60 seconds...")
            time.sleep(60)
            continue
        elif response.status_code != 200:
            print(f"❌ Error {response.status_code}")
            break

        if total_count_known is None:
            total_count_known = response.json().get("total_count", 0)
            print(f"📊 Total available GitHub results for {label}: {total_count_known}")

        items = response.json().get("items", [])
        if not items:
            break

        for item in items:
            repo = item["repository"]
            full_name = repo["full_name"]
            org = repo["owner"]["login"].lower()
            if org in EXCLUDED_ORGS:
                continue
            if full_name not in repo_info:
                stars, last_updated = get_repo_metadata(full_name)
                repo_info[full_name] = {
                    "repository": full_name,
                    "url": repo["html_url"],
                    "owner": org,
                    "stars": stars,
                    "last_updated": last_updated
                }

        if len(items) < per_page:
            break
        time.sleep(1)

    print(f"✅ {label}: {len(repo_info)} repositories collected.\n")
    return list(repo_info.values()), total_count_known


def process_and_save(label, data, csv_path, json_path):
    df = pd.DataFrame(data)
    df["last_updated"] = pd.to_datetime(df["last_updated"], errors="coerce")
    df = df.sort_values(by="last_updated", ascending=False)

    csv_full_path = os.path.join(REPORTS_DIR, csv_path)
    json_full_path = os.path.join(REPORTS_DIR, json_path)

    df.to_csv(csv_full_path, index=False)

    top_contributors = Counter(df["owner"]).most_common(10)
    pd.DataFrame(top_contributors, columns=["owner", "repo_count"]).to_json(json_full_path, orient="records", indent=2)

    print(f"📁 CSV → {csv_full_path}")
    print(f"📊 JSON → {json_full_path}\n")


def write_metadata(label, total_count, repo_count, path):
    full_path = os.path.join(REPORTS_DIR, path)
    metadata = {
        "label": label,
        "total_count": total_count,
        "repo_count": repo_count,
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    }
    with open(full_path, "w") as f:
        json.dump(metadata, f, indent=2)
    print(f"📝 Metadata → {full_path}")


if __name__ == "__main__":
    print("🛑 Excluded repositories from the following GitHub orgs/users:")
    for org in EXCLUDED_ORGS:
        print(f"   • {org}")
    print()

    subgraph_query = "filename:subgraph.yaml OR filename:subgraph.yml"
    subgraph_data, subgraph_total = search_repositories("Subgraph", subgraph_query)
    process_and_save(
        "Subgraph",
        subgraph_data,
        "subgraph_repositories_filtered.csv",
        "top_subgraph_contributors.json"
    )
    write_metadata("Subgraph", subgraph_total, len(subgraph_data), "subgraph_metadata.json")

    substreams_query = "filename:substreams.yaml OR filename:substreams.yml"
    substreams_data, substreams_total = search_repositories("Substreams", substreams_query)
    process_and_save(
        "Substreams",
        substreams_data,
        "substreams_repositories_filtered.csv",
        "top_substreams_contributors.json"
    )
    write_metadata("Substreams", substreams_total, len(substreams_data), "substreams_metadata.json")
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    
    with open(LOG_FILE_PATH, "a") as log_file:
        log_file.write(f"{timestamp}\nSubgraph repos: {subgraph_total}\nSubstreams repos: {substreams_total}\n\n")

    print("🚀 All done.")
