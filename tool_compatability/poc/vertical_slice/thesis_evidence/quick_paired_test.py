#!/usr/bin/env python3
"""Quick test of paired documents to verify correlation"""

from pathlib import Path
import sys
import json

sys.path.append('.')
sys.path.append('..')

from evidence_collector import ThesisEvidenceCollector

# Test just doc_A in all three versions
ground_truth_dir = Path('ground_truth_paired')
collector = ThesisEvidenceCollector(str(ground_truth_dir))

test_docs = [
    ('doc_001_clean.json', 'doc_001_clean.txt', 'Clean'),
    ('doc_002_ocr.json', 'doc_002_ocr.txt', 'OCR Noise'),
    ('doc_003_heavy.json', 'doc_003_heavy.txt', 'Heavy Noise')
]

results = []

print("\n=== Testing Document A (Brian/KGAS) ===\n")

for meta_file, doc_file, label in test_docs:
    with open(ground_truth_dir / 'metadata' / meta_file) as f:
        metadata = json.load(f)
    
    doc_path = str(ground_truth_dir / 'documents' / doc_file)
    
    print(f"📄 {label}:")
    result = collector.run_pipeline_on_document(doc_path, metadata)
    
    if result:
        metrics = collector.calculate_metrics(result, metadata)
        print(f"   F1: {metrics.f1_score:.3f}, Uncertainty: {result.reported_uncertainty:.3f}")
        print(f"   Entities: {len(result.entities_found)}, Relationships: {len(result.relationships_found)}")
        results.append({
            'type': label,
            'f1': metrics.f1_score,
            'uncertainty': result.reported_uncertainty,
            'error': 1 - metrics.f1_score
        })
    print()

# Analysis
print("\n=== ANALYSIS ===\n")
print(f"{'Type':<15} {'F1':<10} {'Uncertainty':<15} {'Error':<10}")
print("-" * 50)
for r in results:
    print(f"{r['type']:<15} {r['f1']:<10.3f} {r['uncertainty']:<15.3f} {r['error']:<10.3f}")

# Check correlation direction
if len(results) == 3:
    # Does uncertainty increase with noise?
    unc_trend = results[2]['uncertainty'] > results[0]['uncertainty']
    # Does F1 decrease with noise?
    f1_trend = results[2]['f1'] < results[0]['f1']
    
    print(f"\n✅ Uncertainty increases with noise: {unc_trend}")
    print(f"✅ F1 decreases with noise: {f1_trend}")
    
    if unc_trend and f1_trend:
        print("\n🎉 SUCCESS: Higher noise → Higher uncertainty & Lower F1")
        print("This suggests positive correlation between uncertainty and error!")
    else:
        print("\n⚠️ WARNING: Unexpected relationship between noise, uncertainty, and F1")