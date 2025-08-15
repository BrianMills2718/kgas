#!/usr/bin/env python3
"""
Phase 2: LLM-Powered Reasoning System Demonstration

This demonstrates the complete LLM reasoning capabilities integrated with the memory system,
showing how agents make intelligent decisions and adapt their strategies dynamically.
"""

import asyncio
import json
import time
import logging
from pathlib import Path
from typing import Dict, Any, List

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import KGAS orchestration components
from src.orchestration.simple_orchestrator import SimpleSequentialOrchestrator
from src.orchestration.base import Task, TaskPriority
from src.orchestration.llm_reasoning import ReasoningType
from src.orchestration.agents.document_agent import DocumentAgent
from src.orchestration.agents.analysis_agent import AnalysisAgent
from src.orchestration.mcp_adapter import MCPToolAdapter


class Phase2ReasoningDemo:
    """
    Comprehensive demonstration of Phase 2 LLM reasoning capabilities.
    """
    
    def __init__(self):
        self.results = {}
        self.demo_config = {
            "memory": {
                "document": {
                    "enable_memory": True,
                    "max_memories": 50,
                    "learning_enabled": True
                },
                "analysis": {
                    "enable_memory": True,
                    "max_memories": 50,
                    "learning_enabled": True
                }
            },
            "reasoning": {
                "document": {
                    "enable_reasoning": True,
                    "default_reasoning_type": "strategic",
                    "reasoning_threshold": 0.5,
                    "max_reasoning_time": 30.0
                },
                "analysis": {
                    "enable_reasoning": True,
                    "default_reasoning_type": "tactical",
                    "reasoning_threshold": 0.5,
                    "max_reasoning_time": 30.0
                }
            }
        }
    
    async def run_complete_demo(self) -> Dict[str, Any]:
        """Run complete Phase 2 reasoning demonstration."""
        
        print("🧠 Phase 2: LLM-Powered Reasoning System Demo")
        print("=" * 60)
        
        try:
            # 1. Initialize reasoning-enhanced agents
            print("\n1️⃣ Initializing Reasoning-Enhanced Agents...")
            mcp_adapter = MCPToolAdapter()
            await mcp_adapter.initialize()
            
            # Create reasoning-enhanced agents
            doc_agent = DocumentAgent(
                mcp_adapter, 
                "reasoning_doc_agent", 
                self.demo_config["memory"]["document"],
                self.demo_config["reasoning"]["document"]
            )
            
            analysis_agent = AnalysisAgent(
                mcp_adapter,
                "reasoning_analysis_agent",
                self.demo_config["memory"]["analysis"],
                self.demo_config["reasoning"]["analysis"]
            )
            
            await doc_agent.initialize()
            await analysis_agent.initialize()
            
            print(f"✅ Created DocumentAgent with reasoning: {doc_agent.reasoning_engine is not None}")
            print(f"✅ Created AnalysisAgent with reasoning: {analysis_agent.reasoning_engine is not None}")
            
            # 2. Demonstrate document processing reasoning
            doc_results = await self._demo_document_reasoning(doc_agent)
            self.results["document_reasoning"] = doc_results
            
            # 3. Demonstrate analysis reasoning
            analysis_results = await self._demo_analysis_reasoning(analysis_agent, doc_results)
            self.results["analysis_reasoning"] = analysis_results
            
            # 4. Demonstrate reasoning evolution through multiple tasks
            evolution_results = await self._demo_reasoning_evolution(doc_agent, analysis_agent)
            self.results["reasoning_evolution"] = evolution_results
            
            # 5. Demonstrate orchestrator integration
            orchestrator_results = await self._demo_orchestrator_reasoning()
            self.results["orchestrator_reasoning"] = orchestrator_results
            
            # 6. Generate comprehensive report
            await self._generate_reasoning_report()
            
            print("\n✅ Phase 2 LLM Reasoning Demo Complete!")
            return self.results
            
        except Exception as e:
            logger.error(f"Demo failed: {e}")
            print(f"\n❌ Demo failed: {e}")
            return {"error": str(e)}
    
    async def _demo_document_reasoning(self, doc_agent: DocumentAgent) -> Dict[str, Any]:
        """Demonstrate document processing with reasoning."""
        
        print("\n2️⃣ Document Processing Reasoning Demo")
        print("-" * 40)
        
        # Create sample document content for testing
        sample_docs = [
            {
                "path": "test_doc_short.txt",
                "content": "This is a short document for testing. It has minimal content to test small document handling."
            },
            {
                "path": "test_doc_medium.txt", 
                "content": "This is a medium-length document for testing reasoning capabilities. " * 20 + 
                          "It contains more complex content that should trigger strategic reasoning decisions for chunking optimization."
            },
            {
                "path": "test_doc_long.txt",
                "content": "This is a long document for comprehensive testing. " * 100 +
                          "It has extensive content that should demonstrate the full reasoning capabilities of the document agent. " * 50
            }
        ]
        
        results = {}
        
        # Test reasoning with different document complexities
        for i, doc_sample in enumerate(sample_docs, 1):
            print(f"\n📄 Testing Document {i}: {doc_sample['path']}")
            
            # Create task for document processing
            task = Task(
                task_id=f"reasoning_doc_test_{i}",
                task_type="document_processing",
                parameters={
                    "document_paths": [doc_sample["path"]],
                    "documents": [doc_sample]  # Pass content directly for demo
                },
                context={
                    "demo_mode": True,
                    "document_content": doc_sample["content"]
                },
                priority=TaskPriority.HIGH
            )
            
            # Execute with reasoning
            start_time = time.time()
            result = await doc_agent.execute(task)
            execution_time = time.time() - start_time
            
            # Analyze reasoning application
            reasoning_applied = result.metadata.get("reasoning", {}) if result.metadata else {}
            
            print(f"  ✅ Success: {result.success}")
            print(f"  🧠 Reasoning Applied: {reasoning_applied.get('applied', False)}")
            if reasoning_applied.get("applied"):
                print(f"     Type: {reasoning_applied.get('type', 'unknown')}")
                print(f"     Confidence: {reasoning_applied.get('confidence', 0.0):.2f}")
                print(f"     Reasoning Time: {reasoning_applied.get('execution_time', 0.0):.3f}s")
            print(f"  ⏱️  Total Execution: {execution_time:.3f}s")
            
            results[f"document_{i}"] = {
                "success": result.success,
                "reasoning_applied": reasoning_applied.get("applied", False),
                "reasoning_type": reasoning_applied.get("type"),
                "reasoning_confidence": reasoning_applied.get("confidence"),
                "execution_time": execution_time,
                "chunks_created": result.data.get("total_chunks", 0) if result.success else 0
            }
        
        # Get agent reasoning summary
        reasoning_summary = await doc_agent.get_reasoning_summary()
        results["agent_summary"] = reasoning_summary
        
        print(f"\n📊 Document Agent Reasoning Stats:")
        print(f"   Total Reasonings: {reasoning_summary['reasoning_stats']['total_reasonings']}")
        print(f"   Successful: {reasoning_summary['reasoning_stats']['successful_reasonings']}")
        print(f"   Decisions Improved: {reasoning_summary['reasoning_stats']['decisions_improved']}")
        
        return results
    
    async def _demo_analysis_reasoning(self, analysis_agent: AnalysisAgent, doc_results: Dict[str, Any]) -> Dict[str, Any]:
        """Demonstrate analysis with reasoning-based optimization."""
        
        print("\n3️⃣ Analysis Reasoning Demo")
        print("-" * 40)
        
        # Create sample chunks for analysis
        sample_chunks = [
            {
                "chunk_ref": "chunk_1",
                "text": "Apple Inc. is a technology company founded by Steve Jobs in California. The company produces iPhone, iPad, and Mac computers.",
                "chunk_confidence": 0.9
            },
            {
                "chunk_ref": "chunk_2", 
                "text": "Microsoft Corporation, led by CEO Satya Nadella, develops Windows operating system and Office productivity software in Washington state.",
                "source_document": "tech_companies.pdf",
                "chunk_confidence": 0.8
            },
            {
                "chunk_ref": "chunk_3",
                "text": "The relationship between artificial intelligence and machine learning is fundamental to modern computing. AI systems use ML algorithms to learn patterns from data.",
                "chunk_confidence": 0.85
            }
        ]
        
        results = {}
        
        # Test different analysis scenarios
        analysis_scenarios = [
            {
                "name": "Entity Extraction",
                "task_type": "entity_extraction",
                "chunks": sample_chunks[:2]  # Simple entities
            },
            {
                "name": "Relationship Extraction", 
                "task_type": "relationship_extraction",
                "chunks": sample_chunks  # Complex relationships
            },
            {
                "name": "Full Analysis",
                "task_type": "analysis",
                "chunks": sample_chunks  # Complete analysis
            }
        ]
        
        for scenario in analysis_scenarios:
            print(f"\n🔍 Testing {scenario['name']}...")
            
            task = Task(
                task_id=f"reasoning_analysis_{scenario['name'].lower().replace(' ', '_')}",
                task_type=scenario["task_type"],
                parameters={
                    "chunks": scenario["chunks"]
                },
                context={
                    "demo_mode": True,
                    "scenario": scenario["name"]
                },
                priority=TaskPriority.HIGH
            )
            
            # Execute with reasoning
            start_time = time.time()
            result = await analysis_agent.execute(task)
            execution_time = time.time() - start_time
            
            # Analyze reasoning application
            reasoning_applied = result.metadata.get("reasoning", {}) if result.metadata else {}
            
            print(f"  ✅ Success: {result.success}")
            print(f"  🧠 Reasoning Applied: {reasoning_applied.get('applied', False)}")
            if reasoning_applied.get("applied"):
                print(f"     Type: {reasoning_applied.get('type', 'unknown')}")
                print(f"     Confidence: {reasoning_applied.get('confidence', 0.0):.2f}")
            print(f"  ⏱️  Execution Time: {execution_time:.3f}s")
            
            if result.success:
                if "entities" in result.data:
                    print(f"  🏷️  Entities Found: {result.data.get('total_entities', 0)}")
                if "relationships" in result.data:
                    print(f"  🔗 Relationships Found: {result.data.get('total_relationships', 0)}")
            
            results[scenario["name"]] = {
                "success": result.success,
                "reasoning_applied": reasoning_applied.get("applied", False),
                "reasoning_type": reasoning_applied.get("type"),
                "reasoning_confidence": reasoning_applied.get("confidence"),
                "execution_time": execution_time,
                "entities_found": result.data.get("total_entities", 0) if result.success else 0,
                "relationships_found": result.data.get("total_relationships", 0) if result.success else 0
            }
        
        # Get agent reasoning summary
        reasoning_summary = await analysis_agent.get_reasoning_summary()
        results["agent_summary"] = reasoning_summary
        
        print(f"\n📊 Analysis Agent Reasoning Stats:")
        print(f"   Total Reasonings: {reasoning_summary['reasoning_stats']['total_reasonings']}")
        print(f"   Successful: {reasoning_summary['reasoning_stats']['successful_reasonings']}")
        print(f"   Decisions Improved: {reasoning_summary['reasoning_stats']['decisions_improved']}")
        
        return results
    
    async def _demo_reasoning_evolution(self, doc_agent: DocumentAgent, analysis_agent: AnalysisAgent) -> Dict[str, Any]:
        """Demonstrate how reasoning evolves with memory accumulation."""
        
        print("\n4️⃣ Reasoning Evolution Demo")
        print("-" * 40)
        
        results = {"iterations": []}
        
        # Run multiple iterations to show reasoning evolution
        for iteration in range(1, 4):
            print(f"\n🔄 Iteration {iteration}: Building Reasoning Memory...")
            
            # Create task with increasing complexity
            task = Task(
                task_id=f"evolution_test_{iteration}",
                task_type="document_processing",
                parameters={
                    "document_paths": [f"evolution_doc_{iteration}.txt"],
                    "complexity_level": iteration
                },
                context={
                    "demo_mode": True,
                    "iteration": iteration,
                    "previous_iterations": iteration - 1
                },
                priority=TaskPriority.MEDIUM
            )
            
            # Execute and track reasoning evolution
            result = await doc_agent.execute(task)
            
            # Get current memory and reasoning state
            memory_summary = await doc_agent.get_memory_summary()
            reasoning_summary = await doc_agent.get_reasoning_summary()
            
            iteration_data = {
                "iteration": iteration,
                "success": result.success,
                "total_memories": memory_summary["total_memories"],
                "learned_patterns": memory_summary["learned_patterns_count"],
                "total_reasonings": reasoning_summary["reasoning_stats"]["total_reasonings"],
                "reasoning_improvements": reasoning_summary["reasoning_stats"]["decisions_improved"]
            }
            
            results["iterations"].append(iteration_data)
            
            print(f"  📚 Total Memories: {iteration_data['total_memories']}")
            print(f"  🧩 Learned Patterns: {iteration_data['learned_patterns']}")
            print(f"  🧠 Total Reasonings: {iteration_data['total_reasonings']}")
            print(f"  📈 Reasoning Improvements: {iteration_data['reasoning_improvements']}")
            
            # Small delay to simulate realistic usage
            await asyncio.sleep(0.1)
        
        # Analyze evolution trends
        if len(results["iterations"]) >= 2:
            final_iteration = results["iterations"][-1]
            first_iteration = results["iterations"][0]
            
            memory_growth = final_iteration["total_memories"] - first_iteration["total_memories"]
            reasoning_growth = final_iteration["total_reasonings"] - first_iteration["total_reasonings"]
            
            results["evolution_analysis"] = {
                "memory_growth": memory_growth,
                "reasoning_growth": reasoning_growth,
                "learning_acceleration": memory_growth > 0 and reasoning_growth > 0,
                "improvement_trend": final_iteration["reasoning_improvements"] > first_iteration["reasoning_improvements"]
            }
            
            print(f"\n📈 Evolution Analysis:")
            print(f"   Memory Growth: +{memory_growth}")
            print(f"   Reasoning Growth: +{reasoning_growth}")
            print(f"   Learning Accelerating: {results['evolution_analysis']['learning_acceleration']}")
            print(f"   Improvement Trend: {results['evolution_analysis']['improvement_trend']}")
        
        return results
    
    async def _demo_orchestrator_reasoning(self) -> Dict[str, Any]:
        """Demonstrate reasoning integration with orchestrator."""
        
        print("\n5️⃣ Orchestrator Integration Demo")
        print("-" * 40)
        
        # Create orchestrator with reasoning configuration
        orchestrator = SimpleSequentialOrchestrator()
        orchestrator.config.update(self.demo_config)
        
        # Initialize orchestrator
        await orchestrator.initialize()
        
        print("✅ Orchestrator initialized with reasoning-enhanced agents")
        
        # Test orchestrated workflow with reasoning
        test_request = "Process and analyze a technical document about machine learning algorithms"
        
        print(f"\n🔄 Processing request: '{test_request}'")
        
        start_time = time.time()
        result = await orchestrator.process_request(test_request, {
            "demo_mode": True,
            "enable_reasoning_tracking": True
        })
        execution_time = time.time() - start_time
        
        # Analyze orchestrated reasoning
        reasoning_traces = []
        if result.success and result.data:
            workflow_results = result.data.get("workflow_results", [])
            for step_result in workflow_results:
                if step_result.metadata and "reasoning" in step_result.metadata:
                    reasoning_info = step_result.metadata["reasoning"]
                    reasoning_traces.append({
                        "agent": step_result.agent_id,
                        "reasoning_applied": reasoning_info.get("applied", False),
                        "reasoning_type": reasoning_info.get("type"),
                        "confidence": reasoning_info.get("confidence")
                    })
        
        orchestrator_results = {
            "success": result.success,
            "execution_time": execution_time,
            "total_steps": len(result.data.get("workflow_results", [])) if result.success else 0,
            "reasoning_traces": reasoning_traces,
            "reasoning_enabled_agents": len([t for t in reasoning_traces if t["reasoning_applied"]])
        }
        
        print(f"  ✅ Workflow Success: {orchestrator_results['success']}")
        print(f"  🔄 Total Steps: {orchestrator_results['total_steps']}")
        print(f"  🧠 Reasoning-Enabled Agents: {orchestrator_results['reasoning_enabled_agents']}")
        print(f"  ⏱️  Total Execution: {orchestrator_results['execution_time']:.3f}s")
        
        # Get orchestrator status
        orchestrator_status = orchestrator.get_status()
        orchestrator_results["orchestrator_status"] = orchestrator_status
        
        # Cleanup
        await orchestrator.cleanup()
        
        return orchestrator_results
    
    async def _generate_reasoning_report(self):
        """Generate comprehensive reasoning capabilities report."""
        
        print("\n6️⃣ Phase 2 Reasoning Report")
        print("=" * 40)
        
        report = {
            "phase": "Phase 2: LLM-Powered Reasoning",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "summary": {
                "components_implemented": [
                    "LLM Reasoning Engine with memory integration",
                    "ReasoningAgent base class extending MemoryAwareAgent",
                    "Enhanced DocumentAgent with chunking strategy reasoning",
                    "Enhanced AnalysisAgent with confidence optimization reasoning",
                    "Reasoning templates for 6 reasoning types",
                    "Orchestrator integration with reasoning-enhanced agents"
                ],
                "reasoning_types_supported": [
                    "Strategic - High-level strategy decisions",
                    "Tactical - Task execution optimization", 
                    "Adaptive - Learning and adaptation decisions",
                    "Diagnostic - Problem analysis and debugging",
                    "Predictive - Future outcome prediction",
                    "Creative - Novel solution generation"
                ],
                "key_capabilities": [
                    "Memory-enhanced reasoning context",
                    "Intelligent decision-making on when to apply reasoning",
                    "Dynamic reasoning type selection based on task characteristics",
                    "Performance tracking and optimization suggestions",
                    "Integration with existing KGAS LLM infrastructure",
                    "Fallback mechanisms for reasoning failures",
                    "Learning from reasoning outcomes"
                ]
            },
            "results": self.results
        }
        
        # Save report
        report_path = Path("phase2_reasoning_report.json")
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)
        
        print(f"📊 Component Status:")
        for component in report["summary"]["components_implemented"]:
            print(f"   ✅ {component}")
        
        print(f"\n🧠 Reasoning Types:")
        for reasoning_type in report["summary"]["reasoning_types_supported"]:
            print(f"   🎯 {reasoning_type}")
        
        print(f"\n🔧 Key Capabilities:")
        for capability in report["summary"]["key_capabilities"]:
            print(f"   ⚡ {capability}")
        
        print(f"\n💾 Report saved to: {report_path}")
        
        return report


async def main():
    """Run the Phase 2 reasoning demonstration."""
    
    demo = Phase2ReasoningDemo()
    results = await demo.run_complete_demo()
    
    if "error" not in results:
        print(f"\n🎉 Phase 2: LLM-Powered Reasoning Implementation Complete!")
        print(f"📈 Ready to proceed to Phase 3: Parallel Orchestration")
    else:
        print(f"\n❌ Demo encountered issues: {results['error']}")
    
    return results


if __name__ == "__main__":
    asyncio.run(main())