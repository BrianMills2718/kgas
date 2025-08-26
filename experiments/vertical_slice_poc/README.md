# Vertical Slice POC - Quick Start

## Purpose
Prove that knowledge graph extraction with uncertainty propagation works BEFORE building complex frameworks.

## Setup

1. **Install dependencies**:
```bash
cd experiments/vertical_slice_poc
pip install -r requirements.txt
```

2. **Configure API keys** in `/home/brian/projects/Digimons/.env`:
```
GEMINI_API_KEY=your_gemini_key
OPENAI_API_KEY=your_openai_key  # optional
NEO4J_PASSWORD=devpassword
```

3. **Start Neo4j** (if not running):
```bash
docker run -d --name neo4j \
  -p 7687:7687 -p 7474:7474 \
  -e NEO4J_AUTH=neo4j/devpassword \
  neo4j:latest
```

4. **Verify configuration**:
```bash
python config.py
```

## Experiments

### 01 - Basic Extraction
```bash
cd 01_basic_extraction
python extract_kg.py
```

### 02 - Neo4j Persistence
```bash
cd 02_neo4j_persistence
python persist_to_neo4j.py
```

### 03 - Uncertainty Testing
```bash
cd 03_uncertainty_test
python extract_with_uncertainty.py
```

### 04 - Framework Integration
Only after 1-3 work!

## Key Files

- `CLAUDE.md` - Detailed plan and documentation
- `config.py` - All configuration in one place
- Each experiment has its own README with specific instructions

## Remember

**We're proving concepts, not building production code!**

Start simple, make it work, then make it better.