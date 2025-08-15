#!/usr/bin/env python3
"""
Memory System Demonstration Script.

This script demonstrates the complete memory-aware agent system,
showing how agents learn from experience and adapt their behavior.
"""

import asyncio
import tempfile
from pathlib import Path
import json

# Import memory system components
from src.orchestration.memory import AgentMemory, MemoryType, MemoryQuery
from src.orchestration.memory_agent import MemoryAwareAgent
from src.orchestration.memory_debug import MemoryDebugger, MemoryVisualizer, debug_agent_memory
from src.orchestration.base import Task, Result
from src.orchestration.mcp_adapter import MCPToolAdapter


class DemoAgent(MemoryAwareAgent):
    """Demo agent for showcasing memory capabilities."""
    
    def __init__(self, agent_id: str, memory_config: dict = None):
        super().__init__(agent_id, memory_config)
        self.simulation_mode = True  # For demo purposes
    
    def get_capabilities(self):
        return ["demo_task", "document_processing", "analysis"]
    
    def can_handle(self, task_type: str) -> bool:
        return task_type in self.get_capabilities()
    
    async def _execute_without_memory(self, task: Task) -> Result:
        """Fallback execution without memory context."""
        # Simulate some work
        await asyncio.sleep(0.1)
        
        return self._create_result(
            success=True,
            data={
                "task_type": task.task_type,
                "processed": True,
                "mode": "without_memory",
                "simulation": self.simulation_mode
            },
            task=task,
            execution_time=0.1
        )
    
    async def _execute_with_memory(self, task: Task, memory_context) -> Result:
        """Execute with memory-enhanced capabilities."""
        # Simulate memory-enhanced processing
        await asyncio.sleep(0.05)  # Faster due to learned optimizations
        
        # Use memory context to enhance execution
        data = {
            "task_type": task.task_type,
            "processed": True,
            "mode": "with_memory",
            "simulation": self.simulation_mode
        }
        
        # Apply learned patterns
        patterns = memory_context.get("learned_patterns", [])
        if patterns:
            data["patterns_applied"] = len(patterns)
            data["optimization_level"] = min(1.0, len(patterns) * 0.2)
        
        # Use learned procedures
        procedures = memory_context.get("procedures", [])
        if procedures:
            data["procedures_available"] = len(procedures)
            data["best_procedure"] = procedures[0]["name"] if procedures else None
        
        # Check for successful executions
        relevant_executions = memory_context.get("relevant_executions", [])
        successful_count = sum(1 for exec in relevant_executions if exec.get("success"))
        
        if successful_count > 0:
            data["success_rate"] = successful_count / len(relevant_executions)
            data["confidence_boost"] = min(0.5, successful_count * 0.1)
        
        return self._create_result(
            success=True,
            data=data,
            task=task,
            execution_time=0.05
        )


