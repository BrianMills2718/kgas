#!/usr/bin/env python3
"""
Simple test to debug the universal model client
"""

from universal_model_client import UniversalModelClient
import logging

logging.basicConfig(level=logging.DEBUG, format='%(name)s - %(levelname)s - %(message)s')

def main():
    client = UniversalModelClient()
    
    print("Available models:")
    for name, config in client.models.items():
        print(f"  {name}: {config.litellm_name}")
    
    print(f"\nPrimary model: {client.fallback_config['primary_model']}")
    print(f"Fallback models: {client.fallback_config['fallback_models']}")
    
    # Test simple completion
    try:
        result = client.complete(
            messages=[{"role": "user", "content": "Say hello!"}]
        )
        print(f"\nSuccess! Model used: {result['model_used']}")
        print(f"Response: {result['response'].choices[0].message.content}")
    except Exception as e:
        print(f"\nError: {e}")

if __name__ == "__main__":
    main()