#!/usr/bin/env python3
"""
Simple HTTP server to view HTML visualizations locally
"""

import http.server
import socketserver
import os
import webbrowser
from pathlib import Path

# Configuration
PORT = 8888
DIRECTORY = "/home/brian/projects/Digimons/kunst_visualizations"

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

def create_index_page():
    """Create an index page listing all visualizations"""
    viz_dir = Path(DIRECTORY)
    html_files = sorted(viz_dir.glob("*.html"))
    
    index_content = """
<!DOCTYPE html>
<html>
<head>
    <title>Kunst-Carter Analysis Visualizations</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        h1 {
            color: #2c3e50;
            text-align: center;
        }
        .viz-list {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        .viz-item {
            margin: 10px 0;
            padding: 10px;
            border-left: 4px solid #3498db;
            background: #f8f9fa;
        }
        .viz-item a {
            text-decoration: none;
            color: #2c3e50;
            font-weight: bold;
        }
        .viz-item a:hover {
            color: #3498db;
        }
        .description {
            color: #7f8c8d;
            font-size: 14px;
            margin-top: 5px;
        }
        .highlight {
            background: #e8f4f8;
            border-left-color: #e74c3c;
        }
    </style>
</head>
<body>
    <h1>🎨 Kunst-Carter Analysis Visualizations</h1>
    
    <div class="viz-list">
        <h2>📊 Interactive Visualizations</h2>
        
        <div class="viz-item highlight">
            <a href="kunst_carter_visual_report.html">📄 Complete Visual Report</a>
            <div class="description">Comprehensive report with all visualizations and insights</div>
        </div>
        
        <div class="viz-item highlight">
            <a href="kunst_carter_dashboard.html">📊 Interactive Dashboard</a>
            <div class="description">All charts in one interactive dashboard</div>
        </div>
        
        <h3>Individual Charts:</h3>
"""
    
    # Add individual chart links
    descriptions = {
        "risk_gauge": "Conspiracy theory risk assessment gauge (42.6% moderate risk)",
        "psychological_radar": "Radar chart showing presence of psychological factors",
        "theme_balance": "Balance between protective and risk-inducing themes",
        "discourse_patterns": "Frequency of different rhetorical patterns",
        "protective_risk_pie": "Distribution of protective vs risk factors",
        "word_frequency": "Frequency analysis of key word categories"
    }
    
    for html_file in html_files:
        if html_file.name not in ["kunst_carter_visual_report.html", "kunst_carter_dashboard.html"]:
            name = html_file.stem.replace("kunst_carter_", "")
            desc = descriptions.get(name, "Interactive visualization")
            index_content += f"""
        <div class="viz-item">
            <a href="{html_file.name}">🔍 {name.replace('_', ' ').title()}</a>
            <div class="description">{desc}</div>
        </div>
"""
    
    index_content += """
    </div>
    
    <div style="text-align: center; margin-top: 30px; color: #7f8c8d;">
        <p>Server running on http://localhost:8888</p>
        <p>Press Ctrl+C to stop the server</p>
    </div>
</body>
</html>
"""
    
    index_file = viz_dir / "index.html"
    with open(index_file, 'w') as f:
        f.write(index_content)
    
    return index_file

def main():
    # Create index page
    index_file = create_index_page()
    print(f"✅ Created index page: {index_file}")
    
    # Start server
    os.chdir(DIRECTORY)
    
    with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
        print(f"\n🌐 Server running at http://localhost:{PORT}")
        print(f"📁 Serving files from: {DIRECTORY}")
        print("\n📋 Available visualizations:")
        print(f"   • http://localhost:{PORT}/index.html - Visualization Index")
        print(f"   • http://localhost:{PORT}/kunst_carter_visual_report.html - Complete Report")
        print(f"   • http://localhost:{PORT}/kunst_carter_dashboard.html - Interactive Dashboard")
        print("\n⚡ Press Ctrl+C to stop the server\n")
        
        # Try to open browser
        try:
            webbrowser.open(f'http://localhost:{PORT}/index.html')
        except:
            pass
        
        httpd.serve_forever()

if __name__ == "__main__":
    main()