async def demonstrate_memory_learning():
    """Demonstrate how agents learn and improve over time."""
    
    print("🧠 Memory System Demonstration")
    print("=" * 50)
    
    # Create temporary database
    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = Path(temp_dir) / "demo_agent.db"
        
        # Configure memory system
        memory_config = {
            "db_path": str(db_path),
            "enable_learning": True,
            "max_context_memories": 10
        }
        
        # Create memory-aware agent
        agent = DemoAgent("demo_agent", memory_config)
        
        print(f"📝 Created agent: {agent.agent_id}")
        print(f"🗄️ Memory database: {db_path}")
        print()
        
        # Simulate multiple task executions to build memory
        task_types = ["demo_task", "document_processing", "analysis"]
        
        print("🔄 Executing tasks to build memory...")
        
        for iteration in range(8):
            task_type = task_types[iteration % len(task_types)]
            
            task = Task(
                task_type=task_type,
                parameters={
                    "iteration": iteration,
                    "complexity": "low" if iteration < 3 else "medium" if iteration < 6 else "high",
                    "data_size": iteration * 100,
                    "priority": "normal"
                },
                context={"demo": True, "batch": iteration // 3}
            )
            
            print(f"  Task {iteration + 1}: {task_type} (complexity: {task.parameters['complexity']})")
            
            # Execute task
            result = await agent.execute(task)
            
            if result.success:
                optimization = result.data.get("optimization_level", 0)
                patterns = result.data.get("patterns_applied", 0)
                procedures = result.data.get("procedures_available", 0)
                
                print(f"    ✓ Success | Patterns: {patterns} | Procedures: {procedures} | Optimization: {optimization:.1%}")
            else:
                print(f"    ✗ Failed: {result.error}")
            
            # Show memory growth every few iterations
            if (iteration + 1) % 3 == 0:
                summary = await agent.get_memory_summary()
                total_memories = summary["memory_stats"]["total_memories"]
                print(f"    📊 Memory state: {total_memories} total memories")
                
                # Show learned strategies
                strategies = await agent.get_learned_strategies(task_type)
                if strategies:
                    best_strategy = strategies[0]
                    print(f"    🎯 Best strategy: {best_strategy['name']} (success rate: {best_strategy['success_rate']:.1%})")
                
                print()
        
        print("🧪 Memory Analysis")
        print("-" * 30)
        
        # Analyze final memory state
        final_summary = await agent.get_memory_summary()
        memory_stats = final_summary["memory_stats"]
        
        print(f"Total memories: {memory_stats['total_memories']}")
        print(f"Recent activity: {memory_stats['recent_memories_7days']} memories in last 7 days")
        print(f"Database size: {memory_stats['database_size_bytes']} bytes")
        print()
        
        # Show memory distribution
        print("Memory type distribution:")
        for mem_type, stats in memory_stats.get("memories_by_type", {}).items():
            count = stats["count"]
            avg_importance = stats["avg_importance"]
            print(f"  {mem_type.title()}: {count} memories (avg importance: {avg_importance:.2f})")
        print()
        
        # Test parameter recommendations
        print("🎛️ Parameter Recommendations")
        print("-" * 30)
        
        for task_type in task_types[:2]:  # Test first two task types
            recommendations = await agent.get_parameter_recommendations(task_type)
            confidence = recommendations["confidence"]
            
            print(f"{task_type}: confidence {confidence:.1%}")
            
            if recommendations["recommended_parameters"]:
                print("  Recommended parameters:")
                for param, value in recommendations["recommended_parameters"].items():
                    print(f"    {param}: {value}")
            
            if recommendations["avoid_parameters"]:
                print("  Avoid parameters:")
                for param, value in recommendations["avoid_parameters"].items():
                    print(f"    {param}: {value}")
            print()
        
        # Test memory debugging
        print("🔍 Memory Debugging")
        print("-" * 30)
        
        debugger = MemoryDebugger()
        analysis = await debugger.analyze_agent_memory("demo_agent")
        
        # Show health assessment
        health = analysis["health"]
        print(f"Health score: {health['health_score']:.2f}/1.0 ({health['status']})")
        
        if health["issues"]:
            print("Issues found:")
            for issue in health["issues"]:
                print(f"  - {issue}")
        
        if health["recommendations"]:
            print("Recommendations:")
            for rec in health["recommendations"]:
                print(f"  - {rec}")
        print()
        
        # Show learning velocity
        patterns = analysis["patterns"]
        if "learning_velocity" in patterns:
            velocity = patterns["learning_velocity"]
            print(f"Learning velocity: {velocity['daily_learning_rate']:.1f} memories/day")
            print(f"Learning trend: {velocity['learning_trend']}")
            print()
        
        # Generate and display memory report
        print("📋 Memory Report")
        print("-" * 30)
        
        visualizer = MemoryVisualizer()
        report = visualizer.create_memory_report(analysis)
        
        # Print first part of report
        report_lines = report.split('\n')
        for line in report_lines[:25]:  # Show first 25 lines
            print(line)
        
        if len(report_lines) > 25:
            print(f"... ({len(report_lines) - 25} more lines)")
        print()
        
        # Test memory queries
        print("🔎 Memory Queries")
        print("-" * 30)
        
        # Query recent episodic memories
        recent_query = MemoryQuery(
            agent_id="demo_agent",
            memory_types=[MemoryType.EPISODIC],
            max_results=3
        )
        
        recent_memories = await agent.memory.query_memories(recent_query)
        print(f"Recent episodic memories ({len(recent_memories)}):")
        
        for i, memory in enumerate(recent_memories[:3], 1):
            task_type = memory.content.get("task_type", "unknown")
            success = memory.content.get("result_success", False)
            execution_time = memory.content.get("execution_time", 0)
            
            print(f"  {i}. {task_type} - {'✓' if success else '✗'} ({execution_time:.3f}s)")
        print()
        
        # Query learned patterns
        pattern_query = MemoryQuery(
            agent_id="demo_agent",
            memory_types=[MemoryType.SEMANTIC],
            content_keywords=["pattern"],
            max_results=3
        )
        
        pattern_memories = await agent.memory.query_memories(pattern_query)
        print(f"Learned patterns ({len(pattern_memories)}):")
        
        for i, memory in enumerate(pattern_memories[:3], 1):
            pattern_type = memory.content.get("pattern_type", "unknown")
            confidence = memory.content.get("pattern_data", {}).get("confidence", 0)
            
            print(f"  {i}. {pattern_type} (confidence: {confidence:.2f})")
        print()
        
        print("✅ Memory system demonstration completed!")
        print(f"📁 Memory database saved at: {db_path}")
        print(f"🧠 Agent learned from {memory_stats['total_memories']} experiences")


async def demonstrate_memory_persistence():
    """Demonstrate memory persistence across agent restarts."""
    
    print("\n" + "=" * 50)
    print("🔄 Memory Persistence Demonstration")
    print("=" * 50)
    
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as temp_file:
        db_path = temp_file.name
    
    try:
        # First agent instance
        print("Creating first agent instance...")
        agent1 = DemoAgent("persistent_agent", {"db_path": db_path})
        
        # Execute some tasks
        for i in range(3):
            task = Task(task_type="demo_task", parameters={"run": i})
            result = await agent1.execute(task)
            print(f"  Task {i+1}: {'✓' if result.success else '✗'}")
        
        # Get memory count
        summary1 = await agent1.get_memory_summary()
        count1 = summary1["memory_stats"]["total_memories"]
        print(f"First instance memory count: {count1}")
        
        # Create second agent instance with same database
        print("\nCreating second agent instance with same database...")
        agent2 = DemoAgent("persistent_agent", {"db_path": db_path})
        
        # Check memory persistence
        summary2 = await agent2.get_memory_summary()
        count2 = summary2["memory_stats"]["total_memories"]
        print(f"Second instance memory count: {count2}")
        
        if count1 == count2:
            print("✅ Memory persisted successfully across agent instances!")
        else:
            print("❌ Memory persistence failed")
        
        # Execute more tasks with second instance
        for i in range(2):
            task = Task(task_type="demo_task", parameters={"run": i + 10})
            result = await agent2.execute(task)
            print(f"  Additional task {i+1}: {'✓' if result.success else '✗'}")
        
        # Final memory count
        final_summary = await agent2.get_memory_summary()
        final_count = final_summary["memory_stats"]["total_memories"]
        print(f"Final memory count: {final_count}")
        
        if final_count > count2:
            print("✅ Memory continued to grow with second instance!")
        
    finally:
        Path(db_path).unlink(missing_ok=True)


if __name__ == "__main__":
    print("🚀 Starting Memory System Demo")
    print()
    
    async def run_demo():
        await demonstrate_memory_learning()
        await demonstrate_memory_persistence()
        print("\n🎉 Demo completed successfully!")
    
    asyncio.run(run_demo())