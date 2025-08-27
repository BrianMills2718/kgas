#!/usr/bin/env python3
"""Run thesis evidence collection on paired documents for valid comparison"""

import json
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from evidence_collector import ThesisEvidenceCollector

def main():
    print("""
╔══════════════════════════════════════════════════════════════╗
║         PAIRED DOCUMENT UNCERTAINTY VALIDATION              ║
║                                                              ║
║  Testing same content with different noise levels:          ║
║  - Clean: No noise                                          ║
║  - OCR: Moderate OCR errors                                 ║
║  - Heavy: OCR errors + truncation                           ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    # Use paired documents
    ground_truth_dir = Path("ground_truth_paired")
    
    if not ground_truth_dir.exists():
        print("❌ Paired documents not found. Run generate_paired_documents.py first")
        return
    
    # Load metadata
    with open(ground_truth_dir / "master_metadata.json") as f:
        master = json.load(f)
    
    print(f"📊 Found {master['total_documents']} documents ({master['base_documents']} base × 3 versions)")
    
    # Initialize collector
    collector = ThesisEvidenceCollector(ground_truth_dir=str(ground_truth_dir))
    
    # Results directory
    results_dir = Path("paired_results")
    results_dir.mkdir(exist_ok=True)
    
    all_metrics = []
    
    # Group by base document for comparison
    base_groups = {}
    for doc_id in master['documents']:
        meta = master['metadata'][doc_id]
        base_id = meta['base_id']
        if base_id not in base_groups:
            base_groups[base_id] = []
        base_groups[base_id].append((doc_id, meta))
    
    print("\n📄 Processing paired documents...\n")
    
    # Process each group
    for base_id, versions in base_groups.items():
        print(f"\n=== Base Document: {base_id} ===")
        
        for doc_id, metadata in sorted(versions, key=lambda x: x[1]['noise_type']):
            doc_path = str(ground_truth_dir / "documents" / f"{doc_id}.txt")
            
            print(f"\n  📄 {doc_id} ({metadata['noise_type']})")
            
            try:
                # Run pipeline
                result = collector.run_pipeline_on_document(doc_path, metadata)
                
                if result:
                    # Calculate metrics
                    metrics = collector.calculate_metrics(result, metadata)
                    all_metrics.append(metrics)
                    
                    print(f"     F1: {metrics.f1_score:.3f}, Uncertainty: {result.reported_uncertainty:.3f}")
                    
                    # Save result
                    result_data = {
                        "document_id": doc_id,
                        "base_id": base_id,
                        "noise_type": metadata['noise_type'],
                        "f1_score": metrics.f1_score,
                        "precision": metrics.precision,
                        "recall": metrics.recall,
                        "uncertainty": result.reported_uncertainty,
                        "expected_uncertainty": metadata['expected_uncertainty'],
                        "entity_count": len(result.entities_found),
                        "relationship_count": len(result.relationships_found)
                    }
                    
                    with open(results_dir / f"{doc_id}_result.json", 'w') as f:
                        json.dump(result_data, f, indent=2)
                else:
                    print(f"     ❌ Pipeline failed")
                    
            except Exception as e:
                print(f"     ❌ Error: {e}")
    
    # Analyze results
    print("\n\n📊 Analysis by Noise Level:")
    print("-" * 60)
    
    # Group metrics by noise type
    by_noise = {'none': [], 'ocr': [], 'ocr+truncation': []}
    for metrics in all_metrics:
        doc_meta = master['metadata'][metrics.document_id]
        noise_type = doc_meta['noise_type']
        by_noise[noise_type].append(metrics)
    
    print(f"{'Noise Type':<20} {'Count':<8} {'Avg F1':<10} {'Avg Unc':<10}")
    print("-" * 60)
    
    for noise_type, metrics_list in by_noise.items():
        if metrics_list:
            avg_f1 = sum(m.f1_score for m in metrics_list) / len(metrics_list)
            # Get uncertainties from saved results
            uncertainties = []
            for m in metrics_list:
                result_file = results_dir / f"{m.document_id}_result.json"
                if result_file.exists():
                    with open(result_file) as f:
                        uncertainties.append(json.load(f)['uncertainty'])
            avg_unc = sum(uncertainties) / len(uncertainties) if uncertainties else 0
            print(f"{noise_type:<20} {len(metrics_list):<8} {avg_f1:<10.3f} {avg_unc:<10.3f}")
    
    # Calculate correlation
    print("\n📈 Correlation Analysis:")
    print("-" * 60)
    
    if all_metrics:
        import numpy as np
        from scipy import stats
        
        # Get uncertainty from results, not metrics
        uncertainties = []
        for metrics in all_metrics:
            result_file = results_dir / f"{metrics.document_id}_result.json"
            if result_file.exists():
                with open(result_file) as f:
                    result = json.load(f)
                    uncertainties.append(result['uncertainty'])
            else:
                uncertainties.append(0.5)  # Default if missing
        errors = [1 - m.f1_score for m in all_metrics]
        
        correlation, p_value = stats.pearsonr(uncertainties, errors)
        print(f"Uncertainty-Error Correlation: {correlation:.3f} (p={p_value:.3f})")
        
        if correlation > 0.3:
            print("✅ Positive correlation achieved - uncertainty predicts errors!")
        else:
            print("⚠️ Weak/negative correlation - uncertainty doesn't predict errors well")
    
    # Save summary with proper uncertainty values
    summary_by_noise = {}
    for noise_type, metrics_list in by_noise.items():
        if metrics_list:
            # Get uncertainties from saved results
            noise_uncertainties = []
            for m in metrics_list:
                result_file = results_dir / f"{m.document_id}_result.json"
                if result_file.exists():
                    with open(result_file) as f:
                        noise_uncertainties.append(json.load(f)['uncertainty'])
            
            summary_by_noise[noise_type] = {
                "count": len(metrics_list),
                "avg_f1": sum(m.f1_score for m in metrics_list) / len(metrics_list),
                "avg_uncertainty": sum(noise_uncertainties) / len(noise_uncertainties) if noise_uncertainties else 0
            }
        else:
            summary_by_noise[noise_type] = {"count": 0, "avg_f1": 0, "avg_uncertainty": 0}
    
    summary = {
        "total_documents": len(all_metrics),
        "base_documents": master['base_documents'],
        "by_noise_type": summary_by_noise,
        "correlation": correlation if all_metrics else None
    }
    
    with open(results_dir / "summary.json", 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"\n✅ Results saved to {results_dir}/")

if __name__ == "__main__":
    main()