#!/bin/bash
# Run the knowledge graph extraction experiment

echo "================================"
echo "Knowledge Graph Extraction Test"
echo "================================"

# Check if config is valid
echo "Checking configuration..."
cd ..
python -c "import config; config.validate_config()" || exit 1

# Run extraction
echo ""
echo "Running extraction..."
cd 01_basic_extraction
python extract_kg.py

# Check if output was created
if [ -f "outputs/extraction_result.json" ]; then
    echo ""
    echo "Output created successfully!"
    echo "Checking JSON validity..."
    python -m json.tool outputs/extraction_result.json > /dev/null
    if [ $? -eq 0 ]; then
        echo "✅ Valid JSON output"
    else
        echo "❌ Invalid JSON output"
    fi
else
    echo "❌ No output file created"
fi