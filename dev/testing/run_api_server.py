#!/usr/bin/env python3
"""
Run the KGAS Cross-Modal REST API Server

This starts a local-only REST API server for cross-modal analysis operations.
The server provides endpoints for:
- Document analysis
- Format conversion (Graph ↔ Table ↔ Vector)
- Mode recommendation
- Batch processing

Usage:
    python run_api_server.py [--port PORT] [--reload]

The API will be available at:
    http://localhost:8000
    
API Documentation:
    http://localhost:8000/api/docs (Swagger UI)
    http://localhost:8000/api/redoc (ReDoc)

Security Note:
    This server binds to localhost only. It is not accessible from other machines.
    This is intentional for security - all processing stays local.
"""

import argparse
import logging
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

import uvicorn
from src.api.cross_modal_api import app

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Main entry point for the API server"""
    parser = argparse.ArgumentParser(
        description="Run the KGAS Cross-Modal REST API Server"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to run the server on (default: 8000)"
    )
    parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable auto-reload for development"
    )
    parser.add_argument(
        "--log-level",
        choices=["debug", "info", "warning", "error"],
        default="info",
        help="Logging level (default: info)"
    )
    
    args = parser.parse_args()
    
    # Validate environment
    logger.info("🚀 Starting KGAS Cross-Modal REST API Server")
    logger.info(f"📍 Server will be available at: http://localhost:{args.port}")
    logger.info(f"📚 API Documentation: http://localhost:{args.port}/api/docs")
    logger.info(f"📖 Alternative docs: http://localhost:{args.port}/api/redoc")
    
    # Check for API keys if needed
    if not os.getenv("OPENAI_API_KEY") and not os.getenv("ANTHROPIC_API_KEY"):
        logger.warning("⚠️  No LLM API keys found. Mode recommendation will be limited.")
        logger.warning("   Set OPENAI_API_KEY or ANTHROPIC_API_KEY for full functionality.")
    
    # Security reminder
    logger.info("🔒 Security: Server bound to localhost only (not accessible externally)")
    
    try:
        # Run the server
        uvicorn.run(
            "src.api.cross_modal_api:app",
            host="127.0.0.1",  # Localhost only for security
            port=args.port,
            reload=args.reload,
            log_level=args.log_level
        )
    except KeyboardInterrupt:
        logger.info("⏹️  Server shutdown requested")
    except Exception as e:
        logger.error(f"❌ Server failed to start: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()