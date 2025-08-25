#!/usr/bin/env python3
"""
Test environment loading directly
"""

import os
from dotenv import load_dotenv

load_dotenv()

# Test the exact code from the class
model_vars = [
    'GEMINI_2_5_PRO', 'GEMINI_2_5_FLASH', 'GEMINI_2_5_FLASH_LITE',
    'GPT_4_1', 'O4_MINI', 'O3',
    'CLAUDE_OPUS_4', 'CLAUDE_SONNET_4', 'CLAUDE_SONNET_3_7', 'CLAUDE_HAIKU_3_5'
]

models = {}
for var in model_vars:
    config_str = os.getenv(var)
    print(f"Loading {var}: {config_str}")
    if config_str:
        parts = config_str.split(',')
        if len(parts) >= 3:
            model_key = var.lower()
            print(f"  Adding {model_key}")
            models[model_key] = {
                'name': model_key,
                'litellm_name': parts[0],
                'supports_structured_output': parts[1].lower() == 'true',
                'max_tokens': int(parts[2])
            }

print(f"\nTotal models: {len(models)}")
for key, model in models.items():
    print(f"  {key}: {model['litellm_name']}")