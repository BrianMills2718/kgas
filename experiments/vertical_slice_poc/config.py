"""
Configuration for vertical slice POC experiments
Central place for all settings - no magic numbers buried in code
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from project root
project_root = Path(__file__).parent.parent.parent
env_file = project_root / '.env'
load_dotenv(env_file)

# ============================================
# LLM Configuration
# ============================================

# Choose provider: "openai", "anthropic", or "google"
LLM_PROVIDER = "google"  # Starting with Gemini like in existing experiments

# Model selection
LLM_MODELS = {
    "openai": "gpt-4-turbo-preview",
    "anthropic": "claude-3-opus-20240229",
    "google": "gemini-1.5-flash"  # Updated to available model
}

LLM_MODEL = LLM_MODELS[LLM_PROVIDER]

# API Keys
API_KEYS = {
    "openai": os.getenv("OPENAI_API_KEY"),
    "anthropic": os.getenv("ANTHROPIC_API_KEY"),
    "google": os.getenv("GEMINI_API_KEY")
}

API_KEY = API_KEYS[LLM_PROVIDER]

# ============================================
# Neo4j Configuration
# ============================================

NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "devpassword")  # Default from existing code

# ============================================
# SQLite Configuration
# ============================================

SQLITE_PATH = str(Path(__file__).parent / "vertical_slice.db")

# ============================================
# Uncertainty Constants
# ============================================

# TextLoader uncertainty by file type (configurable, not buried in code)
TEXT_UNCERTAINTY = {
    "pdf": 0.15,    # OCR challenges, formatting loss
    "txt": 0.02,    # Nearly perfect extraction
    "docx": 0.08,   # Some formatting complexity
    "html": 0.12,   # Tag stripping, structure loss
    "md": 0.03,     # Clean markdown extraction
    "json": 0.01,   # Structured data, minimal loss
    "default": 0.10 # Unknown formats
}

# Reasoning templates for each file type
TEXT_UNCERTAINTY_REASONING = {
    "pdf": "PDF extraction may have OCR errors or formatting loss",
    "txt": "Plain text extraction with minimal uncertainty",
    "docx": "Word document with potential formatting complexity",
    "html": "HTML parsing may lose semantic structure",
    "md": "Markdown extraction preserves structure well",
    "json": "Structured data extraction with minimal loss",
    "default": "Standard uncertainty for unknown file format"
}

# ============================================
# Extraction Configuration
# ============================================

# Chunking parameters
CHUNK_SIZE = 4000  # Characters per chunk
CHUNK_OVERLAP = 200  # Overlap between chunks

# Extraction parameters
MAX_ENTITIES_PER_CHUNK = 50  # Prevent runaway extraction
MAX_RELATIONSHIPS_PER_CHUNK = 100

# Schema mode: "open", "closed", or "hybrid"
SCHEMA_MODE = "open"  # Start with open schema as discussed

# ============================================
# Test Data Configuration
# ============================================

TEST_DOCUMENTS = {
    "simple": "01_basic_extraction/test_documents/simple_news.txt",
    "complex": "01_basic_extraction/test_documents/complex_academic.pdf",
    "long": "01_basic_extraction/test_documents/long_report.txt"
}

# ============================================
# Logging Configuration
# ============================================

LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR
LOG_FILE = "experiments.log"

# ============================================
# Validation Thresholds
# ============================================

# What's acceptable uncertainty for each operation?
MAX_ACCEPTABLE_UNCERTAINTY = {
    "text_extraction": 0.20,
    "kg_extraction": 0.35,
    "graph_persistence": 0.01,  # Should be near zero
    "pipeline_total": 0.45
}

# ============================================
# Helper Functions
# ============================================

def get_llm_client():
    """Get the appropriate LLM client based on configuration"""
    if LLM_PROVIDER == "openai":
        from openai import OpenAI
        return OpenAI(api_key=API_KEY)
    elif LLM_PROVIDER == "anthropic":
        from anthropic import Anthropic
        return Anthropic(api_key=API_KEY)
    elif LLM_PROVIDER == "google":
        import google.generativeai as genai
        genai.configure(api_key=API_KEY)
        return genai.GenerativeModel(LLM_MODEL)
    else:
        raise ValueError(f"Unknown LLM provider: {LLM_PROVIDER}")

def get_neo4j_driver():
    """Get Neo4j driver with proper error handling"""
    from neo4j import GraphDatabase
    from neo4j.exceptions import ServiceUnavailable
    
    try:
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
        # Test connection
        driver.verify_connectivity()
        return driver
    except ServiceUnavailable:
        raise ConnectionError(
            f"Cannot connect to Neo4j at {NEO4J_URI}. "
            "Make sure Neo4j is running: docker run -d -p 7687:7687 -p 7474:7474 "
            "-e NEO4J_AUTH=neo4j/devpassword neo4j"
        )

def validate_config():
    """Validate configuration on import"""
    errors = []
    
    if not API_KEY:
        errors.append(f"No API key found for {LLM_PROVIDER}. Set {LLM_PROVIDER.upper()}_API_KEY in .env")
    
    if not Path(project_root / '.env').exists():
        errors.append(f"No .env file found at {project_root}. Create one with your API keys.")
    
    if errors:
        print("Configuration Errors:")
        for error in errors:
            print(f"  - {error}")
        print("\nCreate a .env file with:")
        print("  GEMINI_API_KEY=your_key_here")
        print("  NEO4J_PASSWORD=your_password_here")
    
    return len(errors) == 0

# Validate on import
if __name__ == "__main__":
    if validate_config():
        print("✅ Configuration valid")
        print(f"  LLM: {LLM_PROVIDER} / {LLM_MODEL}")
        print(f"  Neo4j: {NEO4J_URI}")
        print(f"  SQLite: {SQLITE_PATH}")
    else:
        print("❌ Configuration invalid - see errors above")