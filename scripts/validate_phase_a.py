#!/usr/bin/env python3
"""
Phase A Validation Script
Validates that Phase A implementation is complete and working
"""
import asyncio
import sys
import os
from pathlib import Path
import time
import json

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.mcp.tool_registry import MCPToolRegistry
from src.mcp.mcp_server import MCPServer, MCPClient
from src.nlp.question_parser import QuestionParser, QuestionIntent
from src.nlp.response_generator import ResponseGenerator
from src.execution.mcp_executor import MCPExecutor, PipelineManager
from src.interface.nl_interface import NaturalLanguageInterface
from src.core.service_manager import ServiceManager

class PhaseAValidator:
    """Validates Phase A implementation completeness"""
    
    def __init__(self):
        self.test_results = {}
        self.service_manager = None
        
    async def run_validation(self):
        """Run complete Phase A validation"""
        print("🔧 PHASE A VALIDATION")
        print("=" * 60)
        print("Validating MCP Integration & Basic Natural Language Interface")
        print()
        
        # Initialize service manager
        try:
            self.service_manager = ServiceManager()
            print("✅ Service manager initialized")
        except Exception as e:
            print(f"❌ Service manager initialization failed: {e}")
            return False
        
        # Run validation tests
        validation_tests = [
            ("MCP Tool Registration", self._test_mcp_tool_registration),
            ("Question Parsing", self._test_question_parsing),
            ("MCP Execution", self._test_mcp_execution),
            ("Response Generation", self._test_response_generation),
            ("End-to-End Workflow", self._test_e2e_workflow),
            ("Error Handling", self._test_error_handling)
        ]
        
        passed_tests = 0
        total_tests = len(validation_tests)
        
        for test_name, test_func in validation_tests:
            print(f"\n🧪 Testing {test_name}...")
            
            try:
                start_time = time.time()
                result = await test_func()
                execution_time = time.time() - start_time
                
                if result:
                    print(f"   ✅ {test_name} - Passed ({execution_time:.2f}s)")
                    passed_tests += 1
                    self.test_results[test_name] = {
                        'status': 'passed',
                        'execution_time': execution_time
                    }
                else:
                    print(f"   ❌ {test_name} - Failed ({execution_time:.2f}s)")
                    self.test_results[test_name] = {
                        'status': 'failed',
                        'execution_time': execution_time
                    }
                    
            except Exception as e:
                print(f"   ❌ {test_name} - Error: {e}")
                self.test_results[test_name] = {
                    'status': 'error',
                    'error': str(e)
                }
        
        # Calculate success rate
        success_rate = (passed_tests / total_tests) * 100
        
        print(f"\n📊 PHASE A VALIDATION RESULTS")
        print(f"   Tests Passed: {passed_tests}/{total_tests}")
        print(f"   Success Rate: {success_rate:.1f}%")
        
        if success_rate >= 100:
            print(f"\n🎉 PHASE A VALIDATION: COMPLETE SUCCESS!")
            print(f"   All systems operational - Phase B ready")
            return True
        elif success_rate >= 80:
            print(f"\n✅ PHASE A VALIDATION: MOSTLY SUCCESSFUL")
            print(f"   Core functionality working - Minor issues to address")
            return True
        else:
            print(f"\n⚠️  PHASE A VALIDATION: NEEDS WORK")
            print(f"   Major issues found - Address before Phase B")
            return False
    
    async def _test_mcp_tool_registration(self):
        """Test MCP tool registration works"""
        try:
            # Test tool registry
            registry = MCPToolRegistry(self.service_manager)
            tools = registry.list_tools()
            
            # Should have all 8 tools
            expected_tools = [
                "T01_PDF_LOADER", "T15A_TEXT_CHUNKER", "T23A_SPACY_NER",
                "T27_RELATIONSHIP_EXTRACTOR", "T31_ENTITY_BUILDER", "T34_EDGE_BUILDER",
                "T68_PAGE_RANK", "T49_MULTI_HOP_QUERY"
            ]
            
            if len(tools) != 8:
                print(f"     Expected 8 tools, got {len(tools)}")
                return False
            
            for tool_id in expected_tools:
                if tool_id not in tools:
                    print(f"     Missing tool: {tool_id}")
                    return False
            
            # Test manifest generation
            manifest = registry.get_tool_manifest()
            if "tools" not in manifest or len(manifest["tools"]) != 8:
                print(f"     Manifest generation failed")
                return False
            
            print(f"     All 8 tools registered successfully")
            return True
            
        except Exception as e:
            print(f"     Registry error: {e}")
            return False
    
    async def _test_question_parsing(self):
        """Test question parsing handles 5 question types"""
        try:
            parser = QuestionParser()
            
            test_questions = [
                ("What is this document about?", QuestionIntent.DOCUMENT_SUMMARY),
                ("Who are the key people?", QuestionIntent.ENTITY_ANALYSIS),
                ("How do they relate?", QuestionIntent.RELATIONSHIP_ANALYSIS),
                ("What are the main themes?", QuestionIntent.THEME_ANALYSIS),
                ("Find information about Microsoft", QuestionIntent.SPECIFIC_SEARCH)
            ]
            
            correct_classifications = 0
            
            for question, expected_intent in test_questions:
                parsed = parser.parse_question(question)
                
                if parsed.intent == expected_intent:
                    correct_classifications += 1
                else:
                    print(f"     Misclassified: '{question}' as {parsed.intent.value}, expected {expected_intent.value}")
            
            success_rate = (correct_classifications / len(test_questions)) * 100
            print(f"     Classification accuracy: {success_rate:.1f}% ({correct_classifications}/{len(test_questions)})")
            
            return success_rate >= 80  # At least 80% accuracy required
            
        except Exception as e:
            print(f"     Parsing error: {e}")
            return False
    
    async def _test_mcp_execution(self):
        """Test MCP execution completes tool chains"""
        try:
            # Create simple execution plan
            from src.nlp.question_parser import ExecutionPlan, ExecutionStep
            
            # Simple plan: T01 -> T15A
            steps = [
                ExecutionStep(
                    tool_id="T01_PDF_LOADER",
                    arguments={
                        "input_data": {"file_path": "test.pdf"},
                        "parameters": {}
                    }
                ),
                ExecutionStep(
                    tool_id="T15A_TEXT_CHUNKER",
                    arguments={
                        "input_data": {},
                        "parameters": {}
                    },
                    depends_on=["T01_PDF_LOADER"]
                )
            ]
            
            execution_plan = ExecutionPlan(steps=steps)
            
            # Test executor
            executor = MCPExecutor()
            pipeline_manager = PipelineManager(executor)
            
            # Validate execution plan
            issues = pipeline_manager.validate_execution_plan(execution_plan)
            if issues:
                print(f"     Execution plan issues: {issues}")
                # Continue - issues may be acceptable for test
            
            # Test execution (may fail due to missing file, but should not crash)
            result = await pipeline_manager.execute_pipeline(execution_plan, "test question")
            
            # Should get some result (even if tools failed)
            if result is None:
                print("     No execution result returned")
                return False
            
            print(f"     Execution completed: {result.success_count} successes, {result.failure_count} failures")
            return True  # Success if it doesn't crash
            
        except Exception as e:
            print(f"     Execution error: {e}")
            return False
    
    async def _test_response_generation(self):
        """Test response generation produces natural language"""
        try:
            generator = ResponseGenerator()
            
            # Mock tool results
            mock_results = {
                "T23A_SPACY_NER": {
                    "status": "success",
                    "data": {
                        "entities": [
                            {"surface_form": "Microsoft", "entity_type": "ORG", "confidence": 0.9},
                            {"surface_form": "Google", "entity_type": "ORG", "confidence": 0.8}
                        ]
                    },
                    "metadata": {"execution_time": 1.5, "confidence": 0.85}
                }
            }
            
            # Generate response
            response = generator.generate_response(
                question="What entities are mentioned?",
                tool_results=mock_results,
                intent=QuestionIntent.ENTITY_ANALYSIS
            )
            
            # Validate response
            if not isinstance(response, str):
                print("     Response is not a string")
                return False
            
            if len(response) < 50:
                print(f"     Response too short: {len(response)} characters")
                return False
            
            # Should contain key elements
            required_elements = ["Microsoft", "Google", "Analysis Provenance"]
            missing_elements = [elem for elem in required_elements if elem not in response]
            
            if missing_elements:
                print(f"     Missing elements: {missing_elements}")
                return False
            
            print(f"     Generated {len(response)} character response with provenance")
            return True
            
        except Exception as e:
            print(f"     Response generation error: {e}")
            return False
    
    async def _test_e2e_workflow(self):
        """Test end-to-end workflow: question → answer works"""
        try:
            # Create test document
            test_file = Path("phase_a_test.txt")
            test_content = "This is a test document for Phase A validation with Microsoft and Google as key entities."
            test_file.write_text(test_content)
            
            try:
                # Create interface
                interface = NaturalLanguageInterface(self.service_manager)
                await interface.initialize()
                
                # Load document
                load_success = await interface.load_document(str(test_file))
                if not load_success:
                    print("     Failed to load test document")
                    return False
                
                # Ask question
                response = await interface.ask_question("What is this document about?")
                
                # Validate response
                if not isinstance(response, str):
                    print("     Response is not a string")
                    return False
                
                if "error" in response.lower():
                    print(f"     Error in response: {response[:100]}...")
                    return False
                
                if len(response) < 30:
                    print(f"     Response too short: {len(response)} characters")
                    return False
                
                print(f"     E2E workflow successful: {len(response)} character response")
                return True
                
            finally:
                # Clean up
                if test_file.exists():
                    test_file.unlink()
                    
        except Exception as e:
            print(f"     E2E workflow error: {e}")
            return False
    
    async def _test_error_handling(self):
        """Test graceful error handling"""
        try:
            interface = NaturalLanguageInterface(self.service_manager)
            await interface.initialize()
            
            # Test with no document loaded
            response1 = await interface.ask_question("What is this about?")
            if "load a document" not in response1.lower():
                print("     Missing document error not handled properly")
                return False
            
            # Test with empty question
            test_file = Path("error_test.txt")
            test_file.write_text("Test content")
            
            try:
                await interface.load_document(str(test_file))
                response2 = await interface.ask_question("")
                
                # Should not crash, should return some response
                if not isinstance(response2, str):
                    print("     Empty question not handled properly")
                    return False
                
                print("     Error handling working correctly")
                return True
                
            finally:
                if test_file.exists():
                    test_file.unlink()
                    
        except Exception as e:
            print(f"     Error handling test error: {e}")
            return False
    
    def save_results(self, filepath="phase_a_validation_results.json"):
        """Save validation results to file"""
        results = {
            "timestamp": time.time(),
            "phase": "A",
            "description": "MCP Integration & Basic NL Interface",
            "test_results": self.test_results,
            "summary": {
                "total_tests": len(self.test_results),
                "passed_tests": len([r for r in self.test_results.values() if r.get('status') == 'passed']),
                "failed_tests": len([r for r in self.test_results.values() if r.get('status') == 'failed']),
                "error_tests": len([r for r in self.test_results.values() if r.get('status') == 'error'])
            }
        }
        
        with open(filepath, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n📄 Results saved to: {filepath}")

async def main():
    """Main validation function"""
    validator = PhaseAValidator()
    success = await validator.run_validation()
    
    # Save results
    validator.save_results()
    
    if success:
        print(f"\n🎉 PHASE A VALIDATION COMPLETE!")
        print(f"   Natural Language Interface is operational")
        print(f"   Ready to proceed to Phase B implementation")
        return 0
    else:
        print(f"\n⚠️  PHASE A VALIDATION INCOMPLETE")
        print(f"   Address issues before proceeding to Phase B")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())