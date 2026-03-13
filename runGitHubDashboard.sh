#!/bin/bash
# ─────────────────────────────────────────────────────────────
#  runGitHubDashboard.sh
#  Sets up venv, installs requirements, then runs the pipeline:
#    1. search_subgraphs.py
#    2. generate_dashboards_dynamic.py
#    3. copy reports/ into /var/www/github/current
# ─────────────────────────────────────────────────────────────

set -euo pipefail

# Always run relative to this script's location
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

VENV_DIR="$SCRIPT_DIR/.venv"
LOG_DIR="$SCRIPT_DIR/logs"
RUN_LOG="$LOG_DIR/run.log"
REPORTS_DIR="$SCRIPT_DIR/reports"
DEPLOY_DIR="/var/www/github/current"

# ── Ensure logs folder exists ─────────────────────────────────
mkdir -p "$LOG_DIR"

# ── Logging helper ────────────────────────────────────────────
log() {
    local msg="[$(date -u '+%Y-%m-%d %H:%M:%S UTC')] $*"
    echo "$msg"
    echo "$msg" >> "$RUN_LOG"
}

log "============================================================"
log "🚀 runGitHubDashboard.sh started"

# ── Create venv if it doesn't exist ──────────────────────────
if [ ! -d "$VENV_DIR" ]; then
    log "📦 Creating virtual environment at .venv ..."
    python3 -m venv "$VENV_DIR"
    log "✅ Virtual environment created."
else
    log "✅ Virtual environment already exists — skipping creation."
fi

# ── Activate venv ─────────────────────────────────────────────
source "$VENV_DIR/bin/activate"
log "🐍 Python: $(python --version)"

# ── Install / upgrade requirements ───────────────────────────
log "📥 Installing requirements from requirements.txt ..."
pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt
log "✅ Requirements installed."

# ── Step 1: fetch data from GitHub API ───────────────────────
log "------------------------------------------------------------"
log "▶ Step 1 — search_subgraphs.py"
log "------------------------------------------------------------"
python search_subgraphs.py
log "✅ search_subgraphs.py completed."

# ── Step 2: generate HTML dashboards ─────────────────────────
log "------------------------------------------------------------"
log "▶ Step 2 — generate_dashboards_dynamic.py"
log "------------------------------------------------------------"
python generate_dashboards_dynamic.py
log "✅ generate_dashboards_dynamic.py completed."

# ── Step 3: deploy reports to nginx folder ───────────────────
log "------------------------------------------------------------"
log "▶ Step 3 — deploy reports to $DEPLOY_DIR"
log "------------------------------------------------------------"

if [ ! -d "$REPORTS_DIR" ]; then
    log "❌ Reports directory not found: $REPORTS_DIR"
    exit 1
fi

sudo mkdir -p "$DEPLOY_DIR"
sudo rsync -av --delete "$REPORTS_DIR"/ "$DEPLOY_DIR"/
log "✅ Reports deployed to $DEPLOY_DIR"

# ── Step 4: sync social card images ──────────────────────────
log "------------------------------------------------------------"
log "▶ Step 4 — sync images to $DEPLOY_DIR/images"
log "------------------------------------------------------------"
IMAGES_DIR="$SCRIPT_DIR/images"
if [ -d "$IMAGES_DIR" ]; then
    sudo mkdir -p "$DEPLOY_DIR/images"
    sudo rsync -av "$IMAGES_DIR"/ "$DEPLOY_DIR/images"/
    log "✅ Images synced to $DEPLOY_DIR/images"
else
    log "⚠️  images/ directory not found at $IMAGES_DIR — skipping."
fi

# ── Done ──────────────────────────────────────────────────────
log "🏁 All done."
log "============================================================"