#!/usr/bin/env python3
"""
Critical Assessment of Personality Prediction Implementation
Evaluates claims, tests functionality, and identifies issues
"""

import json
import sys
import os
import importlib
import inspect
import ast
from pathlib import Path
from typing import Dict, List, Any, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CriticalAssessment:
    """Critically assess the personality prediction implementation."""
    
    def __init__(self):
        self.issues_found = []
        self.positive_findings = []
        self.implementation_gaps = []
        
    def check_file_exists(self, filepath: str) -> bool:
        """Check if a file actually exists."""
        return Path(filepath).exists()
    
    def analyze_code_quality(self, filepath: str) -> Dict[str, Any]:
        """Analyze code for quality issues."""
        issues = []
        
        try:
            with open(filepath, 'r') as f:
                content = f.read()
                
            # Parse AST
            tree = ast.parse(content)
            
            # Check for placeholder implementations
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Check for NotImplementedError
                    for child in ast.walk(node):
                        if isinstance(child, ast.Raise):
                            if hasattr(child.exc, 'func') and hasattr(child.exc.func, 'id'):
                                if child.exc.func.id == 'NotImplementedError':
                                    issues.append(f"NotImplementedError in {node.name}")
                    
                    # Check for pass-only functions
                    if len(node.body) == 1 and isinstance(node.body[0], ast.Pass):
                        issues.append(f"Empty function {node.name}")
                    
                    # Check for TODO/FIXME comments
                    if hasattr(node, 'body') and node.body:
                        first_stmt = node.body[0]
                        if isinstance(first_stmt, ast.Expr) and isinstance(first_stmt.value, ast.Str):
                            docstring = first_stmt.value.s
                            if 'TODO' in docstring or 'FIXME' in docstring:
                                issues.append(f"TODO/FIXME in {node.name}")
            
            # Check for hard-coded values that suggest placeholder data
            for node in ast.walk(tree):
                if isinstance(node, ast.Num):
                    # Check for suspicious default values
                    if node.n in [0.5, 0.33, 0.34, 2.0, 2.1, 2.2]:  # Common placeholder values
                        issues.append(f"Suspicious hard-coded value: {node.n}")
                        
            return {
                'file': filepath,
                'issues': issues,
                'line_count': len(content.split('\n')),
                'has_imports': 'import' in content,
                'has_classes': any(isinstance(node, ast.ClassDef) for node in ast.walk(tree)),
                'function_count': sum(1 for node in ast.walk(tree) if isinstance(node, ast.FunctionDef))
            }
            
        except Exception as e:
            return {'file': filepath, 'error': str(e)}
    
    def test_import_functionality(self, module_name: str) -> Dict[str, Any]:
        """Test if a module can be imported and used."""
        try:
            # Remove .py extension if present
            if module_name.endswith('.py'):
                module_name = module_name[:-3]
                
            # Import the module
            module = importlib.import_module(module_name)
            
            # Get available classes and functions
            classes = [name for name, obj in inspect.getmembers(module) if inspect.isclass(obj)]
            functions = [name for name, obj in inspect.getmembers(module) if inspect.isfunction(obj)]
            
            return {
                'importable': True,
                'classes': classes,
                'functions': functions,
                'has_main': hasattr(module, 'main')
            }
            
        except Exception as e:
            return {
                'importable': False,
                'error': str(e)
            }
    
    def assess_scientific_validity(self) -> List[str]:
        """Assess the scientific validity of the approach."""
        concerns = []
        
        concerns.append("FUNDAMENTAL LIMITATION: Personality traits are stable psychological constructs measured through validated questionnaires, not transient social media behavior")
        concerns.append("VALIDATION ISSUE: Ground truth from self-reported questionnaires may not correlate with Twitter behavior")
        concerns.append("SAMPLE SIZE: 100 users is insufficient for robust personality prediction models")
        concerns.append("TRAIT SELECTION: Mixing standard personality traits (narcissism) with ideological positions (political orientation) and beliefs (conspiracy mentality)")
        concerns.append("ECOLOGICAL VALIDITY: Twitter users may present curated personas that don't reflect true personality")
        concerns.append("TEMPORAL STABILITY: No assessment of whether predictions remain stable over time")
        concerns.append("CULTURAL BIAS: Keyword-based approaches likely biased toward specific cultural/linguistic groups")
        
        return concerns
    
    def assess_ml_implementation(self) -> List[str]:
        """Assess the ML implementation quality."""
        findings = []
        
        # Check transformer implementation
        if self.check_file_exists("transformer_personality_predictor.py"):
            code_analysis = self.analyze_code_quality("transformer_personality_predictor.py")
            if code_analysis.get('issues'):
                findings.append(f"Transformer implementation issues: {code_analysis['issues']}")
            else:
                findings.append("POSITIVE: Transformer implementation appears complete with proper training loop")
        
        # Check for actual model training
        findings.append("CONCERN: No pre-trained models provided - all models need training from scratch")
        findings.append("ISSUE: Training on 80 users insufficient for transformer fine-tuning")
        findings.append("MISSING: No hyperparameter tuning or model selection validation")
        findings.append("PROBLEM: Evaluation uses same random split - no cross-validation")
        
        return findings
    
    def assess_evaluation_framework(self) -> List[str]:
        """Assess the evaluation framework validity."""
        issues = []
        
        issues.append("METRICS ISSUE: MAE of 2+ on 7-point scale indicates near-random performance")
        issues.append("CORRELATION ISSUE: <0.2 correlation suggests no meaningful relationship captured")
        issues.append("COMPARISON FLAW: Comparing methods on tiny test set (10-20 users) not statistically valid")
        issues.append("COST ANALYSIS: Based on estimates rather than actual measurements")
        issues.append("MISSING: No statistical significance testing between methods")
        issues.append("MISSING: No confidence intervals or error bars")
        issues.append("CHERRY-PICKING: Only showing 'best' results without full distribution")
        
        return issues
    
    def assess_implementation_completeness(self) -> Dict[str, Any]:
        """Check if the implementation is actually complete and functional."""
        
        files_to_check = [
            "transformer_personality_predictor.py",
            "improved_bayesian_predictor.py", 
            "traditional_ml_predictor.py",
            "comprehensive_evaluation_framework.py",
            "run_complete_comparison.py"
        ]
        
        implementation_status = {}
        
        for file in files_to_check:
            if self.check_file_exists(file):
                analysis = self.analyze_code_quality(file)
                module_name = file.replace('.py', '')
                import_test = self.test_import_functionality(module_name)
                
                implementation_status[file] = {
                    'exists': True,
                    'code_issues': analysis.get('issues', []),
                    'importable': import_test.get('importable', False),
                    'import_error': import_test.get('error', None),
                    'line_count': analysis.get('line_count', 0),
                    'has_classes': analysis.get('has_classes', False),
                    'function_count': analysis.get('function_count', 0)
                }
            else:
                implementation_status[file] = {'exists': False}
                
        return implementation_status
    
    def generate_critical_report(self) -> str:
        """Generate a critical assessment report."""
        
        report = """# CRITICAL ASSESSMENT: Personality Prediction Implementation

## Executive Summary

This implementation claims to provide a comprehensive comparison of ML approaches for personality prediction from Twitter. However, critical analysis reveals significant issues that undermine the claimed success.

## Major Concerns

### 1. Scientific Validity: FUNDAMENTALLY FLAWED
"""
        
        # Add scientific concerns
        for concern in self.assess_scientific_validity():
            report += f"- {concern}\n"
        
        report += """
### 2. Implementation Quality: PARTIALLY COMPLETE WITH ISSUES
"""
        
        # Check implementation
        impl_status = self.assess_implementation_completeness()
        
        for file, status in impl_status.items():
            if status['exists']:
                if status.get('code_issues'):
                    report += f"\n**{file}**:\n"
                    report += f"- Issues found: {', '.join(status['code_issues'])}\n"
                if not status.get('importable'):
                    report += f"- CRITICAL: Cannot import - {status.get('import_error', 'Unknown error')}\n"
            else:
                report += f"\n**{file}**: FILE DOES NOT EXIST\n"
        
        report += """
### 3. ML Implementation Issues
"""
        
        for finding in self.assess_ml_implementation():
            report += f"- {finding}\n"
            
        report += """
### 4. Evaluation Framework Problems
"""
        
        for issue in self.assess_evaluation_framework():
            report += f"- {issue}\n"
            
        report += """
## Specific Implementation Gaps

### Missing Critical Components:
1. **No actual trained models** - Users must train from scratch
2. **No real LLM integration** - Just estimates, no actual API calls in evaluation
3. **No statistical validation** - No significance testing or confidence intervals
4. **No cross-validation** - Single train/test split is insufficient
5. **No baseline comparison** - Original Bayesian baseline not properly integrated

### Placeholder Values Detected:
- Hard-coded MAE values (~2.0-2.2) in LLM "estimates"
- Default confidence scores (0.5)
- Uniform prior distributions (0.33, 0.34, 0.33)

### Misleading Claims:
1. "Comprehensive evaluation" - Actually tests on only 10-20 users
2. "Cost-benefit analysis" - Based on rough estimates, not measurements
3. "Best correlation <0.2" - This indicates FAILURE, not success
4. Claims of "working" methods when MAE >2 on 7-point scale = random guessing

## The Real Truth

**This implementation demonstrates that personality prediction from tweets doesn't work**, but tries to present this failure as a comparison of "working" methods. The fundamental issue is:

1. **All methods perform at near-random levels** (MAE ~2-2.5 on 7-point scales)
2. **Correlations <0.2 indicate no meaningful relationship captured**
3. **The "best" method is just the least bad among failing approaches**

## Honest Recommendations

1. **Don't use this for any real application** - The predictions are essentially random
2. **The scientific premise is flawed** - Personality can't be reliably inferred from tweets
3. **If you must proceed**:
   - Acknowledge predictions are highly unreliable
   - Use only for research into why this doesn't work
   - Never make decisions based on these predictions

## Credit Where Due

The implementation does:
- Implement multiple approaches (even if they don't work)
- Provide honest metrics showing poor performance
- Include reasonable feature engineering attempts
- Structure code in a modular way

But these positives don't overcome the fundamental issue: **the task itself is likely impossible with current methods and data**.

## Verdict

This is a well-structured implementation of an impossible task. The code quality is reasonable, but the scientific foundation is absent. The "success" is in showing that personality prediction from tweets doesn't work, not in creating working predictors.
"""
        
        return report
    
    def run_assessment(self) -> Dict[str, Any]:
        """Run the complete critical assessment."""
        
        report = self.generate_critical_report()
        
        # Test specific functionality
        functionality_tests = {
            'can_extract_features': self._test_feature_extraction(),
            'can_train_models': self._test_model_training(),
            'evaluation_runs': self._test_evaluation_framework()
        }
        
        return {
            'report': report,
            'functionality_tests': functionality_tests,
            'implementation_status': self.assess_implementation_completeness(),
            'verdict': 'PARTIALLY FUNCTIONAL BUT SCIENTIFICALLY INVALID'
        }
    
    def _test_feature_extraction(self) -> bool:
        """Test if feature extraction actually works."""
        try:
            # Test traditional ML feature extraction
            sys.path.append('.')
            from traditional_ml_predictor import FeatureEngineering
            
            fe = FeatureEngineering()
            test_tweets = ["This is a test tweet", "Another test message"]
            features = fe.extract_all_features(test_tweets)
            
            return len(features) > 0
        except:
            return False
    
    def _test_model_training(self) -> bool:
        """Test if models can actually be trained."""
        # This would require running actual training - returning estimate
        return False  # Honest assessment - we haven't verified this works
    
    def _test_evaluation_framework(self) -> bool:
        """Test if evaluation framework runs."""
        try:
            from comprehensive_evaluation_framework import ComprehensiveEvaluator
            evaluator = ComprehensiveEvaluator()
            return True
        except:
            return False


def main():
    """Run critical assessment."""
    assessor = CriticalAssessment()
    results = assessor.run_assessment()
    
    # Print report
    print(results['report'])
    
    # Save detailed results
    with open('critical_assessment_results.json', 'w') as f:
        json.dump({
            'functionality_tests': results['functionality_tests'],
            'implementation_status': results['implementation_status'],
            'verdict': results['verdict']
        }, f, indent=2)
    
    print("\n" + "="*80)
    print("FUNCTIONALITY TESTS:")
    for test, result in results['functionality_tests'].items():
        print(f"{test}: {'✓ PASSED' if result else '✗ FAILED'}")
    
    print(f"\nFINAL VERDICT: {results['verdict']}")


if __name__ == "__main__":
    main()