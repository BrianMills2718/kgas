#!/usr/bin/env python3
"""Debug regex patterns"""

import re

text2 = "Microsoft Corporation was founded by Bill Gates and Paul Allen in 1975."
text3 = "Google competes with Microsoft and Apple in cloud services."

# Test Pattern 3
print("Testing Pattern 3 (founded by):")
print(f"Text: {text2}")

patterns = [
    r"([^,]+)\s+was founded by\s+([^\.]+?)(?:\s+in\s+\d{4})?\.?",  # Current
    r"([^,]+)\s+was founded by\s+(.+?)(?:\s+in\s+\d{4})",           # Alternative 1
    r"([^,]+)\s+was founded by\s+([^\.]+)",                         # Alternative 2
]

for i, pattern in enumerate(patterns, 1):
    print(f"\nPattern {i}: {pattern}")
    for match in re.finditer(pattern, text2, re.IGNORECASE):
        print(f"  Group 1 (org): '{match.group(1)}'")
        print(f"  Group 2 (founders): '{match.group(2)}'")

# Test Pattern 4
print("\n" + "="*50)
print("Testing Pattern 4 (competes with):")
print(f"Text: {text3}")

patterns = [
    r"([^,]+)\s+competes with\s+([^\.]+?)(?:\s+in\s+[^\.]+)?\.?",  # Current
    r"([^,]+)\s+competes with\s+(.+?)(?:\s+in\s+)",                # Alternative 1
    r"([^,]+)\s+competes with\s+([^\.]+)",                         # Alternative 2
]

for i, pattern in enumerate(patterns, 1):
    print(f"\nPattern {i}: {pattern}")
    for match in re.finditer(pattern, text3, re.IGNORECASE):
        print(f"  Group 1 (company): '{match.group(1)}'")
        print(f"  Group 2 (competitors): '{match.group(2)}'")

# Test what the non-greedy ? is doing
print("\n" + "="*50)
print("Understanding non-greedy matching:")

test_string = "competes with Microsoft and Apple in cloud"
patterns = [
    (r"competes with\s+(.+?)(?:\s+in\s+)", "Non-greedy with lookahead"),
    (r"competes with\s+([^\.]+?)(?:\s+in\s+)", "Non-greedy [^\\.] with lookahead"),
    (r"competes with\s+(.+)\s+in\s+", "Greedy with in"),
    (r"competes with\s+([^i]+)", "Until 'i'"),
]

for pattern, desc in patterns:
    print(f"\n{desc}: {pattern}")
    match = re.search(pattern, test_string, re.IGNORECASE)
    if match:
        print(f"  Captured: '{match.group(1)}'")
    else:
        print(f"  No match")