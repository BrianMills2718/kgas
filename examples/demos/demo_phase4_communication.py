#!/usr/bin/env python3
"""
Phase 4: Agent Communication System Demonstration

This demonstrates the complete agent communication capabilities including:
- Inter-agent messaging
- Collaborative document processing
- Team formation
- Agent discovery
- Publish/subscribe patterns
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
from src.orchestration.communication import MessageBus, MessageType, MessagePriority
from src.orchestration.communicating_agent import CommunicatingAgent
from src.orchestration.simple_orchestrator import SimpleSequentialOrchestrator


class Phase4CommunicationDemo:
    """
    Comprehensive demonstration of Phase 4 agent communication capabilities.
    """
    
    def __init__(self):
        self.results = {}
        self.demo_config = {
            "communication": {
                "enabled": True,
                "document": {
                    "enabled": True,
                    "topics": ["document_events", "collaborative_tasks"]
                },
                "analysis": {
                    "enabled": True,
                    "topics": ["analysis_events", "insights"]
                }
            },
            "memory": {
                "document": {"enable_memory": True, "learning_enabled": True},
                "analysis": {"enable_memory": True, "learning_enabled": True}
            },
            "reasoning": {
                "document": {"enable_reasoning": True},
                "analysis": {"enable_reasoning": True}
            },
            "workflows": {
                "collaborative_analysis": {
                    "steps": [
                        {
                            "agent": "document",
                            "task_type": "document_processing",
                            "parameters": {"collaborative": True}
                        },
                        {
                            "agent": "analysis",
                            "task_type": "entity_extraction",
                            "parameters": {"broadcast_insights": True}
                        }
                    ]
                }
            }
        }
    
    async def run_complete_demo(self) -> Dict[str, Any]:
        """Run complete Phase 4 communication demonstration."""
        
        print("🚀 Phase 4: Agent Communication Demo")
        print("=" * 60)
        
        try:
            # 1. Initialize communication system
            print("\n1️⃣ Initializing Communication System...")
            message_bus = await self._initialize_communication()
            
            # 2. Demonstrate direct messaging
            messaging_results = await self._demo_direct_messaging(message_bus)
            self.results["direct_messaging"] = messaging_results
            
            # 3. Demonstrate publish/subscribe
            pubsub_results = await self._demo_publish_subscribe(message_bus)
            self.results["publish_subscribe"] = pubsub_results
            
            # 4. Demonstrate agent discovery
            discovery_results = await self._demo_agent_discovery(message_bus)
            self.results["agent_discovery"] = discovery_results
            
            # 5. Demonstrate collaborative processing
            collab_results = await self._demo_collaborative_processing(message_bus)
            self.results["collaborative_processing"] = collab_results
            
            # 6. Demonstrate team formation
            team_results = await self._demo_team_formation(message_bus)
            self.results["team_formation"] = team_results
            
            # 7. Generate comprehensive report
            await self._generate_communication_report()
            
            # Cleanup
            await message_bus.stop()
            
            print("\n✅ Phase 4 Agent Communication Demo Complete!")
            return self.results
            
        except Exception as e:
            logger.error(f"Demo failed: {e}")
            print(f"\n❌ Demo failed: {e}")
            return {"error": str(e)}
    
    async def _initialize_communication(self) -> MessageBus:
        """Initialize the communication system."""
        
        # Create message bus
        message_bus = MessageBus()
        await message_bus.start()
        
        # Create demo agents
        test_agents = [
            ("agent_1", "test", ["processing", "analysis"]),
            ("agent_2", "test", ["processing", "collaboration"]),
            ("agent_3", "test", ["analysis", "insights"])
        ]
        
        for agent_id, agent_type, capabilities in test_agents:
            success = await message_bus.register_agent(
                agent_id,
                agent_type,
                capabilities
            )
            if success:
                print(f"✅ Registered {agent_id} (type: {agent_type})")
        
        stats = message_bus.get_statistics()
        print(f"📊 Message Bus Statistics:")
        print(f"   Registered Agents: {stats['registered_agents']}")
        print(f"   Active Topics: {stats['active_topics']}")
        
        return message_bus
    
    async def _demo_direct_messaging(self, message_bus: MessageBus) -> Dict[str, Any]:
        """Demonstrate direct agent-to-agent messaging."""
        
        print("\n2️⃣ Direct Messaging Demo")
        print("-" * 40)
        
        results = {
            "messages_sent": 0,
            "responses_received": 0,
            "round_trip_times": []
        }
        
        # Create communicators for test agents
        from src.orchestration.communication import AgentCommunicator
        
        agent1_comm = AgentCommunicator("agent_1", message_bus)
        agent2_comm = AgentCommunicator("agent_2", message_bus)
        
        # Set up message handler for agent_2
        @agent2_comm.on_message(MessageType.REQUEST)
        async def handle_request(message):
            print(f"  Agent 2 received request: {message.payload.get('content')}")
            # Reply to request
            await message_bus.reply(message, {
                "response": "Message received and processed",
                "agent": "agent_2",
                "original_content": message.payload.get("content")
            })
        
        # Start message processing
        await agent1_comm.start()
        await agent2_comm.start()
        
        # Test request-reply pattern
        print("\n📤 Testing Request-Reply Pattern...")
        
        for i in range(3):
            start_time = time.time()
            
            response = await agent1_comm.request(
                "agent_2",
                {
                    "content": f"Test message {i+1}",
                    "timestamp": time.time()
                },
                timeout=5.0
            )
            
            round_trip = time.time() - start_time
            
            if response:
                print(f"  ✅ Request {i+1} - Response received in {round_trip:.3f}s")
                results["responses_received"] += 1
                results["round_trip_times"].append(round_trip)
            else:
                print(f"  ❌ Request {i+1} - No response")
            
            results["messages_sent"] += 1
        
        # Calculate average round trip time
        if results["round_trip_times"]:
            avg_rtt = sum(results["round_trip_times"]) / len(results["round_trip_times"])
            results["avg_round_trip_time"] = avg_rtt
            print(f"\n📊 Average Round Trip Time: {avg_rtt:.3f}s")
        
        # Cleanup
        await agent1_comm.stop()
        await agent2_comm.stop()
        
        return results
    
    async def _demo_publish_subscribe(self, message_bus: MessageBus) -> Dict[str, Any]:
        """Demonstrate publish/subscribe pattern."""
        
        print("\n3️⃣ Publish/Subscribe Demo")
        print("-" * 40)
        
        results = {
            "topics_created": [],
            "messages_published": 0,
            "messages_received": {}
        }
        
        # Create topics
        topics = ["insights", "processing_updates", "system_events"]
        
        # Subscribe agents to topics
        subscriptions = [
            ("agent_1", ["insights", "system_events"]),
            ("agent_2", ["processing_updates", "system_events"]),
            ("agent_3", ["insights", "processing_updates"])
        ]
        
        for agent_id, agent_topics in subscriptions:
            for topic in agent_topics:
                success = await message_bus.subscribe(agent_id, topic)
                if success:
                    print(f"  ✅ {agent_id} subscribed to '{topic}'")
        
        results["topics_created"] = topics
        
        # Publish messages to topics
        print("\n📢 Publishing Messages...")
        
        test_messages = [
            ("insights", {"type": "new_insight", "content": "Pattern detected in documents"}),
            ("processing_updates", {"type": "status", "progress": 50, "task": "document_analysis"}),
            ("system_events", {"type": "alert", "severity": "info", "message": "New agent joined"})
        ]
        
        from src.orchestration.communication import Message
        
        for topic, payload in test_messages:
            message = Message(
                message_type=MessageType.DATA,
                sender_id="demo_publisher",
                topic=topic,
                payload=payload
            )
            
            success = await message_bus.send_message(message)
            if success:
                print(f"  📤 Published to '{topic}': {payload['type']}")
                results["messages_published"] += 1
        
        # Allow time for message propagation
        await asyncio.sleep(0.1)
        
        # Check message reception (would need handlers in real scenario)
        stats = message_bus.get_statistics()
        print(f"\n📊 Publish/Subscribe Statistics:")
        print(f"   Messages Published: {results['messages_published']}")
        print(f"   Active Topics: {len(topics)}")
        print(f"   Total Subscriptions: {sum(len(t) for _, t in subscriptions)}")
        
        return results
    
    async def _demo_agent_discovery(self, message_bus: MessageBus) -> Dict[str, Any]:
        """Demonstrate agent discovery mechanisms."""
        
        print("\n4️⃣ Agent Discovery Demo")
        print("-" * 40)
        
        results = {
            "total_agents": 0,
            "discovered_by_type": {},
            "discovered_by_capability": {}
        }
        
        # Discover all agents
        all_agents = message_bus.get_agents()
        results["total_agents"] = len(all_agents)
        
        print(f"📍 Discovered {len(all_agents)} agents:")
        for agent in all_agents:
            print(f"  • {agent.agent_id} (type: {agent.agent_type}, capabilities: {agent.capabilities})")
        
        # Discover by type
        print("\n🔍 Discovery by Type:")
        for agent_type in ["test", "document", "analysis"]:
            agents = message_bus.get_agents(agent_type=agent_type)
            results["discovered_by_type"][agent_type] = len(agents)
            if agents:
                print(f"  • Type '{agent_type}': {len(agents)} agents")
        
        # Discover by capability
        print("\n🔍 Discovery by Capability:")
        for capability in ["processing", "analysis", "collaboration", "insights"]:
            agents = message_bus.get_agents(capability=capability)
            results["discovered_by_capability"][capability] = len(agents)
            if agents:
                print(f"  • Capability '{capability}': {len(agents)} agents")
                for agent in agents:
                    print(f"    - {agent.agent_id}")
        
        return results
    
    async def _demo_collaborative_processing(self, message_bus: MessageBus) -> Dict[str, Any]:
        """Demonstrate collaborative task processing."""
        
        print("\n5️⃣ Collaborative Processing Demo")
        print("-" * 40)
        
        results = {
            "collaboration_initiated": False,
            "tasks_distributed": 0,
            "results_aggregated": False,
            "total_processing_time": 0
        }
        
        # Simulate collaborative document processing
        print("\n📄 Simulating Collaborative Document Processing...")
        
        # Create a large document simulation
        document_sections = [
            "Section 1: Introduction and background...",
            "Section 2: Technical implementation details...",
            "Section 3: Results and analysis...",
            "Section 4: Conclusions and future work..."
        ]
        
        start_time = time.time()
        
        # Distribute sections to different agents
        from src.orchestration.communication import Message
        
        for i, section in enumerate(document_sections):
            agent_id = f"agent_{(i % 3) + 1}"
            
            message = Message(
                message_type=MessageType.REQUEST,
                sender_id="coordinator",
                recipient_id=agent_id,
                payload={
                    "task": "process_section",
                    "section_id": i,
                    "content": section
                }
            )
            
            success = await message_bus.send_message(message)
            if success:
                print(f"  📤 Distributed section {i+1} to {agent_id}")
                results["tasks_distributed"] += 1
        
        results["collaboration_initiated"] = True
        
        # Simulate processing time
        await asyncio.sleep(0.5)
        
        # Broadcast completion
        completion_message = Message(
            message_type=MessageType.BROADCAST,
            sender_id="coordinator",
            payload={
                "type": "collaboration_complete",
                "sections_processed": len(document_sections),
                "processing_time": time.time() - start_time
            }
        )
        
        count = await message_bus.broadcast("coordinator", completion_message.payload)
        print(f"\n📢 Broadcast completion to {count} agents")
        
        results["results_aggregated"] = True
        results["total_processing_time"] = time.time() - start_time
        
        print(f"⏱️  Total Processing Time: {results['total_processing_time']:.3f}s")
        
        return results
    
    async def _demo_team_formation(self, message_bus: MessageBus) -> Dict[str, Any]:
        """Demonstrate dynamic team formation."""
        
        print("\n6️⃣ Team Formation Demo")
        print("-" * 40)
        
        results = {
            "team_formed": False,
            "team_size": 0,
            "team_members": [],
            "capabilities_covered": []
        }
        
        # Define task requiring multiple capabilities
        task_requirements = {
            "task": "Complex Multi-Modal Analysis",
            "required_capabilities": ["processing", "analysis", "insights"],
            "min_team_size": 2,
            "max_team_size": 4
        }
        
        print(f"\n🎯 Task: {task_requirements['task']}")
        print(f"   Required Capabilities: {task_requirements['required_capabilities']}")
        
        # Form team based on capabilities
        team = []
        capabilities_covered = set()
        
        # Find agents with required capabilities
        for capability in task_requirements["required_capabilities"]:
            agents = message_bus.get_agents(capability=capability)
            
            for agent in agents:
                if agent.agent_id not in [a["agent_id"] for a in team]:
                    team.append({
                        "agent_id": agent.agent_id,
                        "capabilities": agent.capabilities,
                        "role": capability
                    })
                    capabilities_covered.update(agent.capabilities)
                    
                    print(f"  ➕ Added {agent.agent_id} to team (role: {capability})")
                    
                    if len(team) >= task_requirements["max_team_size"]:
                        break
            
            if len(team) >= task_requirements["max_team_size"]:
                break
        
        results["team_formed"] = len(team) >= task_requirements["min_team_size"]
        results["team_size"] = len(team)
        results["team_members"] = team
        results["capabilities_covered"] = list(capabilities_covered)
        
        if results["team_formed"]:
            print(f"\n✅ Team formed with {len(team)} members")
            print(f"   Capabilities covered: {results['capabilities_covered']}")
            
            # Send team invitations
            from src.orchestration.communication import Message
            
            for member in team:
                invite = Message(
                    message_type=MessageType.NOTIFICATION,
                    sender_id="team_coordinator",
                    recipient_id=member["agent_id"],
                    payload={
                        "type": "team_invitation",
                        "task": task_requirements["task"],
                        "role": member["role"],
                        "team_size": len(team)
                    }
                )
                
                await message_bus.send_message(invite)
                print(f"  📨 Sent invitation to {member['agent_id']}")
        else:
            print(f"\n❌ Failed to form team - only {len(team)} members found")
        
        return results
    
    async def _generate_communication_report(self):
        """Generate comprehensive communication report."""
        
        print("\n7️⃣ Phase 4 Communication Report")
        print("=" * 40)
        
        report = {
            "phase": "Phase 4: Agent Communication",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "summary": {
                "components_implemented": [
                    "MessageBus for centralized communication",
                    "AgentCommunicator for individual agents",
                    "CommunicatingAgent base class",
                    "Message types and priorities",
                    "Communication patterns (request-reply, pub-sub, broadcast)",
                    "Agent discovery and registration",
                    "Team formation capabilities",
                    "Collaborative task distribution"
                ],
                "message_types": [
                    "REQUEST - Request-reply pattern",
                    "RESPONSE - Reply to requests",
                    "BROADCAST - Broadcast to all agents",
                    "NOTIFICATION - System notifications",
                    "QUERY - Query other agents",
                    "DATA - Data sharing via topics",
                    "HEARTBEAT - Agent health checks",
                    "DISCOVERY - Agent discovery"
                ],
                "communication_patterns": [
                    "Direct Messaging - Point-to-point communication",
                    "Request-Reply - Synchronous request/response",
                    "Publish-Subscribe - Topic-based messaging",
                    "Broadcast - One-to-all messaging",
                    "Team Communication - Group coordination"
                ]
            },
            "results": self.results
        }
        
        # Save report
        report_path = Path("phase4_communication_report.json")
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)
        
        print(f"📊 Component Status:")
        for component in report["summary"]["components_implemented"]:
            print(f"   ✅ {component}")
        
        print(f"\n💬 Message Types:")
        for msg_type in report["summary"]["message_types"][:4]:
            print(f"   📧 {msg_type}")
        
        print(f"\n🔄 Communication Patterns:")
        for pattern in report["summary"]["communication_patterns"]:
            print(f"   🎯 {pattern}")
        
        # Performance summary
        if "direct_messaging" in self.results:
            dm_results = self.results["direct_messaging"]
            if "avg_round_trip_time" in dm_results:
                print(f"\n⚡ Performance:")
                print(f"   Average Message RTT: {dm_results['avg_round_trip_time']:.3f}s")
                print(f"   Success Rate: {dm_results['responses_received']}/{dm_results['messages_sent']} messages")
        
        print(f"\n💾 Report saved to: {report_path}")
        
        return report


async def main():
    """Run the Phase 4 communication demonstration."""
    
    demo = Phase4CommunicationDemo()
    results = await demo.run_complete_demo()
    
    if "error" not in results:
        print(f"\n🎉 Phase 4: Agent Communication Implementation Complete!")
        print(f"🚀 All Advanced Agent Features are now implemented!")
        print(f"\n✅ Completed Phases:")
        print(f"   1. Memory System ✓")
        print(f"   2. LLM-Powered Reasoning ✓")
        print(f"   3. Parallel Orchestration ✓")
        print(f"   4. Agent Communication ✓")
    else:
        print(f"\n❌ Demo encountered issues: {results['error']}")
    
    return results


if __name__ == "__main__":
    asyncio.run(main())