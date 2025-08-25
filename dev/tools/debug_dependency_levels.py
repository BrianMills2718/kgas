#!/usr/bin/env python3
"""
Debug dependency level calculation
"""
import asyncio
import logging
from pathlib import Path

logging.basicConfig(level=logging.DEBUG)

async def debug_dependencies():
    from src.core.service_manager import ServiceManager
    from src.nlp.natural_language_interface import NaturalLanguageInterface
    from src.execution.dependency_analyzer import DependencyAnalyzer
    
    service_manager = ServiceManager()
    interface = NaturalLanguageInterface(service_manager)
    await interface.initialize()
    
    doc_path = Path("test_deps.txt")
    doc_path.write_text("Microsoft and Google are companies.")
    interface.current_document_path = str(doc_path)
    
    question = "Build comprehensive knowledge graph of all companies and analyze their network structure"
    result = await interface.ask_question(question)
    
    # Get the tool chain that was generated
    if hasattr(interface, 'last_result') and interface.last_result:
        result_obj = interface.last_result
        if hasattr(result_obj, 'advanced_analysis'):
            analysis = result_obj.advanced_analysis
            if hasattr(analysis, 'tool_chain'):
                chain = analysis.tool_chain
                
                print("\nTool Chain Steps:")
                for step in chain.steps:
                    print(f"  {step.tool_id}: depends on {step.depends_on}")
                
                # Test dependency analyzer
                analyzer = DependencyAnalyzer()
                dependency_analysis = analyzer.analyze_dependencies(chain.steps)
                
                print(f"\nDependency Levels: {dependency_analysis.dependency_levels}")
                print(f"Independent Pairs: {dependency_analysis.independent_pairs}")
                print(f"Parallel Groups: {dependency_analysis.parallel_groups}")
    
    doc_path.unlink(missing_ok=True)

if __name__ == "__main__":
    asyncio.run(debug_dependencies())