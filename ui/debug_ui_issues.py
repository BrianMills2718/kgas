#!/usr/bin/env python3
"""
Debug UI Issues
Helps identify what's causing the UI loading problems
"""

import os
import sys
from pathlib import Path
import requests
import subprocess
import time

def check_html_files():
    """Check all HTML files in the UI directory"""
    print("🔍 Checking HTML files...")
    
    ui_dir = Path('ui')
    html_files = list(ui_dir.glob('*.html'))
    
    print(f"Found {len(html_files)} HTML files:")
    for html_file in html_files:
        size = html_file.stat().st_size
        print(f"  - {html_file.name}: {size:,} bytes")
        
        # Check for common issues
        content = html_file.read_text()
        
        # Check for basic structure
        if '<!DOCTYPE html>' not in content:
            print(f"    ⚠️  Missing DOCTYPE in {html_file.name}")
        if '<html' not in content:
            print(f"    ⚠️  Missing <html> tag in {html_file.name}")
        if '</html>' not in content:
            print(f"    ⚠️  Missing closing </html> tag in {html_file.name}")
        if '<head>' not in content:
            print(f"    ⚠️  Missing <head> tag in {html_file.name}")
        if '<body>' not in content:
            print(f"    ⚠️  Missing <body> tag in {html_file.name}")
            
        # Check for scripts that might cause issues
        if 'while(' in content or 'while (' in content:
            print(f"    ⚠️  Potential infinite loop in {html_file.name}")
        if 'setInterval' in content:
            print(f"    ℹ️  Uses setInterval in {html_file.name}")
        if 'setTimeout' in content:
            print(f"    ℹ️  Uses setTimeout in {html_file.name}")
            
    return html_files

def test_server_startup():
    """Test if server can start"""
    print("\n🚀 Testing server startup...")
    
    # Try different ports
    for port in [8899, 8888, 8890, 9000]:
        print(f"Trying port {port}...")
        
        # Start server process
        try:
            process = subprocess.Popen(
                ['python3', '-m', 'http.server', str(port)],
                cwd='ui',
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Wait a moment
            time.sleep(2)
            
            # Test if it's accessible
            try:
                response = requests.get(f'http://localhost:{port}/', timeout=3)
                print(f"  ✅ Port {port} works! Status: {response.status_code}")
                
                # Test specific file
                response = requests.get(f'http://localhost:{port}/simple_working_ui.html', timeout=3)
                print(f"  ✅ simple_working_ui.html accessible: {response.status_code}")
                
                process.terminate()
                return port
                
            except requests.exceptions.RequestException as e:
                print(f"  ❌ Port {port} not accessible: {e}")
                process.terminate()
                
        except Exception as e:
            print(f"  ❌ Failed to start server on port {port}: {e}")
            
    print("❌ No working ports found")
    return None

def analyze_html_content():
    """Analyze HTML content for issues"""
    print("\n🔍 Analyzing HTML content...")
    
    simple_ui = Path('ui/simple_working_ui.html')
    if simple_ui.exists():
        content = simple_ui.read_text()
        
        print(f"File size: {len(content):,} characters")
        print(f"Line count: {len(content.splitlines())}")
        
        # Look for potential issues
        issues = []
        
        if content.count('<script>') != content.count('</script>'):
            issues.append("Unmatched <script> tags")
            
        if content.count('<style>') != content.count('</style>'):
            issues.append("Unmatched <style> tags")
            
        if 'console.error' in content.lower():
            issues.append("Contains console.error calls")
            
        if 'throw ' in content:
            issues.append("Contains throw statements")
            
        if issues:
            print("⚠️  Potential issues found:")
            for issue in issues:
                print(f"    - {issue}")
        else:
            print("✅ No obvious issues found in HTML")
            
        # Extract and validate JavaScript
        import re
        scripts = re.findall(r'<script[^>]*>(.*?)</script>', content, re.DOTALL)
        print(f"Found {len(scripts)} script blocks")
        
        for i, script in enumerate(scripts):
            if script.strip():
                print(f"  Script {i+1}: {len(script)} characters")
                # Check for syntax issues
                if script.count('(') != script.count(')'):
                    print(f"    ⚠️  Unmatched parentheses in script {i+1}")
                if script.count('{') != script.count('}'):
                    print(f"    ⚠️  Unmatched braces in script {i+1}")
                    
    else:
        print("❌ simple_working_ui.html not found")

def create_minimal_test_html():
    """Create the most minimal working HTML for testing"""
    print("\n🛠️  Creating minimal test HTML...")
    
    minimal_html = """<!DOCTYPE html>
<html>
<head>
    <title>Minimal Test</title>
</head>
<body>
    <h1>✅ UI Loading Test</h1>
    <p>If you can see this, the basic HTML loading works!</p>
    <button onclick="alert('JavaScript works!')">Test JS</button>
</body>
</html>"""
    
    Path('ui/minimal_test.html').write_text(minimal_html)
    print("✅ Created ui/minimal_test.html")

def main():
    """Main debug function"""
    print("🐛 KGAS UI Debug Tool")
    print("=" * 50)
    
    # Check HTML files
    html_files = check_html_files()
    
    # Test server
    working_port = test_server_startup()
    
    # Analyze content
    analyze_html_content()
    
    # Create minimal test
    create_minimal_test_html()
    
    print("\n" + "=" * 50)
    print("🎯 DEBUG SUMMARY")
    print("=" * 50)
    
    if working_port:
        print(f"✅ Server can start on port {working_port}")
        print(f"\n📋 Try these URLs:")
        print(f"  1. http://localhost:{working_port}/minimal_test.html (minimal test)")
        print(f"  2. http://localhost:{working_port}/simple_working_ui.html (full UI)")
        print(f"\n🚀 To start server:")
        print(f"  cd ui && python3 -m http.server {working_port}")
    else:
        print("❌ Could not start server - check port conflicts")
        
    print(f"\n📄 HTML files checked: {len(html_files)}")

if __name__ == "__main__":
    main()