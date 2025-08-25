#!/usr/bin/env python3
"""
Run validation with environment variables loaded from .env file
"""

import os
import sys
from pathlib import Path

# Load environment variables from .env file
def load_env():
    env_path = Path("/home/brian/projects/Digimons/.env")
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

# Load environment variables
load_env()

# Now run the validation
from run_gemini_validation import main
import asyncio

if __name__ == "__main__":
    asyncio.run(main())