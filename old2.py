import os
import json
import shutil
import pandas as pd
from datetime import datetime, timezone, timedelta


# v1.0.4 / 18-Apr-2025
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

    # HTML and JavaScript template
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{dashboard_title}</title>
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
        <script src="https://code.jquery.com/jquery-3.7.1.js"></script>
        <script src="https://cdn.datatables.net/1.13.8/js/jquery.dataTables.min.js"></script>
        <script src="https://cdn.datatables.net/1.13.8/js/dataTables.bootstrap5.min.js"></script>
        <link rel="stylesheet" href="https://cdn.datatables.net/1.13.8/css/dataTables.bootstrap5.min.css">

        <style>
            :root {{
                --bg-color: #111;
                --text-color: #fff;
                --table-bg: #1e1e1e;
                --header-bg: #333;
                --link-color: #fff;
            }}

            .light-mode {{
                --bg-color: #f0f2f5;
                --text-color: #000;
                --table-bg: #ffffff;
                --header-bg: #ddd;
                --link-color: #0000EE;
            }}

            .home-link,
            .light-mode .home-link {{
                color: var(--text-color);
            }}

            body {{
                background-color: var(--bg-color);
                color: var(--text-color);
                font-family: Arial, sans-serif;
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
                font-size: 0.9em;
                margin: 0;
                padding: 0;
                display: flex;
                align-items: center;
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
                background: #ccc;
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
                background: white;
                transition: 0.4s;
                border-radius: 50%;
            }}

            .toggle-switch input:checked + .slider,
            input:checked + .slider {{
                background: #2196F3;
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
                height: 2px;
                background: linear-gradient(to right, rgba(255, 255, 255, 0), rgba(255, 255, 255, 0.5), rgba(255, 255, 255, 0));
                margin: 15px 0;
            }}

            .light-mode .divider {{
                background: linear-gradient(to right, rgba(0, 0, 0, 0), rgba(0, 0, 0, 0.7), rgba(0, 0, 0, 0));
            }}
            .footer {{
                text-align: center;
                margin: 10px 0 40px;
                font-size: 0.9rem;
                opacity: 0.9;
            }}
            .footer a {{
                color: #80bfff;
                text-decoration: none;
                transition: color 0.3s ease;
            }}
            .footer a:hover {{
                color: #4d94ff;
            }}
            .light-mode .footer a {{
                color: #0066cc;
            }}
            .light-mode .footer a:hover {{
                color: #0033ff;
            }}
            .footer-divider {{
                border: none;
                border-bottom: 1px solid rgba(200, 200, 200, 0.2);
                margin: 40px 0 10px;
                opacity: 0.8;
             }}
            .display-5 {{
                margin-top: 0 !important;
                margin-bottom: 0 !important;
            }}

            .current-page-title {{
                color: #00bcd4;
                font-weight: bold;
            }}

            .light-mode .current-page-title {{
                color: #1a73e8;
            }}
            .download-button {{
                padding: 5px 10px;
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 3px;
                cursor: pointer;
            }}
            .download-button:hover {{
                background-color: #45a049;
            }}
        </style>
    """
    
    html_content += f"""

            <div class="header-container">
                <div class="breadcrumb" style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; font-weight: 500; font-size: 0.85em; letter-spacing: 0.3px; text-shadow: 0 1px 2px rgba(0,0,0,0.15);">
                    <a href="https://graphtools.pro" class="home-link" style="text-decoration: none;">🏠 Home</a>&nbsp;&nbsp;&raquo;&nbsp;&nbsp;
                    <span class="current-page-title">👨‍💻 GitHub Dashboard</span>    
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
                Generated on: {timestamp} - (updated every 24 hours) - v{DASHBOARD_VERSION}
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
            <div id="custom-toolbar" class="d-flex justify-content-between align-items-center mb-2" style="gap: 8px;">
                <button  class="download-button" style="font-size: 0.75rem;" onclick="downloadCSV('{csv_file}')">Download CSV</button>
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
                    {''.join(f"""
                    <tr>
                        <td>
                            <a href='{row['url']}' class='text-info' target='_blank'>🔗 {row['repository']}</a>
                        </td>
                        <td>
                            <img src='{github_avatar(row["owner"])}' 
                                alt='{row["owner"]}' 
                                style='width:24px;height:24px;border-radius:50%;vertical-align:middle;margin-right:6px;'
                                onerror="this.onerror=null; this.src='https://via.placeholder.com/24?text=👤';">
                            <a href='https://github.com/{row['owner']}' target='_blank'>{row['owner']}</a>
                        </td>
                        <td>{row['stars']}</td>
                        <td>{row['last_updated']}</td>
                    </tr>
                    """ for index, row in df.iterrows())}
                </tbody>

            </table>
        </div>
        <script>
            $(document).ready(function() {{
                $('#dashboard').DataTable({{
                    paging: true,
                    pageLength: 50,
                    lengthChange: false,
                    searching: true,
                    ordering: true,
                    order: [[3, 'desc']],
                    dom: '<"d-flex justify-content-between align-items-center mb-2"<"#custom-toolbar">f>t<"mt-2"p>'
                }});
            }});
            
            function toggleTheme() {{
                document.body.classList.toggle('light-mode');
                const icon = document.getElementById('toggle-icon');
                icon.textContent = document.body.classList.contains('light-mode') ? '☀️' : '🌙';
            }}

            function downloadCSV(csv_file) {{
                const fileName = csv_file.split('/').pop(); // remove any folder path
                const link = document.createElement('a');
                link.href = fileName; // use just the file name as the relative path
                link.download = fileName; // ensures downloaded file has the correct name
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
            }}
                
        </script>

        <hr class="footer-divider">
        <div class="footer">
            ©<script>document.write(new Date().getFullYear())</script>&nbsp;
            <a href="https://graphtools.pro">Graph Tools Pro</a> :: Made with ❤️ by 
            <a href="https://x.com/graphtronauts_c" target="_blank">Graphtronauts</a>
            for <a href="https://x.com/graphprotocol" target="_blank">The Graph</a> ecosystem 👨‍🚀
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