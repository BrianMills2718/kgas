#!/usr/bin/env python3
"""Test that pandas-dependent tools can now be imported."""

import sys
sys.path.append('/home/brian/projects/Digimons')

success_count = 0
failed = []

# Test CrossModalConverter
try:
    from src.analytics.cross_modal_converter import CrossModalConverter
    converter = CrossModalConverter()
    print("✅ CrossModalConverter imported successfully")
    success_count += 1
except Exception as e:
    failed.append(f"CrossModalConverter: {e}")
    print(f"❌ CrossModalConverter failed: {e}")

# Test GraphTableExporter  
try:
    from src.tools.cross_modal.graph_table_exporter import GraphTableExporter
    exporter = GraphTableExporter()
    print("✅ GraphTableExporter imported successfully")
    success_count += 1
except Exception as e:
    failed.append(f"GraphTableExporter: {e}")
    print(f"❌ GraphTableExporter failed: {e}")

# Test MultiFormatExporter
try:
    from src.tools.cross_modal.multi_format_exporter import MultiFormatExporter
    multi_exporter = MultiFormatExporter()
    print("✅ MultiFormatExporter imported successfully")
    success_count += 1
except Exception as e:
    failed.append(f"MultiFormatExporter: {e}")
    print(f"❌ MultiFormatExporter failed: {e}")

print(f"\nResult: {success_count}/3 tools now working")
sys.exit(0 if success_count == 3 else 1)