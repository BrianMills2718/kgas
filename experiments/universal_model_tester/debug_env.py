#!/usr/bin/env python3
"""
Debug environment variable loading
"""

import os
from dotenv import load_dotenv

load_dotenv()

print("Environment variables:")
for key in ['GEMINI_2_5_FLASH', 'O4_MINI', 'CLAUDE_SONNET_4']:
    value = os.getenv(key)
    print(f"{key}: {value}")

print("\nAll environment variables starting with GEMINI/O4/CLAUDE:")
for key, value in os.environ.items():
    if any(key.startswith(prefix) for prefix in ['GEMINI', 'O4', 'CLAUDE']):
        print(f"{key}: {value}")