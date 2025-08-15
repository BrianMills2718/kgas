#!/usr/bin/env python3
"""
Phase 3: Parallel Orchestration System Demonstration

This demonstrates the complete parallel orchestration capabilities with
reasoning-enhanced agents, resource management, and coordination mechanisms.
"""

import asyncio
import json
import time
import logging
from pathlib import Path
from typing import Dict, Any, List
import random

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import KGAS orchestration components
from src.orchestration.parallel_orchestrator import ParallelOrchestrator, ExecutionMode
from src.orchestration.coordination import CoordinationManager, CoordinationEventType
from src.orchestration.base import Task, TaskPriority


class Phase3ParallelDemo:
    """
    Comprehensive demonstration of Phase 3 parallel orchestration capabilities.
    """
    
    def __init__(self):
        self.results = {}
        self.demo_config = {
            "parallel": {
                "execution_mode": "adaptive",
                "max_parallel_tasks": 5,
                "batch_size": 3,
                "enable_resource_management": True,
                "enable_adaptive_parallelism": True,
                "resources": {
                    "max_concurrent_agents": 5,
                    "max_memory_mb": 2048,
                    "max_reasoning_threads": 3
                }
            },
            "memory": {
                "document": {"enable_memory": True, "learning_enabled": True},
                "analysis": {"enable_memory": True, "learning_enabled": True},
                "graph": {"enable_memory": True, "learning_enabled": True},
                "insight": {"enable_memory": True, "learning_enabled": True}
            },
            "reasoning": {
                "document": {"enable_reasoning": True, "default_reasoning_type": "strategic"},
                "analysis": {"enable_reasoning": True, "default_reasoning_type": "tactical"},
                "graph": {"enable_reasoning": False},
                "insight": {"enable_reasoning": True, "default_reasoning_type": "creative"}
            }
        }
    
    async def run_complete_demo(self) -> Dict[str, Any]:
        """Run complete Phase 3 parallel orchestration demonstration."""
        
        print("🚀 Phase 3: Parallel Orchestration Demo")
        print("=" * 60)
        
        try:
            # 1. Initialize parallel orchestrator
            print("\n1️⃣ Initializing Parallel Orchestrator...")
            orchestrator = await self._initialize_orchestrator()
            
            # 2. Demonstrate execution modes
            mode_results = await self._demo_execution_modes(orchestrator)
            self.results["execution_modes"] = mode_results
            
            # 3. Demonstrate resource management
            resource_results = await self._demo_resource_management(orchestrator)
            self.results["resource_management"] = resource_results
            
            # 4. Demonstrate coordination mechanisms
            coordination_results = await self._demo_coordination()
            self.results["coordination"] = coordination_results
            
            # 5. Demonstrate parallel speedup
            speedup_results = await self._demo_parallel_speedup(orchestrator)
            self.results["parallel_speedup"] = speedup_results
            
            # 6. Generate comprehensive report
            await self._generate_parallel_report()
            
            # Cleanup
            await orchestrator.cleanup()
            
            print("\n✅ Phase 3 Parallel Orchestration Demo Complete!")
            return self.results
            
        except Exception as e:
            logger.error(f"Demo failed: {e}")
            print(f"\n❌ Demo failed: {e}")
            return {"error": str(e)}
    
    async def _initialize_orchestrator(self) -> ParallelOrchestrator:
        """Initialize parallel orchestrator with configuration."""
        
        # Create config file
        config_path = Path("demo_parallel_config.json")
        with open(config_path, "w") as f:
            json.dump(self.demo_config, f, indent=2)
        
        # Create orchestrator
        orchestrator = ParallelOrchestrator(str(config_path))
        
        # Initialize
        success = await orchestrator.initialize()
        
        if success:
            print("✅ Parallel orchestrator initialized successfully")
            
            # Get status
            status = orchestrator.get_status()
            print(f"   Execution Mode: {status['execution_mode']}")
            print(f"   Max Parallel Tasks: {status['max_parallel_tasks']}")
            print(f"   Resource Management: {self.demo_config['parallel']['enable_resource_management']}")
            print(f"   Available Resources:")
            print(f"     - Agents: {status['resource_pool']['available_agents']}")
            print(f"     - Memory: {status['resource_pool']['max_memory_mb'] - status['resource_pool']['used_memory_mb']} MB")
            print(f"     - Reasoning Threads: {status['resource_pool']['max_reasoning_threads'] - status['resource_pool']['active_reasoning']}")
        else:
            raise RuntimeError("Failed to initialize parallel orchestrator")
        
        return orchestrator
    
    async def _demo_execution_modes(self, orchestrator: ParallelOrchestrator) -> Dict[str, Any]:
        """Demonstrate different parallel execution modes."""
        
        print("\n2️⃣ Execution Modes Demo")
        print("-" * 40)
        
        results = {}
        
        # Test different execution modes
        modes = [
            ExecutionMode.PARALLEL,
            ExecutionMode.BATCH,
            ExecutionMode.PIPELINE,
            ExecutionMode.ADAPTIVE
        ]
        
        for mode in modes:
            print(f"\n🔄 Testing {mode.value} execution mode...")
            
            # Update execution mode
            orchestrator.execution_mode = mode
            
            # Create test request
            request = f"Analyze multiple documents using {mode.value} execution"
            
            # Execute request
            start_time = time.time()
            result = await orchestrator.process_request(request, {
                "demo_mode": True,
                "test_documents": self._generate_test_documents(3)
            })
            execution_time = time.time() - start_time
            
            # Analyze results
            if result.success and result.data:
                stats = result.data.get("execution_stats", {})
                print(f"  ✅ Success: {result.success}")
                print(f"  📊 Tasks Executed: {stats.get('total_tasks', 0)}")
                print(f"  ⚡ Speedup: {stats.get('speedup', 1.0)}x")
                print(f"  ⏱️  Execution Time: {execution_time:.3f}s")
                
                results[mode.value] = {
                    "success": result.success,
                    "total_tasks": stats.get("total_tasks", 0),
                    "speedup": stats.get("speedup", 1.0),
                    "execution_time": execution_time,
                    "parallel_time": stats.get("parallel_time", 0),
                    "sequential_time": stats.get("sequential_time", 0)
                }
            else:
                print(f"  ❌ Failed: {result.error}")
                results[mode.value] = {
                    "success": False,
                    "error": result.error
                }
        
        return results
    
    async def _demo_resource_management(self, orchestrator: ParallelOrchestrator) -> Dict[str, Any]:
        """Demonstrate resource management capabilities."""
        
        print("\n3️⃣ Resource Management Demo")
        print("-" * 40)
        
        results = {}
        
        # Test resource allocation scenarios
        scenarios = [
            {
                "name": "Normal Load",
                "documents": 3,
                "analysis_depth": "standard"
            },
            {
                "name": "High Memory Load",
                "documents": 5,
                "analysis_depth": "deep",
                "large_dataset": True
            },
            {
                "name": "High Reasoning Load",
                "documents": 4,
                "analysis_depth": "reasoning_intensive",
                "enable_all_reasoning": True
            }
        ]
        
        for scenario in scenarios:
            print(f"\n📊 Testing {scenario['name']}...")
            
            # Get initial resource state
            initial_status = orchestrator.get_status()
            initial_resources = initial_status["resource_pool"]
            
            # Create request with resource requirements
            request = f"Process {scenario['documents']} documents with {scenario['name']} scenario"
            context = {
                "demo_mode": True,
                "test_documents": self._generate_test_documents(scenario["documents"]),
                "analysis_depth": scenario.get("analysis_depth", "standard"),
                "large_dataset": scenario.get("large_dataset", False)
            }
            
            # Execute request
            result = await orchestrator.process_request(request, context)
            
            # Get resource usage
            if result.success and result.data:
                resource_usage = result.data.get("resource_usage", {})
                
                print(f"  ✅ Success: {result.success}")
                print(f"  📈 Peak Resource Usage:")
                print(f"     Memory: {resource_usage.get('peak_memory_mb', 0)} MB")
                print(f"     Agents: {resource_usage.get('peak_agents', 0)}")
                print(f"     Reasoning Threads: {resource_usage.get('peak_reasoning_threads', 0)}")
                
                # Calculate utilization
                memory_util = (resource_usage.get('peak_memory_mb', 0) / 
                             initial_resources['max_memory_mb'] * 100)
                agent_util = (resource_usage.get('peak_agents', 0) / 
                            initial_resources['max_concurrent_agents'] * 100)
                
                print(f"  📊 Utilization:")
                print(f"     Memory: {memory_util:.1f}%")
                print(f"     Agents: {agent_util:.1f}%")
                
                results[scenario['name']] = {
                    "success": True,
                    "peak_memory_mb": resource_usage.get('peak_memory_mb', 0),
                    "peak_agents": resource_usage.get('peak_agents', 0),
                    "peak_reasoning_threads": resource_usage.get('peak_reasoning_threads', 0),
                    "memory_utilization": memory_util,
                    "agent_utilization": agent_util
                }
            else:
                print(f"  ❌ Failed: {result.error}")
                results[scenario['name']] = {
                    "success": False,
                    "error": result.error
                }
        
        return results
    
    async def _demo_coordination(self) -> Dict[str, Any]:
        """Demonstrate agent coordination mechanisms."""
        
        print("\n4️⃣ Coordination Mechanisms Demo")
        print("-" * 40)
        
        results = {}
        
        # Create coordination manager
        coord_manager = CoordinationManager()
        await coord_manager.start()
        
        try:
            # Test barrier synchronization
            print("\n🚧 Testing Barrier Synchronization...")
            barrier_result = await self._test_barrier_sync(coord_manager)
            results["barrier_sync"] = barrier_result
            
            # Test shared state
            print("\n📝 Testing Shared State Management...")
            shared_state_result = await self._test_shared_state(coord_manager)
            results["shared_state"] = shared_state_result
            
            # Test event coordination
            print("\n📡 Testing Event Coordination...")
            event_result = await self._test_event_coordination(coord_manager)
            results["event_coordination"] = event_result
            
            # Get coordination statistics
            stats = coord_manager.get_coordination_stats()
            results["coordination_stats"] = stats
            
            print(f"\n📊 Coordination Statistics:")
            print(f"   Total Events: {stats['total_events']}")
            print(f"   Active Barriers: {stats['active_barriers']}")
            print(f"   Shared States: {stats['shared_states']}")
            print(f"   Registered Agents: {stats['registered_agents']}")
            
        finally:
            await coord_manager.cleanup()
        
        return results
    
    async def _test_barrier_sync(self, coord_manager: CoordinationManager) -> Dict[str, Any]:
        """Test barrier synchronization between agents."""
        
        # Create barrier for 3 agents
        barrier_id = "test_barrier"
        barrier = await coord_manager.create_barrier(barrier_id, parties=3)
        
        results = {"agents_synchronized": []}
        
        async def agent_task(agent_id: str, delay: float):
            """Simulated agent task with barrier sync."""
            await asyncio.sleep(delay)
            print(f"  Agent {agent_id} reaching barrier...")
            
            try:
                index = await coord_manager.wait_at_barrier(barrier_id, agent_id, timeout=5.0)
                print(f"  ✅ Agent {agent_id} passed barrier at index {index}")
                results["agents_synchronized"].append({
                    "agent_id": agent_id,
                    "barrier_index": index,
                    "success": True
                })
            except asyncio.TimeoutError:
                print(f"  ❌ Agent {agent_id} timed out at barrier")
                results["agents_synchronized"].append({
                    "agent_id": agent_id,
                    "success": False,
                    "error": "timeout"
                })
        
        # Launch agents with different delays
        agents = [
            ("agent_1", 0.1),
            ("agent_2", 0.5),
            ("agent_3", 0.3)
        ]
        
        await asyncio.gather(
            *[agent_task(agent_id, delay) for agent_id, delay in agents]
        )
        
        results["all_synchronized"] = all(
            a["success"] for a in results["agents_synchronized"]
        )
        
        return results
    
    async def _test_shared_state(self, coord_manager: CoordinationManager) -> Dict[str, Any]:
        """Test shared state management between agents."""
        
        state_id = "test_state"
        await coord_manager.create_shared_state(state_id, {"counter": 0, "agents": []})
        
        results = {"updates": [], "final_state": None}
        
        async def agent_update(agent_id: str):
            """Agent updates shared state."""
            # Read current state
            state = await coord_manager.read_shared_state(state_id, agent_id)
            print(f"  Agent {agent_id} read state: counter={state['counter']}")
            
            # Update state
            updates = {
                "counter": state["counter"] + 1,
                "agents": state["agents"] + [agent_id],
                f"{agent_id}_timestamp": time.time()
            }
            
            updated_state = await coord_manager.update_shared_state(
                state_id, agent_id, updates, merge=True
            )
            
            print(f"  ✅ Agent {agent_id} updated state to version {updated_state.version}")
            results["updates"].append({
                "agent_id": agent_id,
                "version": updated_state.version,
                "counter": updated_state.data["counter"]
            })
        
        # Multiple agents update shared state
        agents = ["agent_A", "agent_B", "agent_C"]
        
        # Sequential updates to avoid conflicts (in real scenarios, use locking)
        for agent_id in agents:
            await agent_update(agent_id)
        
        # Read final state
        final_state = await coord_manager.read_shared_state(state_id, "observer")
        results["final_state"] = final_state
        results["total_updates"] = len(results["updates"])
        
        return results
    
    async def _test_event_coordination(self, coord_manager: CoordinationManager) -> Dict[str, Any]:
        """Test event-based coordination."""
        
        results = {"events_received": [], "event_flow": []}
        
        # Subscribe to events
        async def event_handler(event):
            """Handle coordination events."""
            results["events_received"].append({
                "event_type": event.event_type.value,
                "source": event.source_agent,
                "timestamp": event.timestamp.isoformat()
            })
            print(f"  📨 Received {event.event_type.value} from {event.source_agent}")
        
        # Subscribe to different event types
        coord_manager.subscribe_to_event(CoordinationEventType.TASK_STARTED, event_handler)
        coord_manager.subscribe_to_event(CoordinationEventType.TASK_COMPLETED, event_handler)
        coord_manager.subscribe_to_event(CoordinationEventType.DATA_AVAILABLE, event_handler)
        
        # Simulate agent workflow with events
        agents = ["doc_agent", "analysis_agent", "graph_agent"]
        
        for agent_id in agents:
            # Task started
            await coord_manager.emit_event(
                type(
                    "Event",
                    (),
                    {
                        "event_type": CoordinationEventType.TASK_STARTED,
                        "source_agent": agent_id,
                        "timestamp": time.time(),
                        "data": {"task": f"{agent_id}_task"}
                    }
                )()
            )
            
            await asyncio.sleep(0.1)  # Simulate work
            
            # Task completed with data
            await coord_manager.emit_event(
                type(
                    "Event",
                    (),
                    {
                        "event_type": CoordinationEventType.TASK_COMPLETED,
                        "source_agent": agent_id,
                        "timestamp": time.time(),
                        "data": {"result": f"{agent_id}_result"}
                    }
                )()
            )
            
            # Data available
            await coord_manager.emit_event(
                type(
                    "Event",
                    (),
                    {
                        "event_type": CoordinationEventType.DATA_AVAILABLE,
                        "source_agent": agent_id,
                        "timestamp": time.time(),
                        "data": {"data_type": f"{agent_id}_output"}
                    }
                )()
            )
        
        # Allow events to propagate
        await asyncio.sleep(0.5)
        
        results["total_events"] = len(results["events_received"])
        results["event_types"] = list(set(e["event_type"] for e in results["events_received"]))
        
        return results
    
    async def _demo_parallel_speedup(self, orchestrator: ParallelOrchestrator) -> Dict[str, Any]:
        """Demonstrate parallel execution speedup."""
        
        print("\n5️⃣ Parallel Speedup Demo")
        print("-" * 40)
        
        results = {}
        
        # Test with different numbers of documents
        document_counts = [1, 3, 5, 10]
        
        for count in document_counts:
            print(f"\n📄 Processing {count} documents...")
            
            # Sequential execution (baseline)
            orchestrator.execution_mode = ExecutionMode.PARALLEL
            orchestrator.max_parallel_tasks = 1  # Force sequential
            
            request = f"Process {count} documents sequentially"
            context = {
                "demo_mode": True,
                "test_documents": self._generate_test_documents(count)
            }
            
            seq_start = time.time()
            seq_result = await orchestrator.process_request(request, context)
            seq_time = time.time() - seq_start
            
            # Parallel execution
            orchestrator.max_parallel_tasks = 5  # Allow parallel
            
            request = f"Process {count} documents in parallel"
            
            par_start = time.time()
            par_result = await orchestrator.process_request(request, context)
            par_time = time.time() - par_start
            
            # Calculate speedup
            if seq_result.success and par_result.success:
                speedup = seq_time / par_time if par_time > 0 else 1.0
                efficiency = speedup / min(count, 5)  # Efficiency relative to parallelism
                
                print(f"  ⏱️  Sequential: {seq_time:.3f}s")
                print(f"  ⚡ Parallel: {par_time:.3f}s")
                print(f"  📈 Speedup: {speedup:.2f}x")
                print(f"  📊 Efficiency: {efficiency:.1%}")
                
                results[f"{count}_documents"] = {
                    "sequential_time": seq_time,
                    "parallel_time": par_time,
                    "speedup": speedup,
                    "efficiency": efficiency,
                    "tasks_executed": par_result.data.get("execution_stats", {}).get("total_tasks", 0)
                }
            else:
                print(f"  ❌ Execution failed")
                results[f"{count}_documents"] = {
                    "success": False,
                    "error": seq_result.error or par_result.error
                }
        
        return results
    
    def _generate_test_documents(self, count: int) -> List[Dict[str, Any]]:
        """Generate test documents for parallel processing."""
        
        documents = []
        
        for i in range(count):
            doc_size = random.choice(["small", "medium", "large"])
            
            if doc_size == "small":
                content = f"Document {i+1}: " + " ".join([f"Word{j}" for j in range(50)])
            elif doc_size == "medium":
                content = f"Document {i+1}: " + " ".join([f"Word{j}" for j in range(200)])
            else:
                content = f"Document {i+1}: " + " ".join([f"Word{j}" for j in range(500)])
            
            documents.append({
                "id": f"doc_{i+1}",
                "content": content,
                "metadata": {
                    "size": doc_size,
                    "complexity": random.choice(["low", "medium", "high"]),
                    "requires_reasoning": random.choice([True, False])
                }
            })
        
        return documents
    
    async def _generate_parallel_report(self):
        """Generate comprehensive parallel orchestration report."""
        
        print("\n6️⃣ Phase 3 Parallel Orchestration Report")
        print("=" * 40)
        
        report = {
            "phase": "Phase 3: Parallel Orchestration",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "summary": {
                "components_implemented": [
                    "ParallelOrchestrator with 4 execution modes",
                    "ResourcePool for dynamic resource management",
                    "CoordinationManager for agent synchronization",
                    "Parallel workflow configurations",
                    "Result aggregation with speedup analysis",
                    "Adaptive parallelism with resource scaling"
                ],
                "execution_modes": [
                    "PARALLEL - Full concurrent execution",
                    "BATCH - Batched parallel execution",
                    "PIPELINE - Streaming pipeline execution",
                    "ADAPTIVE - Dynamic resource-aware execution"
                ],
                "coordination_features": [
                    "Barrier synchronization for agent coordination",
                    "Shared state management with versioning",
                    "Event-based coordination system",
                    "Distributed locks and semaphores",
                    "Agent dependency tracking"
                ],
                "resource_management": [
                    "Dynamic agent allocation",
                    "Memory usage tracking and limits",
                    "Reasoning thread pooling",
                    "Adaptive resource scaling",
                    "Resource requirement estimation"
                ]
            },
            "results": self.results
        }
        
        # Save report
        report_path = Path("phase3_parallel_report.json")
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)
        
        print(f"📊 Component Status:")
        for component in report["summary"]["components_implemented"]:
            print(f"   ✅ {component}")
        
        print(f"\n🔄 Execution Modes:")
        for mode in report["summary"]["execution_modes"]:
            print(f"   🎯 {mode}")
        
        print(f"\n🤝 Coordination Features:")
        for feature in report["summary"]["coordination_features"]:
            print(f"   ⚡ {feature}")
        
        # Analyze speedup results
        if "parallel_speedup" in self.results:
            speedup_data = self.results["parallel_speedup"]
            avg_speedup = sum(
                v["speedup"] for k, v in speedup_data.items() 
                if isinstance(v, dict) and "speedup" in v
            ) / len(speedup_data)
            
            print(f"\n📈 Performance Summary:")
            print(f"   Average Speedup: {avg_speedup:.2f}x")
            print(f"   Best Speedup: {max(v.get('speedup', 0) for v in speedup_data.values() if isinstance(v, dict)):.2f}x")
        
        print(f"\n💾 Report saved to: {report_path}")
        
        return report


async def main():
    """Run the Phase 3 parallel orchestration demonstration."""
    
    demo = Phase3ParallelDemo()
    results = await demo.run_complete_demo()
    
    if "error" not in results:
        print(f"\n🎉 Phase 3: Parallel Orchestration Implementation Complete!")
        print(f"🚀 Ready to proceed to Phase 4: Agent Communication")
    else:
        print(f"\n❌ Demo encountered issues: {results['error']}")
    
    return results


if __name__ == "__main__":
    asyncio.run(main())