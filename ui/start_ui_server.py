#!/usr/bin/env python3
"""
Start KGAS UI Server
Simple script to start the UI server for testing
"""

import subprocess
import time
import webbrowser
import sys
import os
import signal

def find_free_port():
    """Find a free port"""
    import socket
    for port in range(8888, 9999):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.bind(('', port))
            s.close()
            return port
        except:
            continue
    return None

def main():
    """Start the UI server"""
    port = find_free_port()
    if not port:
        print("❌ No free ports available")
        sys.exit(1)
        
    print("🚀 Starting KGAS Research UI Server")
    print("=" * 50)
    print(f"Port: {port}")
    print(f"URL: http://localhost:{port}/research_ui.html")
    print("\nStarting server...")
    
    # Change to UI directory
    os.chdir('ui')
    
    # Start server
    server = subprocess.Popen(
        ['python3', '-m', 'http.server', str(port)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Wait a moment
    time.sleep(1)
    
    print(f"\n✅ Server is running!")
    print(f"\n📌 Open your browser and navigate to:")
    print(f"   👉 http://localhost:{port}/research_ui.html")
    print(f"\n   Or for Streamlit UI:")
    print(f"   👉 Run: streamlit run graphrag_ui.py")
    print(f"\n   Or for React app:")
    print(f"   👉 cd research-app && npm install && npm run dev")
    print(f"\nPress Ctrl+C to stop the server")
    
    # Keep running
    try:
        server.wait()
    except KeyboardInterrupt:
        print("\n\n✋ Stopping server...")
        server.terminate()
        print("👋 Server stopped. Goodbye!")

if __name__ == "__main__":
    main()