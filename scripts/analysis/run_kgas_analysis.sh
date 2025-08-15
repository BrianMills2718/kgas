#!/bin/bash
# KGAS Analysis using Claude Code as Agent Brain
# This script demonstrates practical usage of Claude Code with KGAS MCP tools

set -e

echo "🚀 KGAS Analysis with Claude Code"
echo "=================================="

# Step 1: Ensure KGAS MCP server is configured
echo "📋 Step 1: Checking KGAS MCP configuration..."
if ! claude mcp list | grep -q "kgas"; then
    echo "   Adding KGAS MCP server..."
    claude mcp add kgas python /home/brian/projects/Digimons/kgas_mcp_server.py
else
    echo "   ✓ KGAS MCP server already configured"
fi

# Step 2: Create analysis prompt
echo -e "\n📝 Step 2: Creating analysis prompt..."
cat > /tmp/kgas_analysis_prompt.txt << 'EOF'
I need you to perform a comprehensive analysis using KGAS tools and subagents.

**Documents to analyze:**
1. /home/brian/projects/Digimons/kunst_paper.txt - Academic paper on psychological factors
2. /home/brian/projects/Digimons/lit_review/data/test_texts/texts/carter_speech.txt - Political speech

**Research Objective:**
Apply the psychological conspiracy theory framework from the Kunst paper to analyze the Carter speech.

**Instructions:**

Please use subagents to parallelize this analysis:

**Subagent 1 - Theory Extraction:**
- Use mcp__kgas__load_pdf_document to load the Kunst paper
- Use mcp__kgas__chunk_text to process it
- Extract the theoretical framework, focusing on:
  - Psychological constructs (narcissism, denialism, etc.)
  - Relationships between constructs
  - Measurement approaches
- Create a structured theory schema

**Subagent 2 - Speech Analysis:**
- Use mcp__kgas__load_pdf_document to load the Carter speech
- Use mcp__kgas__chunk_text to segment it
- Use mcp__kgas__extract_entities_from_text on each chunk
- Identify rhetorical patterns and themes

**Subagent 3 - Theory Application:**
- Take the theory from Subagent 1 and speech analysis from Subagent 2
- Apply the psychological framework to the speech content
- Identify presence/absence of conspiracy-related factors
- Calculate risk scores based on the framework

**Subagent 4 - Knowledge Graph Construction:**
- Build a unified knowledge graph from all findings
- Use mcp__kgas__calculate_pagerank to identify central concepts
- Use mcp__kgas__query_graph to extract key insights

**Final Synthesis:**
After all subagents complete, synthesize the findings into:
1. Executive summary of the analysis
2. Detailed findings by psychological factor
3. Risk assessment with evidence
4. Knowledge graph visualization data
5. Recommendations for further analysis

Please execute this analysis now using the Task tool for subagents and KGAS MCP tools.
EOF

echo "   ✓ Analysis prompt created"

# Step 3: Execute analysis
echo -e "\n🔬 Step 3: Running KGAS analysis with Claude Code..."
echo "   This will:"
echo "   - Create 4 parallel subagents"
echo "   - Each subagent will use KGAS MCP tools"
echo "   - Results will be synthesized automatically"
echo ""

# Create output directory
OUTPUT_DIR="kgas_analysis_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$OUTPUT_DIR"

# Option 1: Interactive mode (user can see progress)
# claude --continue < /tmp/kgas_analysis_prompt.txt

# Option 2: Non-interactive mode with JSON output
echo "   Running in non-interactive mode..."
claude -p "$(cat /tmp/kgas_analysis_prompt.txt)" \
    --output-format json \
    --max-turns 15 \
    > "$OUTPUT_DIR/analysis_results.json"

# Step 4: Extract and format results
echo -e "\n📊 Step 4: Processing results..."
if [ -f "$OUTPUT_DIR/analysis_results.json" ]; then
    # Extract the main result text
    jq -r '.result' "$OUTPUT_DIR/analysis_results.json" > "$OUTPUT_DIR/analysis_report.md"
    
    # Extract metadata
    jq '{
        session_id: .session_id,
        duration_ms: .duration_ms,
        num_turns: .num_turns,
        total_cost_usd: .total_cost_usd
    }' "$OUTPUT_DIR/analysis_results.json" > "$OUTPUT_DIR/analysis_metadata.json"
    
    echo "   ✓ Results processed"
    echo ""
    echo "📁 Results saved to: $OUTPUT_DIR/"
    echo "   - analysis_report.md: Full analysis report"
    echo "   - analysis_results.json: Raw JSON output"
    echo "   - analysis_metadata.json: Execution metadata"
else
    echo "   ❌ Error: No results generated"
    exit 1
fi

# Step 5: Display summary
echo -e "\n📋 Analysis Summary:"
echo "===================="
if [ -f "$OUTPUT_DIR/analysis_metadata.json" ]; then
    echo "Session ID: $(jq -r .session_id "$OUTPUT_DIR/analysis_metadata.json")"
    echo "Duration: $(jq -r .duration_ms "$OUTPUT_DIR/analysis_metadata.json")ms"
    echo "Turns: $(jq -r .num_turns "$OUTPUT_DIR/analysis_metadata.json")"
    echo "Cost: $$(jq -r .total_cost_usd "$OUTPUT_DIR/analysis_metadata.json")"
fi

echo -e "\n✅ KGAS analysis complete!"
echo ""
echo "To view the full report:"
echo "  cat $OUTPUT_DIR/analysis_report.md"
echo ""
echo "To continue this analysis:"
echo "  claude --resume $(jq -r .session_id "$OUTPUT_DIR/analysis_metadata.json")"