#!/usr/bin/env python3
"""
Run MCP Tool Exposure Validation

Script to execute comprehensive MCP tool exposure validation and generate reports.
"""

import asyncio
import sys
import logging
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from validation.mcp_tool_exposure_validator import (
    MCPToolExposureValidator,
    MCPToolValidationConfig,
    ValidationSeverity
)


async def run_comprehensive_validation():
    """Run comprehensive MCP tool validation"""
    
    print("🔍 KGAS MCP Tool Exposure Validation")
    print("=" * 50)
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Create validation configuration
    config = MCPToolValidationConfig(
        test_timeout_seconds=30.0,
        enable_deep_testing=True,
        enable_performance_testing=False,
        test_with_sample_data=True,
        validate_tool_contracts=True,
        check_error_handling=True,
        validate_parameter_schemas=True
    )
    
    # Create validator
    validator = MCPToolExposureValidator(config)
    
    try:
        print("📋 Initializing MCP server for validation...")
        
        # Run validation
        print("🧪 Running comprehensive tool exposure validation...")
        results = await validator.validate_all_tool_exposure()
        
        # Display results
        print("\n" + "=" * 60)
        print("📊 VALIDATION RESULTS SUMMARY")
        print("=" * 60)
        
        summary = results['validation_summary']
        stats = results['tool_exposure_statistics']
        issues = results['validation_issues']
        
        # Overall status
        status_icon = {
            'HEALTHY': '✅',
            'WARNINGS_FOUND': '⚠️',
            'ERRORS_FOUND': '❌',
            'CRITICAL_ISSUES': '🚨',
            'FAILED': '💥'
        }.get(summary['overall_status'], '❓')
        
        print(f"Overall Status: {status_icon} {summary['overall_status']}")
        print(f"Validation Success: {'✅ Yes' if summary['success'] else '❌ No'}")
        print(f"Timestamp: {summary['timestamp']}")
        
        # Tool exposure statistics
        print(f"\n📈 TOOL EXPOSURE STATISTICS")
        print(f"  Total Tools Validated: {stats['total_tools_validated']}")
        print(f"  Fully Exposed: {stats['fully_exposed']} ({stats['exposure_rate_percent']:.1f}%)")
        print(f"  Partially Exposed: {stats['partially_exposed']}")
        print(f"  Not Exposed: {stats['not_exposed']}")
        print(f"  Exposed but Broken: {stats['exposed_but_broken']}")
        
        # Issues summary
        print(f"\n🔍 VALIDATION ISSUES")
        print(f"  Total Issues: {issues['total_issues']}")
        for severity, count in issues['by_severity'].items():
            severity_icon = {
                'critical': '🚨',
                'error': '❌',
                'warning': '⚠️',
                'info': 'ℹ️'
            }.get(severity, '❓')
            print(f"  {severity_icon} {severity.title()}: {count}")
        
        # Tool results breakdown
        print(f"\n🔧 TOOL RESULTS BREAKDOWN")
        tool_results = results['tool_results']
        
        categories = {}
        for tool_id, tool_result in tool_results.items():
            category = tool_result.get('category', 'unknown')
            if category not in categories:
                categories[category] = {
                    'total': 0,
                    'exposed': 0,
                    'partially_exposed': 0,
                    'not_exposed': 0,
                    'broken': 0
                }
            
            categories[category]['total'] += 1
            status = tool_result['exposure_status']
            if status == 'exposed':
                categories[category]['exposed'] += 1
            elif status == 'partially_exposed':
                categories[category]['partially_exposed'] += 1
            elif status == 'not_exposed':
                categories[category]['not_exposed'] += 1
            elif status == 'exposed_but_broken':
                categories[category]['broken'] += 1
        
        for category, cat_stats in categories.items():
            total = cat_stats['total']
            exposed = cat_stats['exposed']
            rate = (exposed / total * 100) if total > 0 else 0
            
            print(f"  📁 {category.title()}: {exposed}/{total} exposed ({rate:.1f}%)")
            if cat_stats['partially_exposed'] > 0:
                print(f"    ⚠️ Partially Exposed: {cat_stats['partially_exposed']}")
            if cat_stats['not_exposed'] > 0:
                print(f"    ❌ Not Exposed: {cat_stats['not_exposed']}")
            if cat_stats['broken'] > 0:
                print(f"    🚨 Broken: {cat_stats['broken']}")
        
        # Show specific issues if any
        if issues['total_issues'] > 0:
            print(f"\n⚠️ SPECIFIC ISSUES FOUND")
            for issue in issues['issues'][:10]:  # Show first 10 issues
                severity_icon = {
                    'critical': '🚨',
                    'error': '❌', 
                    'warning': '⚠️',
                    'info': 'ℹ️'
                }.get(issue['severity'], '❓')
                
                print(f"  {severity_icon} [{issue['component']}] {issue['description']}")
                print(f"    💡 Recommendation: {issue['recommendation']}")
            
            if len(issues['issues']) > 10:
                print(f"  ... and {len(issues['issues']) - 10} more issues")
        
        # Show recommendations
        recommendations = results.get('recommendations', [])
        if recommendations:
            print(f"\n💡 RECOMMENDATIONS")
            for i, rec in enumerate(recommendations, 1):
                print(f"  {i}. {rec}")
        
        # Show detailed tool results for key tools
        print(f"\n🔧 KEY TOOL STATUS")
        key_tools = [
            'T01_PDF_LOADER',
            'T23A_SPACY_NER', 
            'T68_PAGERANK',
            'T49_MULTIHOP_QUERY',
            'SERVER_MANAGEMENT'
        ]
        
        for tool_id in key_tools:
            if tool_id in tool_results:
                tool_result = tool_results[tool_id]
                status = tool_result['exposure_status']
                status_icon = {
                    'exposed': '✅',
                    'partially_exposed': '⚠️',
                    'not_exposed': '❌',
                    'exposed_but_broken': '🚨'
                }.get(status, '❓')
                
                print(f"  {status_icon} {tool_id}: {status}")
                if tool_result['functions_found']:
                    print(f"    📋 Functions: {', '.join(tool_result['functions_found'][:3])}{'...' if len(tool_result['functions_found']) > 3 else ''}")
                if tool_result['validation_errors']:
                    print(f"    ❌ Errors: {tool_result['validation_errors'][0]}{'...' if len(tool_result['validation_errors']) > 1 else ''}")
        
        # Export detailed report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = f"mcp_tool_validation_report_{timestamp}.json"
        
        print(f"\n📄 Exporting detailed report...")
        success = await validator.export_validation_report(report_path)
        if success:
            print(f"✅ Detailed report saved to: {report_path}")
        else:
            print(f"❌ Failed to export detailed report")
        
        # Final summary
        print(f"\n" + "=" * 60)
        if summary['overall_status'] == 'HEALTHY':
            print("🎉 MCP tool exposure validation PASSED!")
            print("   All tools are properly exposed and functional via MCP.")
        elif summary['overall_status'] in ['WARNINGS_FOUND', 'ERRORS_FOUND']:
            print("⚠️ MCP tool exposure validation completed with ISSUES.")
            print("   Some tools need attention but basic functionality is available.")
        else:
            print("🚨 MCP tool exposure validation FAILED!")
            print("   Critical issues found - immediate attention required.")
        
        print(f"📊 Summary: {stats['fully_exposed']}/{stats['total_tools_validated']} tools fully exposed ({stats['exposure_rate_percent']:.1f}%)")
        
        return summary['overall_status'] in ['HEALTHY', 'WARNINGS_FOUND']
        
    except Exception as e:
        print(f"\n💥 Validation failed with error: {e}")
        logging.error(f"Validation error: {e}", exc_info=True)
        return False


