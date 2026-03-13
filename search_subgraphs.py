import os
import time
import requests
import pandas as pd
from collections import Counter
from datetime import datetime, timezone
from dotenv import load_dotenv
import json
import traceback

# v1.0.3 - Mar-2026
# Author: Paolo Diomede

load_dotenv()
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

# Ensure directories exist
REPORTS_DIR = "reports"
os.makedirs(REPORTS_DIR, exist_ok=True)

ARCHIVE_DIR = "archive"
os.makedirs(ARCHIVE_DIR, exist_ok=True)

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE_PATH = os.path.join(LOG_DIR, "search_subgraphs.log")

HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

SEARCH_URL = "https://api.github.com/search/code"
REPO_URL_TEMPLATE = "https://api.github.com/repos/{}"
EXCLUDED_ORGS = ["graphprotocol", "graphops", "edgeandnode", "streamingfast", "pinax-network"]


def log_message(msg):
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    line = f"[{timestamp}] {msg}"
    print(line)
    with open(LOG_FILE_PATH, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def get_repo_metadata(full_name):
    url = REPO_URL_TEMPLATE.format(full_name)
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        if response.status_code == 200:
            data = response.json()
            return data.get("stargazers_count", 0), data.get("pushed_at", "")
        else:
            log_message(f"⚠️  Could not fetch metadata for {full_name} (HTTP {response.status_code})")
    except Exception as e:
        log_message(f"❌ Exception fetching metadata for {full_name}: {e}")
    return 0, ""


def search_repositories(label, query, per_page=100, max_pages=5):
    log_message(f"🔍 Starting search for {label}...")
    repo_info = {}
    total_count_known = None

    for page in range(1, max_pages + 1):
        log_message(f"📄 Page {page}...")
        params = {"q": query, "per_page": per_page, "page": page}
        try:
            response = requests.get(SEARCH_URL, headers=HEADERS, params=params, timeout=30)
        except Exception as e:
            log_message(f"❌ Network error on page {page} for {label}: {e}")
            break

        if response.status_code == 403:
            log_message("⚠️  Rate limit hit. Waiting 60 seconds...")
            time.sleep(60)
            continue
        elif response.status_code == 401:
            log_message("❌ Error 401 — GitHub token is missing or invalid. Check your GITHUB_TOKEN env variable.")
            break
        elif response.status_code != 200:
            log_message(f"❌ Error {response.status_code} on page {page} for {label}")
            break

        try:
            payload = response.json()
        except Exception as e:
            log_message(f"❌ Failed to parse JSON response on page {page} for {label}: {e}")
            break

        if total_count_known is None:
            total_count_known = payload.get("total_count", 0)
            log_message(f"📊 Total available GitHub results for {label}: {total_count_known}")

        items = payload.get("items", [])
        if not items:
            log_message(f"ℹ️  No more items on page {page} for {label}. Stopping.")
            break

        for item in items:
            try:
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
            except Exception as e:
                log_message(f"⚠️  Skipping item due to error: {e}")
                continue

        if len(items) < per_page:
            break
        time.sleep(1)

    log_message(f"✅ {label}: {len(repo_info)} repositories collected.")
    return list(repo_info.values()), total_count_known


def process_and_save(label, data, csv_path, json_path):
    if not data:
        log_message(f"⚠️  No data for {label}, skipping save.")
        return
    try:
        df = pd.DataFrame(data)
        df["last_updated"] = pd.to_datetime(df["last_updated"], errors="coerce")
        df = df.sort_values(by="last_updated", ascending=False)

        csv_full_path = os.path.join(REPORTS_DIR, csv_path)
        json_full_path = os.path.join(REPORTS_DIR, json_path)

        df.to_csv(csv_full_path, index=False)

        top_contributors = Counter(df["owner"]).most_common(10)
        pd.DataFrame(top_contributors, columns=["owner", "repo_count"]).to_json(
            json_full_path, orient="records", indent=2
        )

        log_message(f"📁 CSV  → {csv_full_path}")
        log_message(f"📊 JSON → {json_full_path}")
    except Exception as e:
        log_message(f"❌ Error saving data for {label}: {e}")
        log_message(traceback.format_exc())


def write_metadata(label, total_count, repo_count, path):
    full_path = os.path.join(REPORTS_DIR, path)
    try:
        metadata = {
            "label": label,
            "total_count": total_count,
            "repo_count": repo_count,
            "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        }
        with open(full_path, "w") as f:
            json.dump(metadata, f, indent=2)
        log_message(f"📝 Metadata → {full_path}")
    except Exception as e:
        log_message(f"❌ Error writing metadata for {label}: {e}")


if __name__ == "__main__":
    log_message("=" * 60)
    log_message("🚀 search_subgraphs.py started")
    log_message("🛑 Excluded orgs/users: " + ", ".join(EXCLUDED_ORGS))

    try:
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

        log_message(f"📋 Summary — Subgraph:    {subgraph_total} found / {len(subgraph_data)} saved")
        log_message(f"📋 Summary — Substreams:  {substreams_total} found / {len(substreams_data)} saved")
        log_message("✅ All done.")

    except Exception as e:
        log_message(f"❌ Fatal error: {e}")
        log_message(traceback.format_exc())

    log_message("=" * 60)
