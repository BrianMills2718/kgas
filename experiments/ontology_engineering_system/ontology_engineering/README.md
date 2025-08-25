BORO_1.py is the main file for the BORO analysis.

    # BORO Analysis Tool

    A Streamlit-based application that implements the Business Object Reference Ontology (BORO) decision tree methodology for analyzing and visualizing conceptual relationships.

    ## Overview

    The BORO Analysis Tool helps users understand and visualize how concepts are related by categorizing them into:

    - **Individuals**: Physical objects that exist in space and time (e.g., "John's car")
    - **Types**: Categories that have members/instances (e.g., "Car" as a category)
    - **Tuples**: Relationships between entities (e.g., "Car Ownership")

  
    ## Usage

    1. Enter a concept in the input field (e.g., "Car", "Customer Account", "Sales Process")
    2. Click "Run BORO Analysis"
    3. The tool will:
    - Recursively analyze the concept
    - Create a visual graph of relationships
    - Display statistics about the analysis

    ## Features

    - Interactive network visualization
    - Real-time analysis statistics
    - Color-coded concept types:
    - Green: Individuals
    - Blue: Types
    - Red: Tuples
    - Export functionality for analysis results

    ## Applications

    The tool is useful for:
    - Business Process Modeling
    - Data Architecture Design
    - Knowledge Management
    - System Integration Planning
    - Requirements Analysis

    ## Example Analysis

    Input: "Car"
