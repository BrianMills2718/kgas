#!/usr/bin/env python3
"""Single script to verify everything is ready"""
import sys
import os

def check_all():
    errors = []
    
    # Check location
    if not os.path.exists('framework/clean_framework.py'):
        errors.append("Wrong directory - must be in vertical_slice/")
    
    # Check Neo4j
    try:
        from neo4j import GraphDatabase
        driver = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', 'devpassword'))
        driver.verify_connectivity()
        driver.close()
    except:
        errors.append("Neo4j not running - run: sudo systemctl start neo4j")
    
    # Check dependencies
    try:
        import openai
        import pandas
        import numpy
        import litellm
        from dotenv import load_dotenv
    except ImportError as e:
        errors.append(f"Missing package: {e} - run: pip install openai pandas numpy litellm python-dotenv")
    
    # Check API keys
    sys.path.append('/home/brian/projects/Digimons')
    from dotenv import load_dotenv
    load_dotenv('/home/brian/projects/Digimons/.env')
    
    if not os.getenv('OPENAI_API_KEY'):
        errors.append("OPENAI_API_KEY not set in .env")
    if not os.getenv('GEMINI_API_KEY'):
        errors.append("GEMINI_API_KEY not set in .env")
    
    # Report
    if errors:
        print("❌ Setup problems found:")
        for error in errors:
            print(f"  - {error}")
        return False
    else:
        print("✅ All checks passed - ready to proceed")
        return True

if __name__ == "__main__":
    if not check_all():
        sys.exit(1)