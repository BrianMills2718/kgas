#!/usr/bin/env python3
"""
Simple test launcher for Phase D.4 Dashboard Tests
"""

import warnings
import logging
import sys

# Suppress Streamlit warnings
warnings.filterwarnings("ignore", category=UserWarning)
logging.getLogger('streamlit').setLevel(logging.ERROR)

# Import and run tests
from tests.test_enhanced_dashboard import run_all_tests

if __name__ == "__main__":
    try:
        evidence = run_all_tests()
        print("\n✅ Phase D.4 Dashboard Tests Completed Successfully!")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Phase D.4 Dashboard Tests Failed: {e}")
        sys.exit(1)