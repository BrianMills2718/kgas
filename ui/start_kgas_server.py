#!/usr/bin/env python3
"""
KGAS Server Startup Script
Starts the complete KGAS web server with all backend functionality
"""

import sys
import subprocess
import time
import requests
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed"""
    print("🔍 Checking dependencies...")
    
    required_packages = [
        'fastapi',
        'uvicorn',
        'python-multipart',
        'pydantic'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"  ✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"  ❌ {package}")
    
    if missing_packages:
        print(f"\n📦 Installing missing packages: {', '.join(missing_packages)}")
        try:
            subprocess.check_call([
                sys.executable, '-m', 'pip', 'install'
            ] + missing_packages)
            print("✅ Dependencies installed successfully!")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install dependencies: {e}")
            return False
    else:
        print("✅ All dependencies are available!")
    
    return True

def setup_directories():
    """Setup required directories"""
    print("📁 Setting up directories...")
    
    directories = [
        Path("ui/uploads"),
        Path("ui/exports")
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        print(f"  ✅ {directory}")
    
    print("✅ Directories ready!")

def check_kgas_backend():
    """Check if KGAS backend components are available"""
    print("🔧 Checking KGAS backend components...")
    
    try:
        # Try to import KGAS modules
        from src.core.service_manager import ServiceManager
        from src.tools.phase1.t01_pdf_loader_unified import T01PDFLoaderUnified
        print("  ✅ KGAS core modules available")
        
        # Try to initialize service manager
        service_manager = ServiceManager()
        print("  ✅ Service manager initialized")
        
        return True, "Full KGAS backend available"
        
    except ImportError as e:
        print(f"  ⚠️ KGAS modules not available: {e}")
        return False, "Running in mock mode (UI features work, but with simulated data)"

def start_server():
    """Start the KGAS web server"""
    print("🚀 Starting KGAS Web Server...")
    
    try:
        # Start the server
        process = subprocess.Popen([
            sys.executable, 'ui/kgas_web_server.py'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait a moment for server to start
        time.sleep(3)
        
        # Test if server is responding
        try:
            response = requests.get('http://localhost:8899/', timeout=5)
            if response.status_code == 200:
                print("✅ Server started successfully!")
                print("\n🌟 KGAS Research UI is now running!")
                print("📡 Server: http://localhost:8899")
                print("🔗 UI: http://localhost:8899/")
                print("\n🎯 Features available:")
                print("  • Real file upload and processing")
                print("  • Complete analysis pipeline")
                print("  • Natural language queries")
                print("  • Multiple export formats")
                print("  • Graph visualization")
                print("\n💡 To stop the server, press Ctrl+C")
                
                # Keep the process running
                try:
                    process.wait()
                except KeyboardInterrupt:
                    print("\n🛑 Shutting down server...")
                    process.terminate()
                    process.wait()
                    print("✅ Server stopped.")
                
            else:
                print(f"❌ Server not responding properly (HTTP {response.status_code})")
                process.terminate()
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Cannot connect to server: {e}")
            process.terminate()
            return False
            
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        return False
    
    return True

def main():
    """Main startup function"""
    print("🔬 KGAS Research UI - Complete Backend Integration")
    print("=" * 60)
    
    # Check dependencies
    if not check_dependencies():
        print("❌ Dependency check failed. Exiting.")
        return False
    
    # Setup directories
    setup_directories()
    
    # Check KGAS backend
    backend_available, backend_message = check_kgas_backend()
    print(f"🔧 Backend Status: {backend_message}")
    
    if not backend_available:
        print("\n⚠️ Note: Running in mock mode.")
        print("   UI functionality will work with simulated data.")
        print("   For full functionality, ensure KGAS backend is properly installed.")
    
    # Start server
    print("\n" + "=" * 60)
    success = start_server()
    
    if not success:
        print("❌ Server startup failed.")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)