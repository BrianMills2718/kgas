#!/usr/bin/env python3
"""
Phase A Demo: Natural Language Interface
Demonstrates the working natural language Q&A system
"""
import asyncio
import sys
import os
from pathlib import Path
import time

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.interface.nl_interface import NaturalLanguageInterface

class PhaseADemo:
    """Demo for Phase A Natural Language Interface"""
    
    def __init__(self):
        self.interface = None
        self.demo_documents = []
        
    async def run_demo(self):
        """Run the complete Phase A demo"""
        print("🤖 PHASE A DEMO: Natural Language Interface")
        print("=" * 60)
        print("Demonstrating: Question → MCP Tool Execution → Natural Language Answer")
        print()
        
        # Initialize interface
        print("🔧 Initializing Natural Language Interface...")
        try:
            self.interface = NaturalLanguageInterface()
            await self.interface.initialize()
            print("✅ Interface initialized successfully")
        except Exception as e:
            print(f"❌ Initialization failed: {e}")
            return False
        
        # Show capabilities
        await self._show_capabilities()
        
        # Create demo documents
        await self._create_demo_documents()
        
        # Run demo scenarios
        scenarios = [
            ("Business Document Analysis", self._demo_business_document),
            ("Academic Paper Analysis", self._demo_academic_document),
            ("Session Context Demo", self._demo_session_context),
            ("Different Question Types", self._demo_question_types),
            ("Error Handling Demo", self._demo_error_handling)
        ]
        
        for scenario_name, scenario_func in scenarios:
            print(f"\n" + "="*60)
            print(f"📋 SCENARIO: {scenario_name}")
            print("="*60)
            
            try:
                await scenario_func()
                print(f"✅ {scenario_name} completed successfully")
            except Exception as e:
                print(f"❌ {scenario_name} failed: {e}")
                import traceback
                traceback.print_exc()
        
        # Cleanup
        await self._cleanup_demo_documents()
        
        print(f"\n" + "="*60)
        print(f"🎉 PHASE A DEMO COMPLETED!")
        print(f"   Natural Language Interface is fully operational")
        print(f"   Ready for Phase B: Dynamic Execution & Intelligent Orchestration")
        print("="*60)
        
        return True
    
    async def _show_capabilities(self):
        """Show interface capabilities"""
        print(f"\n📋 Interface Capabilities:")
        capabilities = self.interface.list_capabilities()
        
        print(f"   • Initialization: {'✅' if capabilities['initialization_complete'] else '❌'}")
        print(f"   • MCP Client: {'✅' if capabilities['mcp_status']['mcp_client_available'] else '❌'}")
        print(f"   • Question Types: {len(capabilities['supported_question_types'])}")
        print(f"   • Document Types: {', '.join(capabilities['supported_document_types'])}")
        
        print(f"\n💬 Supported Question Types:")
        for i, question_type in enumerate(capabilities['supported_question_types'], 1):
            print(f"   {i}. {question_type}")
    
    async def _create_demo_documents(self):
        """Create demo documents for testing"""
        print(f"\n📄 Creating demo documents...")
        
        # Business document
        business_doc = Path("demo_business.txt")
        business_content = """
        Microsoft Corporation Strategic Analysis Report
        
        Microsoft is a leading technology company founded by Bill Gates and Paul Allen in 1975.
        The company is headquartered in Redmond, Washington, and is led by CEO Satya Nadella.
        
        Key Business Areas:
        - Cloud Computing: Azure platform competes with Amazon Web Services
        - Productivity Software: Office 365 serves millions of enterprise customers
        - Gaming: Xbox division generates significant revenue from console sales
        - LinkedIn: Professional networking platform acquired in 2016
        
        Strategic Partnerships:
        Microsoft works closely with Intel for hardware optimization.
        The company has partnerships with Samsung for mobile device integration.
        OpenAI collaboration has strengthened Microsoft's AI capabilities.
        
        Financial Performance:
        Revenue has grown consistently, reaching $200+ billion annually.
        Cloud services represent the fastest-growing segment.
        The company maintains strong profit margins across all divisions.
        """
        business_doc.write_text(business_content)
        self.demo_documents.append(business_doc)
        
        # Academic document
        academic_doc = Path("demo_academic.txt")
        academic_content = """
        Artificial Intelligence in Healthcare: A Systematic Review
        
        Abstract:
        This paper examines the application of artificial intelligence technologies 
        in healthcare settings, focusing on machine learning applications in 
        diagnostic imaging and patient care optimization.
        
        Authors: Dr. Sarah Johnson (Stanford University), Dr. Michael Chen (MIT), 
        Dr. Lisa Rodriguez (Johns Hopkins)
        
        Key Findings:
        1. Machine learning algorithms demonstrate 95% accuracy in medical imaging
        2. Natural language processing improves electronic health record efficiency
        3. Predictive analytics reduces patient readmission rates by 30%
        
        Methodology:
        The research team analyzed 500 clinical studies published between 2020-2023.
        Data was collected from hospitals in California, Massachusetts, and Maryland.
        Statistical analysis was performed using Python and R programming languages.
        
        Conclusions:
        AI technologies show significant promise for healthcare improvement.
        Implementation challenges include data privacy and clinician training.
        Future research should focus on bias reduction and ethical considerations.
        """
        academic_doc.write_text(academic_content)
        self.demo_documents.append(academic_doc)
        
        # Technical document
        tech_doc = Path("demo_technical.txt")
        tech_content = """
        Blockchain Technology Implementation Guide
        
        Overview:
        Blockchain represents a distributed ledger technology that enables secure,
        transparent, and immutable record-keeping without central authority.
        
        Key Components:
        - Cryptographic Hashing: SHA-256 ensures data integrity
        - Consensus Mechanisms: Proof of Work and Proof of Stake validation
        - Smart Contracts: Automated execution of predefined conditions
        - Peer-to-Peer Network: Decentralized node communication
        
        Implementation Steps:
        1. Network Architecture Design: Configure node topology
        2. Consensus Protocol Selection: Choose appropriate validation method
        3. Smart Contract Development: Write and test automated contracts
        4. Security Audit: Verify cryptographic implementations
        5. Performance Testing: Measure transaction throughput
        
        Use Cases:
        - Supply Chain Management: Track products from origin to consumer
        - Digital Identity: Secure credential verification systems  
        - Financial Services: Cryptocurrency and payment processing
        - Healthcare Records: Patient data integrity and access control
        
        Technical Requirements:
        - Programming Languages: Solidity, Go, Rust, Python
        - Development Frameworks: Truffle, Hardhat, Web3.js
        - Infrastructure: AWS, Azure, Google Cloud Platform
        """
        tech_doc.write_text(tech_content)
        self.demo_documents.append(tech_doc)
        
        print(f"   ✅ Created {len(self.demo_documents)} demo documents")
    
    async def _demo_business_document(self):
        """Demo with business document"""
        doc_path = "demo_business.txt"
        print(f"📄 Loading business document: {doc_path}")
        
        success = await self.interface.load_document(doc_path)
        if not success:
            print(f"❌ Failed to load document")
            return
        
        print(f"✅ Document loaded successfully")
        
        # Ask different types of questions
        questions = [
            "What is this document about?",
            "Who are the key people mentioned?", 
            "What companies does Microsoft work with?",
            "What are Microsoft's main business areas?"
        ]
        
        session_id = "business_demo"
        
        for i, question in enumerate(questions, 1):
            print(f"\n🤔 Question {i}: {question}")
            print("-" * 50)
            
            start_time = time.time()
            response = await self.interface.ask_question(question, session_id)
            execution_time = time.time() - start_time
            
            # Show abbreviated response
            if len(response) > 300:
                displayed_response = response[:300] + "..."
            else:
                displayed_response = response
            
            print(f"🤖 Response ({execution_time:.2f}s):")
            print(displayed_response)
    
    async def _demo_academic_document(self):
        """Demo with academic document"""
        doc_path = "demo_academic.txt"
        print(f"📄 Loading academic document: {doc_path}")
        
        success = await self.interface.load_document(doc_path)
        if not success:
            print(f"❌ Failed to load document")
            return
        
        # Academic-focused questions
        questions = [
            "What are the key findings of this research?",
            "Who are the authors and their affiliations?",
            "What methodology was used in this study?",
            "What are the main conclusions?"
        ]
        
        session_id = "academic_demo"
        
        for i, question in enumerate(questions, 1):
            print(f"\n🤔 Academic Question {i}: {question}")
            print("-" * 50)
            
            start_time = time.time()
            response = await self.interface.ask_question(question, session_id)
            execution_time = time.time() - start_time
            
            # Show abbreviated response
            displayed_response = response[:250] + "..." if len(response) > 250 else response
            
            print(f"🤖 Response ({execution_time:.2f}s):")
            print(displayed_response)
    
    async def _demo_session_context(self):
        """Demo session context and follow-up questions"""
        doc_path = "demo_technical.txt"
        print(f"📄 Loading technical document for context demo: {doc_path}")
        
        success = await self.interface.load_document(doc_path)
        if not success:
            print(f"❌ Failed to load document")
            return
        
        session_id = "context_demo"
        
        # Sequence of related questions
        conversation = [
            "What is blockchain technology?",
            "What are the key components mentioned?",
            "How do smart contracts work?",
            "What programming languages are needed?"
        ]
        
        for i, question in enumerate(conversation, 1):
            print(f"\n💬 Context Question {i}: {question}")
            print("-" * 50)
            
            response = await self.interface.ask_question(question, session_id)
            displayed_response = response[:200] + "..." if len(response) > 200 else response
            
            print(f"🤖 Response:")
            print(displayed_response)
        
        # Show session context
        print(f"\n📊 Session Context Summary:")
        context = self.interface.get_session_context(session_id)
        print(f"   • Session ID: {context['session_id']}")
        print(f"   • Interactions: {context['interaction_count']}")
        print(f"   • Duration: {context['duration']:.1f} seconds")
        print(f"   • Active: {context['active']}")
    
    async def _demo_question_types(self):
        """Demo different question types with same document"""
        doc_path = "demo_business.txt"
        await self.interface.load_document(doc_path)
        
        print(f"📄 Testing different question types on business document:")
        
        question_type_demos = [
            ("Document Summary", "Summarize the main points of this document"),
            ("Entity Analysis", "What organizations are mentioned in this document?"),
            ("Relationship Analysis", "How do Microsoft and its partners relate?"),
            ("Theme Analysis", "What are the main themes discussed?"),
            ("Specific Search", "Find information about Azure cloud platform"),
            ("Graph Analysis", "Show me the network of business relationships"),
            ("PageRank Analysis", "Which entities are most important in this document?")
        ]
        
        session_id = "question_types_demo"
        
        for question_type, question in question_type_demos:
            print(f"\n🎯 {question_type}:")
            print(f"   Question: {question}")
            
            start_time = time.time()
            response = await self.interface.ask_question(question, session_id)
            execution_time = time.time() - start_time
            
            # Show first 150 characters
            preview = response[:150] + "..." if len(response) > 150 else response
            print(f"   Response ({execution_time:.2f}s): {preview}")
    
    async def _demo_error_handling(self):
        """Demo error handling capabilities"""
        print(f"🛡️  Testing error handling capabilities:")
        
        # Test 1: No document loaded
        self.interface.current_document = None
        print(f"\n   Test 1: Question without loaded document")
        response1 = await self.interface.ask_question("What is this about?")
        print(f"   Result: {'✅' if 'load a document' in response1.lower() else '❌'}")
        
        # Test 2: Empty question
        await self.interface.load_document("demo_business.txt")
        print(f"\n   Test 2: Empty question")
        response2 = await self.interface.ask_question("")
        print(f"   Result: {'✅' if isinstance(response2, str) and len(response2) > 0 else '❌'}")
        
        # Test 3: Very long question
        print(f"\n   Test 3: Very long question")
        long_question = "What about " + "technology and business " * 50 + "?"
        response3 = await self.interface.ask_question(long_question)
        print(f"   Result: {'✅' if isinstance(response3, str) and 'error' not in response3.lower() else '❌'}")
        
        # Test 4: Non-existent file
        print(f"\n   Test 4: Loading non-existent file")
        load_result = await self.interface.load_document("nonexistent_file.pdf")
        print(f"   Result: {'✅' if load_result == False else '❌'}")
    
    async def _cleanup_demo_documents(self):
        """Clean up demo documents"""
        print(f"\n🧹 Cleaning up demo documents...")
        
        for doc in self.demo_documents:
            if doc.exists():
                doc.unlink()
        
        print(f"   ✅ Cleaned up {len(self.demo_documents)} demo documents")

async def main():
    """Main demo function"""
    demo = PhaseADemo()
    success = await demo.run_demo()
    
    if success:
        print(f"\n🎉 SUCCESS: Phase A Demo completed successfully!")
        print(f"   The Natural Language Interface is fully operational")
        return 0
    else:
        print(f"\n❌ FAILURE: Phase A Demo encountered issues")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())