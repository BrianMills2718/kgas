#!/usr/bin/env python3
"""Fix tool IDs to match test expectations."""

import os
import re

# Mapping of file patterns to expected tool IDs
TOOL_ID_MAPPINGS = {
    't01_pdf_loader_unified.py': 'T01_PDF_LOADER',
    't02_word_loader_unified.py': 'T02_WORD_LOADER',
    't03_text_loader_unified.py': 'T03_TEXT_LOADER',
    't04_markdown_loader_unified.py': 'T04_MARKDOWN_LOADER',
    't05_csv_loader_unified.py': 'T05_CSV_LOADER',
    't06_json_loader_unified.py': 'T06_JSON_LOADER',
    't07_html_loader_unified.py': 'T07_HTML_LOADER',
    't08_xml_loader_unified.py': 'T08_XML_LOADER',
    't09_yaml_loader_unified.py': 'T09_YAML_LOADER',
    't10_excel_loader_unified.py': 'T10_EXCEL_LOADER',
    't11_powerpoint_loader_unified.py': 'T11_POWERPOINT_LOADER',
    't12_zip_loader_unified.py': 'T12_ZIP_LOADER',
    't13_web_scraper_unified.py': 'T13_WEB_SCRAPER',
    't14_email_parser_unified.py': 'T14_EMAIL_PARSER',
    't15a_text_chunker_unified.py': 'T15A_TEXT_CHUNKER',
    't15b_vector_embedder.py': 'T15B_VECTOR_EMBEDDER',
    't23a_spacy_ner_unified.py': 'T23A_SPACY_NER',
    't27_relationship_extractor_unified.py': 'T27_RELATIONSHIP_EXTRACTOR',
    't31_entity_builder_unified.py': 'T31_ENTITY_BUILDER',
    't34_edge_builder_unified.py': 'T34_EDGE_BUILDER',
    't49_multihop_query_unified.py': 'T49_MULTIHOP_QUERY',
    't68_pagerank_unified.py': 'T68_PAGERANK',
}

def fix_tool_id(filepath, expected_id):
    """Fix tool ID in a file."""
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Pattern to match tool_id assignment
    pattern = r'self\.tool_id\s*=\s*"[^"]*"'
    replacement = f'self.tool_id = "{expected_id}"'
    
    new_content = re.sub(pattern, replacement, content)
    
    if new_content != content:
        with open(filepath, 'w') as f:
            f.write(new_content)
        return True
    return False

def main():
    """Fix all tool IDs."""
    phase1_dir = 'src/tools/phase1'
    fixed_count = 0
    
    for filename, expected_id in TOOL_ID_MAPPINGS.items():
        filepath = os.path.join(phase1_dir, filename)
        if os.path.exists(filepath):
            if fix_tool_id(filepath, expected_id):
                print(f"Fixed {filename}: {expected_id}")
                fixed_count += 1
            else:
                print(f"Already correct: {filename}")
        else:
            print(f"Not found: {filename}")
    
    print(f"\nFixed {fixed_count} files")

if __name__ == "__main__":
    main()