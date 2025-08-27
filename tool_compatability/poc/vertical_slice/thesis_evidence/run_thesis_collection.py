#!/usr/bin/env python3
"""
Main runner script for thesis evidence collection
Executes the complete pipeline and generates all outputs
"""

import sys
import os

def main():
    print("""
╔══════════════════════════════════════════════════════════════╗
║           KGAS THESIS EVIDENCE COLLECTION SYSTEM            ║
║                                                              ║
║  This will:                                                 ║
║  1. Generate ground truth documents (if needed)             ║
║  2. Run KGAS pipeline on each document                      ║
║  3. Collect performance metrics                             ║
║  4. Generate LaTeX tables for thesis                        ║
║  5. Create visualizations showing results                   ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    # Step 1: Check if ground truth exists
    ground_truth_dir = "/home/brian/projects/Digimons/tool_compatability/poc/vertical_slice/thesis_evidence/ground_truth_data"
    
    if not os.path.exists(ground_truth_dir):
        print("📝 Step 1: Generating ground truth dataset...")
        from ground_truth_generator import GroundTruthGenerator
        generator = GroundTruthGenerator(output_dir=ground_truth_dir)
        documents = generator.generate_all_documents()
        print(f"✅ Generated {len(documents)} ground truth documents\n")
    else:
        print("✅ Ground truth dataset already exists\n")
    
    # Step 2: Run evidence collection
    print("🔬 Step 2: Running KGAS pipeline on documents...")
    print("(This may take several minutes...)\n")
    
    from evidence_collector import ThesisEvidenceCollector
    
    collector = ThesisEvidenceCollector(
        ground_truth_dir=ground_truth_dir,
        output_dir="/home/brian/projects/Digimons/tool_compatability/poc/vertical_slice/thesis_evidence/thesis_results"
    )
    
    try:
        results, metrics = collector.run_full_collection()
        print(f"\n✅ Processed {len(results)} documents")
    finally:
        # Clean up
        collector.framework.cleanup()
        collector.neo4j_driver.close()
    
    # Step 3: Analyze metrics and generate outputs
    print("\n📊 Step 3: Analyzing metrics and generating outputs...")
    
    from metrics_analyzer import ThesisMetricsAnalyzer
    
    analyzer = ThesisMetricsAnalyzer(
        results_db="/home/brian/projects/Digimons/tool_compatability/poc/vertical_slice/thesis_evidence/thesis_results/thesis_results.db",
        output_dir="/home/brian/projects/Digimons/tool_compatability/poc/vertical_slice/thesis_evidence/thesis_analysis"
    )
    
    # Load and analyze
    metrics_data, results_data = analyzer.load_metrics()
    
    # Generate outputs
    analyzer.generate_latex_tables(metrics_data, results_data)
    analyzer.generate_visualizations(metrics_data, results_data)
    summary = analyzer.generate_thesis_summary(metrics_data, results_data)
    
    # Final summary
    print("""
╔══════════════════════════════════════════════════════════════╗
║                    COLLECTION COMPLETE                       ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    print("📁 Output Locations:")
    print(f"   • Ground Truth: {ground_truth_dir}")
    print(f"   • Results Database: thesis_results/thesis_results.db")
    print(f"   • LaTeX Tables: thesis_analysis/tables/")
    print(f"   • Figures: thesis_analysis/figures/")
    print(f"   • Summary: thesis_analysis/thesis_summary.json")
    
    print("\n🎯 Key Results:")
    print(f"   • Uncertainty-Error Correlation: {summary['hypothesis_validation']['correlation_coefficient']:.3f}")
    print(f"   • Overall F1 Score: {summary['performance_summary']['overall_f1']:.3f}")
    print(f"   • Hypothesis Validated: {summary['hypothesis_validation']['validated']}")
    
    print("\n✨ Thesis evidence collection complete!")


if __name__ == "__main__":
    # Check dependencies
    try:
        from dotenv import load_dotenv
        load_dotenv('/home/brian/projects/Digimons/.env')
        
        # Check for Neo4j
        from neo4j import GraphDatabase
        driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "devpassword"))
        driver.verify_connectivity()
        driver.close()
        
    except Exception as e:
        print(f"❌ Error: Prerequisites not met")
        print(f"   {e}")
        print("\nPlease ensure:")
        print("  1. Neo4j is running (bolt://localhost:7687)")
        print("  2. Environment variables are set (.env file)")
        print("  3. All dependencies are installed")
        sys.exit(1)
    
    main()