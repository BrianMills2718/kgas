# Data Directory

This directory contains all data files, databases, logs, and outputs organized by type.

## Directory Structure

### Databases (`/databases/`)
System databases and data stores:
- `demo_kgas.db` - Demo KGAS database
- `kunst_data.db` - Kunst dataset analysis database  
- `provenance.db` - System provenance tracking database

### Datasets (`/datasets/`)
Original datasets and research data:
- `kunst_dataset/` - Complete Kunst conspiracy theory research dataset

### Outputs (`/outputs/`)
Generated outputs from system operations:
- `demo_output/` - Demo execution results
- `demo_results/` - Demo result summaries
- `kgas_agent_demo_results/` - KGAS agent demonstration outputs
- `kunst_demo_results/` - Kunst analysis demonstration results
- `kunst_visualizations/` - Generated visualizations for Kunst dataset
- `kunst_carter_analysis/` - Carter-Kunst comparative analysis results
- `performance_data.json` - System performance metrics
- `sla_config.json` - Service level agreement configuration

### Research Data (`/research/`)
Research datasets and analysis materials:
- `paul_davis_notes/` - Research notes from Paul Davis analysis
- `kunst_conspiracy_theory/` - Kunst conspiracy theory schema data
- `kunst_paper.txt` - Original Kunst research paper text

### Test Data (`/test_data/`)
Test files and sample data:
- PDF documents for testing document processing
- Sample text files for analysis
- Enhanced test documents

### Logs (`/logs/`)
System logs and execution traces:
- `super_digimon.log` - Main system log
- `super_digimon.rotating.log` - Rotating system log

### Tool Registry (`/tool_registry.json`)
System tool registry configuration

## Usage Notes

- **Databases**: Neo4j and SQLite databases for different system components
- **Outputs**: All generated content from demos, analyses, and visualizations  
- **Research**: Original research materials and derived analysis
- **Test Data**: Sample files for system testing and validation
- **Logs**: System execution logs for debugging and monitoring

## Related Directories

- Generated content: [../generated/](../generated/)
- Evidence files: [../evidence/](../evidence/)
- Source code: [../src/](../src/)

---

*This directory consolidates all data files that were previously scattered across the repository.*