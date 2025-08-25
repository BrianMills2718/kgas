#!/usr/bin/env python3
"""
Direct test using the actual model names
"""

from litellm import completion
from dotenv import load_dotenv

load_dotenv()

# Test directly with litellm
try:
    response = completion(
        model="gemini/gemini-2.5-flash",
        messages=[{"role": "user", "content": "Say hello!"}]
    )
    print(f"Success! Response: {response.choices[0].message.content}")
except Exception as e:
    print(f"Error: {e}")

# Test o4-mini
try:
    response = completion(
        model="o4-mini",
        messages=[{"role": "user", "content": "Say hello!"}]
    )
    print(f"Success! o4-mini Response: {response.choices[0].message.content}")
except Exception as e:
    print(f"o4-mini Error: {e}")

# Test Claude
try:
    response = completion(
        model="claude-sonnet-4-20250514",
        messages=[{"role": "user", "content": "Say hello!"}]
    )
    print(f"Success! Claude Response: {response.choices[0].message.content}")
except Exception as e:
    print(f"Claude Error: {e}")