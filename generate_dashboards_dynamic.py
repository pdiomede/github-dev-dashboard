import os
import json
import shutil
import pandas as pd
from datetime import datetime, timezone, timedelta

# v1.0.5 / 25-Apr-2025
# Author: Paolo Diomede
DASHBOARD_VERSION="1.0.5"


# Ensure reports folder exists
reports_folder = "reports"
os.makedirs(reports_folder, exist_ok=True)

# Function to reliably fetch GitHub owner avatar URL
def github_avatar(owner):
    return f"https://avatars.githubusercontent.com/{owner}"

dashboard_files = [os.path.join(reports_folder, "index.html"), os.path.join(reports_folder, "index2.html")]
archive_folder = "./archive"

if not os.path.exists(archive_folder):
    os.makedirs(archive_folder)

yesterday = datetime.now() - timedelta(days=1)
date_suffix = yesterday.strftime("%m%d%Y")

# Get data to be used in the log and report files
timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

def archive_old_dashboards():
    for file in dashboard_files:
        if os.path.exists(file):
            # Get just the file name like "index.html"
            base_name = os.path.basename(file)
            name_no_ext = os.path.splitext(base_name)[0]
            archived_file_name = f"{name_no_ext}_{date_suffix}.html"
            archived_path = os.path.join(archive_folder, archived_file_name)

            shutil.move(file, archived_path)
            print(f"✅ Archived {file} to {archived_path}")

# Run the archive logic
archive_old_dashboards()


