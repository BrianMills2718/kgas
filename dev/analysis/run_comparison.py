#!/usr/bin/env python3
"""
Simple runner script for method comparison.
Executes the three personality prediction methods on the same data.
"""

import sys
import logging
from pathlib import Path

# Add paths
sys.path.append(str(Path(__file__).parent))
sys.path.append(str(Path(__file__).parent.parent))

from method_comparison_framework import MethodComparisonFramework

def main():
    """Run the method comparison."""
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
    
    # Check if baseline file exists
    baseline_file = "../uncertainty_stress_test/PARALLEL_100_USERS_FINAL_RESULTS.json"
    
    if not Path(baseline_file).exists():
        logger.error(f"Baseline file not found: {baseline_file}")
        logger.info("Available files in uncertainty_stress_test/:")
        
        uncertainty_dir = Path("uncertainty_stress_test")
        if uncertainty_dir.exists():
            for file in uncertainty_dir.glob("*.json"):
                logger.info(f"  {file.name}")
        
        logger.info("Please update the baseline_file path in the script")
        return False
    
    try:
        # Initialize framework
        logger.info("🚀 Starting method comparison...")
        framework = MethodComparisonFramework(baseline_file)
        
        # Run comparison on first 10 users
        logger.info("🔄 Running three methods on same users...")
        results = framework.run_comparison_on_users(max_users=10)
        
        # Generate report
        logger.info("📊 Generating comparison report...")
        report = framework.generate_comparison_report()
        
        # Display key results
        print("\\n" + "="*60)
        print("🎯 METHOD COMPARISON RESULTS")
        print("="*60)
        
        print(f"\\n📈 Users Analyzed: {report['summary']['total_users_compared']}")
        print(f"🧠 Traits: {', '.join(report['summary']['traits_analyzed'])}")
        print(f"⚡ Methods: {', '.join(report['summary']['methods_compared'])}")
        
        print("\\n⏱️  PROCESSING TIMES:")
        for method, metrics in report["performance_metrics"].items():
            time_avg = metrics['avg_processing_time']
            time_std = metrics['std_processing_time']
            print(f"   {method:20}: {time_avg:.3f}s ± {time_std:.3f}s")
        
        print("\\n🤝 PREDICTION CONSISTENCY (Agreement between methods):")
        for trait, consistency in report["prediction_consistency"].items():
            agreement = consistency['mean_agreement']
            std = consistency['std_agreement']
            print(f"   {trait:20}: {agreement:.3f} ± {std:.3f}")
        
        print("\\n💡 METHODOLOGY DIFFERENCES:")
        for method, details in report["methodology_comparison"].items():
            print(f"\\n   {method.upper()}:")
            print(f"     Approach: {details['approach']}")
            print(f"     Strengths: {', '.join(details['strengths'][:2])}")
            print(f"     Limitations: {', '.join(details['weaknesses'][:2])}")
        
        print("\\n🎯 RECOMMENDATIONS:")
        rec = report["recommendations"]
        print(f"   Overall Agreement: {rec['overall_agreement']:.3f}")
        print(f"   Assessment: {rec['recommendation']}")
        print(f"   Fastest Method: {rec['best_performing_method']}")
        
        print("\\n📝 NEXT STEPS:")
        for step in rec['next_steps']:
            print(f"   • {step}")
        
        # Save detailed results
        output_file = "comparison_results.json"
        framework.save_results(output_file)
        
        print(f"\\n💾 Detailed results saved to: {output_file}")
        print("\\n✅ Comparison completed successfully!")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Comparison failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)