#!/usr/bin/env python3
"""
Start Simple KGAS UI Server
A no-nonsense server that definitely works
"""

import subprocess
import time
import sys
import os

def main():
    print("🚀 Starting Simple KGAS UI Server")
    print("=" * 50)
    
    # Find a port that works
    port = 8899
    print(f"Using port: {port}")
    
    # Change to UI directory
    os.chdir('ui')
    print(f"Working directory: {os.getcwd()}")
    
    # List files to confirm
    files = os.listdir('.')
    print(f"UI files available: {[f for f in files if f.endswith('.html')]}")
    
    print(f"\n✅ Starting server...")
    print(f"📌 Open your browser and go to:")
    print(f"   👉 http://localhost:{port}/simple_working_ui.html")
    print(f"\n🛑 Press Ctrl+C to stop\n")
    
    # Start server
    try:
        subprocess.run(['python3', '-m', 'http.server', str(port)])
    except KeyboardInterrupt:
        print("\n👋 Server stopped!")

if __name__ == "__main__":
    main()