# Function to generate HTML dashboard
def generate_dashboard(csv_file, metadata_file, output_file, dashboard_title, dashboard, other, other_dashboard_link,logo):

    df = pd.read_csv(csv_file)

    df['last_updated'] = pd.to_datetime(df['last_updated'])
    df.sort_values(by='last_updated', ascending=False, inplace=True)
    df['last_updated'] = df['last_updated'].dt.strftime('%Y-%m-%d %H:%M')

    # Load metadata
    with open(metadata_file) as f:
        metadata = json.load(f)

    # Determine the page-specific SEO details based on dashboard type
    is_subgraphs = dashboard == "Subgraphs"
    page_url = "https://graphtools.pro/github/" if is_subgraphs else "https://graphtools.pro/github/index2.html"
    page_description = (
        "Explore GitHub repositories for Subgraphs in The Graph ecosystem, with details on stars, owners, and last updates."
        if is_subgraphs
        else "Discover GitHub repositories for Substreams in The Graph ecosystem, including stars, owners, and update history."
    )
    og_description = (
        "View GitHub repositories for Subgraphs in The Graph ecosystem with detailed analytics."
        if is_subgraphs
        else "Check out GitHub repositories for Substreams in The Graph ecosystem with analytics."
    )
    og_image = (
        "https://graphtools.pro/github/images/social-card-subgraphs.png"
        if is_subgraphs
        else "https://graphtools.pro/github/images/social-card-substreams.png"
    )
    og_image_alt = (
        "Subgraphs Dashboard — Graph Tools Pro"
        if is_subgraphs
        else "Substreams Dashboard — Graph Tools Pro"
    )
    page_keywords = (
        "The Graph, subgraphs, GitHub repositories, open source, GRT, Graph Protocol, decentralized indexing, Graph Tools Pro, subgraph analytics, blockchain development"
        if is_subgraphs
        else "The Graph, substreams, GitHub repositories, open source, GRT, Graph Protocol, streaming data, Graph Tools Pro, blockchain development, real-time data"
    )

    # Pre-build table rows to avoid nested f-string (not supported in Python < 3.12)
    table_rows = ''.join(f"""
                    <tr>
                        <td data-label="Repository">
                            🔗 <a href="{row['url']}" class='text-info' target='_blank'>{row['repository']}</a>
                        </td>
                        <td data-label="Owner">
                            <img src="{github_avatar(row['owner'])}"
                                alt="{row['owner']}"
                                style='width:24px;height:24px;border-radius:50%;vertical-align:middle;margin-right:6px;'
                                onerror="this.onerror=null; this.src='https://via.placeholder.com/24?text=👤';">
                            <a href='https://github.com/{row["owner"]}' target='_blank'>{row['owner']}</a>
                        </td>
                        <td data-label="Stars">{row['stars']}</td>
                        <td data-label="Last Updated">{row['last_updated']}</td>
                    </tr>
                    """ for _, row in df.iterrows())

    # HTML and JavaScript template
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta name="description" content="{page_description}">
        <meta name="robots" content="index, follow">
        <meta name="keywords" content="{page_keywords}">
        <meta name="author" content="Paolo Diomede — Graph Tools Pro">

        <!-- Open Graph (Facebook, LinkedIn, Discord, Telegram, WhatsApp) -->
        <meta property="og:type" content="website">
        <meta property="og:site_name" content="Graph Tools Pro">
        <meta property="og:title" content="Graph Tools Pro :: {dashboard_title}">
        <meta property="og:description" content="{og_description}">
        <meta property="og:url" content="{page_url}">
        <meta property="og:image" content="{og_image}">
        <meta property="og:image:width" content="1200">
        <meta property="og:image:height" content="630">
        <meta property="og:image:alt" content="{og_image_alt}">

        <!-- X / Twitter Card -->
        <meta name="twitter:card" content="summary_large_image">
        <meta name="twitter:site" content="@graphtronauts_c">
        <meta name="twitter:creator" content="@pdiomede">
        <meta name="twitter:title" content="Graph Tools Pro :: {dashboard_title}">
        <meta name="twitter:description" content="{og_description}">
        <meta name="twitter:image" content="{og_image}">
        <meta name="twitter:image:alt" content="{og_image_alt}">
        
        <title>Graph Tools Pro: {dashboard_title} & Analytics</title>
        <link rel="canonical" href="{page_url}">
        <link rel="icon" type="image/png" href="https://graphtools.pro/favicon.ico">
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600&display=swap" rel="stylesheet">

        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
        <script src="https://code.jquery.com/jquery-3.7.1.js"></script>
        <script src="https://cdn.datatables.net/1.13.8/js/jquery.dataTables.min.js"></script>
        <script src="https://cdn.datatables.net/1.13.8/js/dataTables.bootstrap5.min.js"></script>
        <link rel="stylesheet" href="https://cdn.datatables.net/1.13.8/css/dataTables.bootstrap5.min.css">
        
        <!-- Plausible Analytics -->
        <script defer data-domain="graphtools.pro/github" src="https://plausible.io/js/script.file-downloads.hash.outbound-links.pageview-props.tagged-events.js"></script>
        <script>window.plausible = window.plausible || function() {{ (window.plausible.q = window.plausible.q || []).push(arguments) }}</script>

        <style>
            /* ── The Graph brand palette ── */
            :root {{
                --bg-color:    #0C0A1D;
                --text-color:  #F8F6FF;
                --text-muted:  #9491A7;
                --table-bg:    #13112A;
                --header-bg:   #1A1833;
                --link-color:  #4C66FF;
                --border:      rgba(111, 76, 255, 0.22);
                --border-mid:  rgba(111, 76, 255, 0.38);
                --accent:      #4C66FF;
                --accent-light:#6F4CFF;
                --aqua:        #66D8FF;
                --solar:       #FFA801;
            }}

            .light-mode {{
                --bg-color:   #F5F3FF;
                --text-color: #0C0A1D;
                --text-muted: #494755;
                --table-bg:   #FFFFFF;
                --header-bg:  #EDE9FE;
                --link-color: #4C66FF;
                --border:     rgba(111, 76, 255, 0.18);
                --border-mid: rgba(111, 76, 255, 0.32);
            }}

            .home-link,
            .light-mode .home-link {{
                color: var(--text-muted);
            }}

            body {{
                background-color: var(--bg-color);
                color: var(--text-color);
                font-family: 'Poppins', sans-serif;
                padding: 10px 20px 20px 20px;
                margin-top: 0;
                transition: all 0.3s ease;
            }}

            body.light-mode .table-bordered-custom td {{
                background-color: #fff;
                color: #333;
            }}

            body.light-mode .table-bordered-custom th {{
                background-color: #ddd;
                color: #222;
            }}

            .header-container {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 15px;
                line-height: 1;
            }}

            .breadcrumb {{
                font-size: 0.85em;
                font-weight: 500;
                letter-spacing: 0.2px;
                margin: 0;
                padding: 0;
                display: flex;
                align-items: center;
                gap: 6px;
                color: var(--text-muted);
            }}
            .breadcrumb a.home-link {{
                display: inline-flex;
                align-items: center;
                gap: 5px;
                color: var(--text-muted);
                text-decoration: none;
                transition: color 0.2s;
            }}
            .breadcrumb a.home-link:hover {{
                color: var(--accent);
            }}
            .breadcrumb a.home-link svg {{
                flex-shrink: 0;
            }}
            .breadcrumb .sep {{
                opacity: 0.4;
                font-size: 1em;
            }}
            .current-page-title {{
                display: inline-flex;
                align-items: center;
                gap: 5px;
                color: var(--aqua);
                font-weight: 600;
            }}
            .current-page-title svg {{
                flex-shrink: 0;
            }}

            .toggle-container {{
                display: flex;
                align-items: center;
                margin: 0;
            }}

            .toggle-switch {{
                position: relative;
                width: 50px;
                height: 24px;
                margin-right: 10px;
            }}

            .toggle-switch input {{
                opacity: 0;
                width: 0;
                height: 0;
            }}

            .toggle-switch .slider,
            .slider {{
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: #494755;
                transition: 0.4s;
                border-radius: 34px;
            }}

            .toggle-switch .slider:before,
            .slider:before {{
                position: absolute;
                content: "";
                height: 18px;
                width: 18px;
                left: 4px;
                bottom: 3px;
                background: #F8F6FF;
                transition: 0.4s;
                border-radius: 50%;
            }}

            .toggle-switch input:checked + .slider,
            input:checked + .slider {{
                background: #6F4CFF;
            }}

            .toggle-switch input:checked + .slider:before,
            input:checked + .slider:before {{
                transform: translateX(24px);
            }}

            #toggle-icon {{
                font-size: 1.5rem;
                line-height: 1;
                transition: transform 0.4s ease;
            }}

            .divider {{
                border: 0;
                height: 1px;
                background: linear-gradient(to right,
                    transparent,
                    rgba(111, 76, 255, 0.5),
                    transparent);
                margin: 15px 0;
            }}

            .footer {{
                text-align: center;
                margin: 10px 0 40px;
                font-size: 0.9rem;
                opacity: 0.9;
            }}
            .footer a {{
                color: var(--accent);
                text-decoration: none;
                transition: color 0.3s ease;
            }}
            .footer a:hover {{
                color: var(--aqua);
            }}
            .light-mode .footer a {{
                color: var(--accent);
            }}
            .light-mode .footer a:hover {{
                color: var(--accent-light);
            }}
            .footer-divider {{
                border: none;
                border-bottom: 1px solid var(--border);
                margin: 40px 0 10px;
                opacity: 0.8;
             }}
            .display-5 {{
                margin-top: 0 !important;
                margin-bottom: 0 !important;
            }}
            .download-button {{
                padding: 5px 14px;
                background: transparent;
                color: var(--accent);
                border: 1px solid var(--accent);
                border-radius: 6px;
                cursor: pointer;
                font-family: inherit;
                font-size: 0.85em;
                font-weight: 500;
                transition: background 0.2s, color 0.2s;
            }}
            .download-button:hover {{
                background: var(--accent);
                color: #F8F6FF;
            }}
            @media (max-width: 768px) {{
                body {{ padding: 8px 12px 20px; }}
                .header-container {{ flex-direction: column; align-items: flex-start; gap: 10px; }}
                .search-download-row {{ flex-direction: column; gap: 8px; align-items: stretch !important; }}
                #customSearchBox {{ max-width: 100% !important; }}
                .download-button {{ align-self: flex-start; }}
                .dataTables_wrapper .dataTables_paginate {{ text-align: center; }}
                .dataTables_info {{ font-size: 0.8em; }}
            }}
            @media (max-width: 600px) {{
                thead {{ display: none; }}
                tbody tr {{ display: block; border: 1px solid var(--border-mid); border-radius: 8px; margin-bottom: 10px; overflow: hidden; }}
                tbody td {{ display: flex; justify-content: space-between; align-items: flex-start; padding: 8px 12px; border: none; border-bottom: 1px solid var(--border); font-size: 0.85em; gap: 10px; word-break: break-word; }}
                tbody td:last-child {{ border-bottom: none; }}
                tbody td::before {{ content: attr(data-label); color: var(--text-muted); font-size: 0.75em; font-weight: 600; text-transform: uppercase; letter-spacing: 0.07em; flex-shrink: 0; min-width: 90px; padding-top: 2px; }}
                .footer {{ flex-direction: column; gap: 4px; }}
                .footer-sep {{ display: none; }}
            }}
        </style>
    
    
    </head>

    <body>
    """
    
    html_content += f"""

            <div class="header-container">
                <div class="breadcrumb">
                    <a href="https://graphtools.pro" class="home-link">
                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="15" height="15" stroke="currentColor" fill="none" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>
                        Home
                    </a>
                    <span class="sep">›</span>
                    <span class="current-page-title">
                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="15" height="15" stroke="currentColor" fill="none" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/></svg>
                        GitHub Dashboard
                    </span>
                </div>
                <div class="toggle-container">
                    <label class="toggle-switch">
                        <input type="checkbox" onclick="toggleTheme()">
                        <span class="slider"></span>
                    </label>
                    <span id="toggle-icon">🌙</span>
                </div>
            </div>
            <hr class="divider">

            <div style="text-align: center; font-size: 0.8em; color: var(--text-color); margin: 0 0 4px 0;">
                Generated on: {timestamp} - (updated every day at 1am UTC)
            </div>

        <div class="container position-relative" style="padding-top: 0; padding-bottom: 0;">
            
            <h1 class="display-5 fw-bold text-center" style="margin-top: 0; margin-bottom: 0;">
                <img src="{logo}" style="height: 1.5em; vertical-align: middle; margin-right: 8px;">
                {dashboard_title}
            </h1>

           <p class="text-center mt-2" style="font-size: 0.95em; line-height: 1.8;">
            ‼️ This is the list of GitHub repositories using {dashboard}, for {other} click 
            <a href="{other_dashboard_link}" class="text-decoration-none text-info">here</a> ⬅️            
            <br/>
            </p>

            <br/>
            
            <div class="text-start mb-3">
                🔍 Total available GitHub repositories: {metadata['total_count']}<br>
                📦 Repositories collected: {metadata['repo_count']}<br>
                🕒 Report generated on: {metadata['generated_at']}
            </div>

            <div style="font-size: 0.85em;">
                Excluding:
                <img src="https://avatars.githubusercontent.com/graphprotocol" alt="graphprotocol" style="width:20px;height:20px;border-radius:50%;vertical-align:middle;margin-right:4px;">
                <a href="https://github.com/graphprotocol" target="_blank">graphprotocol</a> | 
                <img src="https://avatars.githubusercontent.com/edgeandnode" alt="edgeandnode" style="width:20px;height:20px;border-radius:50%;vertical-align:middle;margin-right:4px;">
                <a href="https://github.com/edgeandnode" target="_blank">edgeandnode</a> | 
                <img src="https://avatars.githubusercontent.com/streamingfast" alt="streamingfast" style="width:20px;height:20px;border-radius:50%;vertical-align:middle;margin-right:4px;">
                <a href="https://github.com/streamingfast" target="_blank">streamingfast</a> |  
                <img src="https://avatars.githubusercontent.com/pinax-network" alt="pinax" style="width:20px;height:20px;border-radius:50%;vertical-align:middle;margin-right:4px;">
                <a href="https://github.com/pinax-network" target="_blank">pinax</a> | 
                <img src="https://avatars.githubusercontent.com/graphops" alt="graphops" style="width:20px;height:20px;border-radius:50%;vertical-align:middle;margin-right:4px;">
                <a href="https://github.com/graphops" target="_blank">graphops</a>
            </div>

            <br />

            <div class="d-flex justify-content-between align-items-center mb-2 search-download-row">
                <input type="text" id="customSearchBox" class="form-control form-control-sm" style="max-width:300px;width:100%;" placeholder="Search repositories..." onkeyup="filterTable()" />
                <button  class="download-button" style="font-size: 0.75rem;flex-shrink:0;" onclick="downloadCSV('{csv_file}')">Download CSV</button>
            </div>

            <table id="dashboard" class="table table-dark table-striped table-hover table-bordered-custom" style="width:100%">
                <thead>
                    <tr>
                        <th>Repository</th>
                        <th>Owner</th>
                        <th>Stars</th>
                        <th>Last Updated</th>
                    </tr>
                </thead>
                
                <tbody>
                    {table_rows}
                </tbody>

            </table>
        </div>
        <script>
            $(document).ready(function() {{
                $('#dashboard').DataTable({{
                    paging: true,
                    pageLength: 50,
                    lengthChange: false,
                    searching: false, // Disable default search
                    ordering: true,
                    order: [[3, 'desc']],
                    dom: '<"row mb-2 align-items-center"<"col-sm-6"l><"col-sm-6 text-end small"i>>t<"mt-2"p>'
                }});
            }});
            
            function filterTable() {{
                const input = document.getElementById("customSearchBox");
                const filter = input.value.toLowerCase();
                const table = document.getElementById("dashboard");
                const tr = table.getElementsByTagName("tr");

                for (let i = 1; i < tr.length; i++) {{
                    const rowText = tr[i].textContent.toLowerCase();
                    tr[i].style.display = rowText.includes(filter) ? "" : "none";
                }}
            }}

            function toggleTheme() {{
                document.body.classList.toggle('light-mode');
                const icon = document.getElementById('toggle-icon');
                icon.textContent = document.body.classList.contains('light-mode') ? '☀️' : '🌙';
            }}

            function downloadCSV(csv_file) {{
                const fileName = csv_file.split('/').pop(); // extract file name only
                const link = document.createElement('a');
                link.href = fileName; // use relative path assuming the file is in the same directory
                link.download = fileName;
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
            }}
                
        </script>

        <hr class="footer-divider">
        <div class="footer" style="display:flex;align-items:center;justify-content:center;gap:0;flex-wrap:wrap;">
            <span>©<script>document.write(new Date().getFullYear())</script>&nbsp;<a href="https://graphtools.pro">Graph Tools Pro</a></span>
            <span style="opacity:0.4;">&nbsp;&nbsp;|&nbsp;&nbsp;</span>
            <span>GitHub Dashboard v{DASHBOARD_VERSION}</span>
            <span style="opacity:0.4;">&nbsp;&nbsp;|&nbsp;&nbsp;</span>
            <span>Author: <a href="https://x.com/pdiomede" target="_blank">Paolo Diomede</a></span>
            <span style="opacity:0.4;">&nbsp;&nbsp;|&nbsp;&nbsp;</span>
            <a href="https://github.com/pdiomede/graph-github-dashboard" target="_blank" style="display:inline-flex;align-items:center;gap:4px;">
                <svg height="14" width="14" viewBox="0 0 16 16" fill="currentColor" style="vertical-align:middle;" aria-hidden="true"><path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z"/></svg>
                View on GitHub
            </a>
        </div>
    
    </body>

    </html>
    """

    # Write HTML content to file
    with open(output_file, "w") as file:
        file.write(html_content)

# Generate dashboards
generate_dashboard(
    os.path.join(reports_folder, "subgraph_repositories_filtered.csv"),
    os.path.join(reports_folder, "subgraph_metadata.json"),
    os.path.join(reports_folder, "index.html"),
    "Subgraphs Dashboard", "Subgraphs", "Substreams", "index2.html","graph.jpg"
)

generate_dashboard(
    os.path.join(reports_folder, "substreams_repositories_filtered.csv"),
    os.path.join(reports_folder, "substreams_metadata.json"),
    os.path.join(reports_folder, "index2.html"),
    "Substreams Dashboard", "Substreams", "Subgraphs", "index.html","sf.png"
)