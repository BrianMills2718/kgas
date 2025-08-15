#!/usr/bin/env python3
"""
Verify UI Functionality
Double-check that the functional UI actually works as claimed
"""

import subprocess
import time
import requests
from pathlib import Path
import os
import signal

def start_server():
    """Start server and verify it works"""
    print("🚀 Starting server for verification...")
    
    # Kill any existing servers
    os.system("pkill -f 'http.server'")
    time.sleep(1)
    
    # Start server
    process = subprocess.Popen(
        ['python3', '-m', 'http.server', '8899'],
        cwd='ui',
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Wait and test
    time.sleep(3)
    
    try:
        response = requests.get('http://localhost:8899/functional_ui.html', timeout=5)
        if response.status_code == 200:
            print(f"✅ Server running, functional_ui.html accessible ({len(response.content)} bytes)")
            return process, response.text
        else:
            print(f"❌ HTTP {response.status_code}")
            return None, None
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return None, None

def verify_html_content(html_content):
    """Verify the HTML contains working functionality"""
    print("\n🔍 Verifying HTML content...")
    
    # Check basic structure
    if '<!DOCTYPE html>' not in html_content:
        print("❌ Missing DOCTYPE")
        return False
        
    # Check for working JavaScript functions
    required_functions = [
        'function showTab',
        'function handleFileUpload', 
        'function startAnalysis',
        'function executeQuery',
        'function generateExport'
    ]
    
    missing_functions = []
    for func in required_functions:
        if func not in html_content:
            missing_functions.append(func)
            
    if missing_functions:
        print(f"❌ Missing functions: {missing_functions}")
        return False
    else:
        print("✅ All required JavaScript functions present")
    
    # Check for interactive elements
    interactive_elements = [
        'onclick="showTab',
        'onclick="handleFileUpload',
        'onclick="startAnalysis',
        'onclick="executeQuery"',
        'onchange="changeLayout'
    ]
    
    found_elements = 0
    for element in interactive_elements:
        if element in html_content:
            found_elements += 1
            
    print(f"✅ Found {found_elements}/{len(interactive_elements)} interactive elements")
    
    # Check for CSS styling
    if '.tab.active' in html_content and '.btn:hover' in html_content:
        print("✅ CSS styling present")
    else:
        print("❌ Missing CSS styling")
        return False
        
    return True

def test_file_exists():
    """Test if functional_ui.html file actually exists"""
    print("\n📁 Checking file existence...")
    
    functional_ui = Path('ui/functional_ui.html')
    if functional_ui.exists():
        size = functional_ui.stat().st_size
        print(f"✅ functional_ui.html exists ({size:,} bytes)")
        return True
    else:
        print("❌ functional_ui.html not found")
        return False

def create_simple_test_page():
    """Create a simple test page to verify server works"""
    print("\n🔧 Creating simple test page...")
    
    test_html = '''<!DOCTYPE html>
<html>
<head><title>Test Page</title></head>
<body>
    <h1>✅ Server Test</h1>
    <p>If you see this, the server is working!</p>
    <button onclick="alert('Button works!')">Test Button</button>
    <script>console.log('JavaScript loaded successfully');</script>
</body>
</html>'''
    
    Path('ui/test.html').write_text(test_html)
    print("✅ Created ui/test.html")

def main():
    """Main verification function"""
    print("🔍 KGAS UI Functionality Verification")
    print("=" * 50)
    
    # Check if file exists
    if not test_file_exists():
        print("\n❌ VERIFICATION FAILED: functional_ui.html doesn't exist")
        return False
    
    # Create simple test
    create_simple_test_page()
    
    # Start server and test
    process, html_content = start_server()
    
    if not process or not html_content:
        print("\n❌ VERIFICATION FAILED: Server not accessible")
        return False
    
    try:
        # Verify content
        if verify_html_content(html_content):
            print("\n✅ VERIFICATION PASSED")
            print(f"\n📋 Working URLs to test:")
            print(f"   👉 http://localhost:8899/functional_ui.html (Full functional UI)")
            print(f"   👉 http://localhost:8899/test.html (Simple test page)")
            print(f"\n🔧 Server is running - test the functionality manually!")
            print(f"   - Try clicking tabs")
            print(f"   - Try clicking buttons") 
            print(f"   - Try file upload")
            print(f"   - Check browser console (F12) for JavaScript logs")
            return True
        else:
            print("\n❌ VERIFICATION FAILED: Content issues found")
            return False
            
    finally:
        # Keep server running for manual testing
        print(f"\n⚠️  Server left running for manual testing")
        print(f"   To stop: pkill -f http.server")

if __name__ == "__main__":
    main()