async def run_quick_validation():
    """Run quick validation without deep testing"""
    
    print("⚡ Quick MCP Tool Exposure Check")
    print("=" * 40)
    
    config = MCPToolValidationConfig(
        test_timeout_seconds=10.0,
        enable_deep_testing=False,
        validate_tool_contracts=False
    )
    
    validator = MCPToolExposureValidator(config)
    
    try:
        results = await validator.validate_all_tool_exposure()
        
        stats = results['tool_exposure_statistics']
        print(f"✅ Quick validation completed")
        print(f"📊 {stats['fully_exposed']}/{stats['total_tools_validated']} tools exposed ({stats['exposure_rate_percent']:.1f}%)")
        
        if stats['exposed_but_broken'] > 0:
            print(f"⚠️ {stats['exposed_but_broken']} tools are exposed but may have issues")
        
        return stats['exposure_rate_percent'] > 50
        
    except Exception as e:
        print(f"❌ Quick validation failed: {e}")
        return False


async def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Run MCP Tool Exposure Validation")
    parser.add_argument(
        "--mode", 
        choices=["comprehensive", "quick"],
        default="comprehensive",
        help="Validation mode"
    )
    
    args = parser.parse_args()
    
    try:
        if args.mode == "comprehensive":
            success = await run_comprehensive_validation()
        else:
            success = await run_quick_validation()
        
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print("\n🛑 Validation interrupted by user")
        return 1
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))