#!/usr/bin/env python3
"""
MCP-BASED MULTI-DOCUMENT OVERLOAD STRESS TEST

Converts the multi-document stress test to use MCP tool calls instead of Python imports.
This addresses the relationship extraction pipeline failure we fixed by using MCP protocol.

Original Issues Fixed:
1. ToolRequest import scoping issues
2. Entity format mismatch between T23A and T27
3. chunk_ref association problems
4. Python dependency coupling

Tests MCP-based processing of 50+ academic papers simultaneously to find:
1. MCP communication scalability limits
2. Process isolation benefits/overhead
3. Error propagation through MCP chains
4. Resource management via MCP protocol
5. Relationship extraction via pure MCP

This validates the relationship extraction fixes work correctly via MCP.
"""

import asyncio
import json
import time
import uuid
import random
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging
import subprocess
import os
from pathlib import Path

class MCPClientWrapper:
    """Reusable MCP client wrapper for tool communication"""
    
    def __init__(self, server_command: List[str], server_name: str):
        self.server_command = server_command
        self.server_name = server_name
        self.process = None
        self.logger = logging.getLogger(f"mcp_client_{server_name}")
        self.call_count = 0
    
    async def __aenter__(self):
        """Start MCP server process"""
        try:
            self.process = await asyncio.create_subprocess_exec(
                *self.server_command,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd="/home/brian/projects/Digimons"
            )
            
            # Give server time to start
            await asyncio.sleep(3)
            
            if self.process.returncode is not None:
                stderr = await self.process.stderr.read()
                raise Exception(f"MCP server {self.server_name} failed to start: {stderr.decode()}")
            
            self.logger.info(f"MCP server {self.server_name} started successfully")
            return self
            
        except Exception as e:
            self.logger.error(f"Failed to start MCP server {self.server_name}: {e}")
            raise
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Stop MCP server process"""
        if self.process and self.process.returncode is None:
            try:
                self.process.terminate()
                await asyncio.wait_for(self.process.wait(), timeout=5.0)
            except asyncio.TimeoutError:
                self.process.kill()
                await self.process.wait()
            
            self.logger.info(f"MCP server {self.server_name} stopped ({self.call_count} total calls)")
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call MCP tool with arguments and track call count"""
        try:
            self.call_count += 1
            
            # Prepare MCP request
            request = {
                "jsonrpc": "2.0",
                "id": str(uuid.uuid4()),
                "method": "tools/call",
                "params": {
                    "name": tool_name,
                    "arguments": arguments
                }
            }
            
            # Send request
            request_json = json.dumps(request) + "\n"
            self.process.stdin.write(request_json.encode())
            await self.process.stdin.drain()
            
            # Read response with timeout
            response_line = await asyncio.wait_for(
                self.process.stdout.readline(), 
                timeout=30.0  # 30 second timeout per tool call
            )
            
            if not response_line:
                raise Exception("No response from MCP server")
            
            response = json.loads(response_line.decode().strip())
            
            if "error" in response:
                raise Exception(f"MCP tool error: {response['error']}")
            
            return response.get("result", {})
            
        except asyncio.TimeoutError:
            raise Exception(f"MCP tool call timeout after 30 seconds")
        except Exception as e:
            self.logger.error(f"MCP tool call failed (call #{self.call_count}): {e}")
            raise

class MCPMultiDocumentStressTest:
    """Test MCP-based multi-document processing to validate relationship extraction fixes"""
    
    def __init__(self):
        self.test_id = f"mcp_multidoc_{uuid.uuid4().hex[:8]}"
        self.logger = logging.getLogger(f"mcp_multidoc_{self.test_id}")
        self.logger.setLevel(logging.DEBUG)
        
        print(f"📚 MCP-BASED MULTI-DOCUMENT STRESS TEST INITIALIZED")
        print(f"   Target: Process 25 academic papers via MCP protocol")
        print(f"   Focus: Validate relationship extraction fixes work via MCP")
        print(f"   Architecture: Pure MCP communication (no Python imports)")
    
    async def execute_academic_paper_overload(self, num_documents: int = 25) -> Dict[str, Any]:
        """Process multiple academic papers via MCP to validate relationship extraction"""
        
        print(f"\n🚨 MCP ACADEMIC PAPER OVERLOAD TEST")
        print(f"   Documents: {num_documents}")
        print(f"   Architecture: Pure MCP tool calls")
        print(f"   Goal: Validate relationship extraction fixes via MCP")
        print(f"   Expected: Successful entity extraction AND relationship extraction")
        
        test_results = {
            "test_id": self.test_id,
            "start_time": datetime.now().isoformat(),
            "num_documents": num_documents,
            "architecture": "pure_mcp",
            "documents_processed": 0,
            "total_chunks": 0,
            "total_entities": 0,
            "total_relationships": 0,
            "successful_operations": 0,
            "failed_operations": 0,
            "mcp_call_count": 0,
            "performance_timeline": [],
            "validation_results": {}
        }
        
        try:
            # Generate test papers
            test_papers = self._generate_relationship_rich_papers(num_documents)
            print(f"✅ Generated {len(test_papers)} relationship-rich test papers")
            
            # Start KGAS MCP server
            server_command = ["python", "kgas_mcp_server.py"]
            
            async with MCPClientWrapper(server_command, "kgas_tools") as mcp_client:
                print(f"✅ KGAS MCP server started successfully")
                
                start_time = time.time()
                
                # Process all papers via MCP
                paper_results = []
                for i, paper in enumerate(test_papers):
                    print(f"\n📄 Processing paper {i+1}/{len(test_papers)}: '{paper['title'][:50]}...'")
                    
                    try:
                        paper_result = await self._process_paper_via_mcp(
                            mcp_client, paper, i, test_results
                        )
                        paper_results.append(paper_result)
                        test_results["successful_operations"] += 1
                        
                        # Update totals
                        test_results["total_chunks"] += paper_result.get("chunks", 0)
                        test_results["total_entities"] += paper_result.get("entities", 0)
                        test_results["total_relationships"] += paper_result.get("relationships", 0)
                        
                        print(f"   ✅ Paper {i+1}: {paper_result.get('entities', 0)} entities, {paper_result.get('relationships', 0)} relationships")
                        
                    except Exception as e:
                        self.logger.error(f"Paper {i+1} processing failed: {e}")
                        test_results["failed_operations"] += 1
                        paper_results.append({
                            "paper_id": paper["id"],
                            "status": "failed",
                            "error": str(e)
                        })
                        print(f"   ❌ Paper {i+1}: Processing failed - {e}")
                
                test_results["documents_processed"] = len([r for r in paper_results if r.get("status") == "success"])
                test_results["mcp_call_count"] = mcp_client.call_count
                test_results["total_execution_time"] = time.time() - start_time
                
                # Validate the relationship extraction fix
                validation_result = self._validate_relationship_extraction_fix(paper_results)
                test_results["validation_results"] = validation_result
                
                print(f"\n📊 MCP MULTI-DOCUMENT TEST RESULTS:")
                print(f"   Documents Processed: {test_results['documents_processed']}/{num_documents}")
                print(f"   Success Rate: {test_results['successful_operations']/num_documents*100:.1f}%")
                print(f"   Total MCP Calls: {test_results['mcp_call_count']}")
                print(f"   Execution Time: {test_results['total_execution_time']:.2f}s")
                print(f"   Total Entities Extracted: {test_results['total_entities']}")
                print(f"   Total Relationships Found: {test_results['total_relationships']}")
                
                # Key validation: Did we extract relationships?
                if test_results["total_relationships"] > 0:
                    print(f"   🎉 RELATIONSHIP EXTRACTION SUCCESS: {test_results['total_relationships']} relationships found!")
                    print(f"   ✅ Format conversion fix working via MCP")
                    print(f"   ✅ chunk_ref association fix working via MCP")
                else:
                    print(f"   🚨 RELATIONSHIP EXTRACTION FAILURE: 0 relationships found")
                    print(f"   ❌ MCP communication may have issues")
                
                # Performance validation
                if test_results["total_execution_time"] < num_documents * 2:  # Less than 2s per document
                    print(f"   ✅ Performance: MCP overhead acceptable")
                else:
                    print(f"   ⚠️ Performance: MCP overhead may be high")
                
                return test_results
                
        except Exception as e:
            test_results["status"] = "catastrophic_failure"
            test_results["error"] = str(e)
            self.logger.error(f"MCP multi-document test catastrophic failure: {e}")
            print(f"💥 MCP MULTI-DOCUMENT TEST CATASTROPHIC FAILURE: {e}")
            return test_results
    
    async def _process_paper_via_mcp(self, mcp_client: MCPClientWrapper, 
                                    paper: Dict[str, Any], paper_index: int,
                                    test_results: Dict[str, Any]) -> Dict[str, Any]:
        """Process single paper via MCP calls to validate relationship extraction"""
        
        paper_start = time.time()
        
        try:
            # Step 1: Text chunking via MCP
            chunk_result = await mcp_client.call_tool("chunk_text", {
                "document_ref": f"storage://mcp_stress/{paper['id']}.txt",
                "text": paper["content"],
                "document_confidence": 0.9,
                "chunk_size": 500,
                "overlap": 50
            })
            
            chunks = chunk_result.get("chunks", [])
            if not chunks:
                raise Exception("No chunks returned from MCP chunking")
            
            # Step 2: Entity extraction via MCP for each chunk
            all_entities = []
            for chunk in chunks:
                entity_result = await mcp_client.call_tool("extract_entities", {
                    "chunk_ref": chunk["chunk_ref"],
                    "text": chunk["text"],
                    "chunk_confidence": chunk.get("confidence", 0.8),
                    "confidence_threshold": 0.5
                })
                
                entities = entity_result.get("entities", [])
                all_entities.extend(entities)
            
            # Step 3: Relationship extraction via MCP (this is where the fix is tested)
            all_relationships = []
            for chunk in chunks:
                # Get entities for this chunk
                chunk_entities = [e for e in all_entities if e.get("chunk_ref") == chunk["chunk_ref"]]
                
                if len(chunk_entities) >= 2:  # Need at least 2 entities for relationships
                    # Apply the format conversion fix we implemented
                    t27_entities = []
                    for entity in chunk_entities:
                        # This is the critical fix: T23A → T27 format conversion
                        t27_entity = {
                            'text': entity.get('surface_form', ''),     # T23A field → T27 field
                            'label': entity.get('entity_type', ''),    # T23A field → T27 field  
                            'start': entity.get('start_pos', 0),       # T23A field → T27 field
                            'end': entity.get('end_pos', 0),           # T23A field → T27 field
                            # Preserve debug info
                            '_chunk_ref': entity.get('chunk_ref', ''),
                            '_confidence': entity.get('confidence', 0.0)
                        }
                        t27_entities.append(t27_entity)
                    
                    # Call relationship extraction with converted format
                    rel_result = await mcp_client.call_tool("extract_relationships", {
                        "chunk_ref": chunk["chunk_ref"],
                        "text": chunk["text"],
                        "entities": t27_entities,  # Using converted format!
                        "confidence": 0.3  # Lower threshold for stress test
                    })
                    
                    relationships = rel_result.get("relationships", [])
                    all_relationships.extend(relationships)
            
            processing_time = time.time() - paper_start
            
            # Track performance
            test_results["performance_timeline"].append({
                "paper_index": paper_index,
                "processing_time": processing_time,
                "chunks": len(chunks),
                "entities": len(all_entities),
                "relationships": len(all_relationships),
                "entities_per_second": len(all_entities) / max(0.1, processing_time),
                "relationships_per_second": len(all_relationships) / max(0.1, processing_time)
            })
            
            return {
                "paper_id": paper["id"],
                "status": "success",
                "processing_time": processing_time,
                "chunks": len(chunks),
                "entities": len(all_entities),
                "relationships": len(all_relationships),
                "expected_entities": paper.get("expected_entities", 0),
                "expected_relationships": paper.get("expected_relationships", 0),
                "extraction_effectiveness": {
                    "entity_extraction_rate": len(all_entities) / max(1, paper.get("expected_entities", 1)),
                    "relationship_extraction_rate": len(all_relationships) / max(1, paper.get("expected_relationships", 1))
                }
            }
            
        except Exception as e:
            return {
                "paper_id": paper["id"],
                "status": "failed",
                "error": str(e),
                "processing_time": time.time() - paper_start
            }
    
    def _validate_relationship_extraction_fix(self, paper_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate that the relationship extraction fixes work correctly via MCP"""
        
        successful_papers = [r for r in paper_results if r.get("status") == "success"]
        
        if not successful_papers:
            return {
                "validation_status": "failed",
                "reason": "no_successful_papers",
                "details": "No papers processed successfully"
            }
        
        # Check if relationships were extracted
        papers_with_relationships = [r for r in successful_papers if r.get("relationships", 0) > 0]
        relationship_extraction_rate = len(papers_with_relationships) / len(successful_papers)
        
        # Calculate average extraction rates
        avg_entities = sum(r.get("entities", 0) for r in successful_papers) / len(successful_papers)
        avg_relationships = sum(r.get("relationships", 0) for r in successful_papers) / len(successful_papers)
        
        # Determine validation result
        if relationship_extraction_rate >= 0.7:  # 70% of papers should have relationships
            validation_status = "passed"
            reason = "relationship_extraction_successful"
        elif relationship_extraction_rate >= 0.3:  # 30% is partial success
            validation_status = "partial"
            reason = "some_relationship_extraction"
        else:
            validation_status = "failed"
            reason = "insufficient_relationship_extraction"
        
        return {
            "validation_status": validation_status,
            "reason": reason,
            "metrics": {
                "successful_papers": len(successful_papers),
                "papers_with_relationships": len(papers_with_relationships),
                "relationship_extraction_rate": relationship_extraction_rate,
                "avg_entities_per_paper": avg_entities,
                "avg_relationships_per_paper": avg_relationships,
                "entity_to_relationship_ratio": avg_relationships / max(1, avg_entities)
            },
            "comparison_to_original_issue": {
                "original_problem": "398 entities extracted, 0 relationships found",
                "mcp_result": f"{int(avg_entities)} avg entities, {int(avg_relationships)} avg relationships",
                "fix_effectiveness": "working" if avg_relationships > 0 else "still_broken"
            }
        }
    
    def _generate_relationship_rich_papers(self, count: int) -> List[Dict[str, Any]]:
        """Generate papers specifically designed to test relationship extraction"""
        
        # Authors with clear relationships
        authors_pool = [
            "Dr. Sarah Chen", "Prof. Michael Rodriguez", "Dr. Elena Kowalski",
            "Prof. James Thompson", "Dr. Aisha Patel", "Prof. David Kim"
        ]
        
        # Institutions with clear relationships
        institutions_pool = [
            "MIT Computer Science Department", "Stanford AI Lab", "Google DeepMind",
            "Carnegie Mellon University", "UC Berkeley EECS", "Harvard Medical School"
        ]
        
        # Companies with clear business relationships
        companies_pool = [
            "TechCorp Industries LLC", "Meta Platforms Inc.", "OpenAI Research",
            "Anthropic AI", "Microsoft Research", "NVIDIA Corporation"
        ]
        
        papers = []
        
        for i in range(count):
            # Select entities for this paper
            paper_authors = random.sample(authors_pool, random.randint(2, 4))
            paper_institutions = random.sample(institutions_pool, random.randint(1, 3))
            paper_companies = random.sample(companies_pool, random.randint(1, 2))
            
            # Create content with explicit relationships
            content = self._create_relationship_rich_content(
                paper_authors, paper_institutions, paper_companies, i
            )
            
            papers.append({
                "id": f"rel_test_paper_{i:03d}",
                "title": f"Collaborative Research on Advanced AI Methods (Paper {i+1})",
                "authors": paper_authors,
                "institutions": paper_institutions,
                "companies": paper_companies,
                "content": content,
                "expected_entities": len(paper_authors) + len(paper_institutions) + len(paper_companies) + 5,  # +5 for concepts
                "expected_relationships": len(paper_authors) * len(paper_institutions) + len(paper_companies) * 2  # Conservative estimate
            })
        
        return papers
    
    def _create_relationship_rich_content(self, authors: List[str], institutions: List[str], 
                                         companies: List[str], paper_id: int) -> str:
        """Create content with explicit, detectable relationships"""
        
        # Use very explicit relationship patterns
        content = f"""
        This research is conducted by {authors[0]} from {institutions[0]} in collaboration with {authors[1] if len(authors) > 1 else authors[0]}.
        
        {authors[0]} works at {institutions[0]} and partnered with {companies[0]} for this project.
        The collaboration between {institutions[0]} and {companies[0]} enabled comprehensive validation.
        
        Prof. {authors[1].split()[-1] if len(authors) > 1 else authors[0].split()[-1]} leads the research team at {institutions[0]}.
        {companies[0]} provided funding for this research conducted at {institutions[0]}.
        
        The methodology developed by {authors[0]} demonstrates applications of machine learning.
        {institutions[0]} researchers collaborated with {companies[0]} engineers to implement the solution.
        
        Results show {authors[0]} and {authors[1] if len(authors) > 1 else authors[0]} successfully created novel algorithms.
        The partnership between {institutions[0]} and {companies[0]} produced significant innovations.
        
        Future work will explore connections between the research at {institutions[0]} and applications at {companies[0]}.
        {authors[0]} plans to continue collaboration with {companies[0]} and expand work at {institutions[0]}.
        """
        
        return content.strip()

async def run_mcp_multi_document_stress_test():
    """Execute the MCP-based multi-document stress test"""
    
    test = MCPMultiDocumentStressTest()
    
    print(f"\\n🚨 MCP-BASED MULTI-DOCUMENT STRESS TEST")
    print(f"   Goal: Validate relationship extraction fixes via MCP")
    print(f"   Target: Process 25 documents with entity + relationship extraction")
    print(f"   Architecture: Pure MCP protocol (no Python imports)")
    print(f"=" * 80)
    
    try:
        # Execute MCP multi-document test
        results = await test.execute_academic_paper_overload(25)
        
        print(f"\\n📊 FINAL MCP MULTI-DOCUMENT STRESS TEST RESULTS:")
        print(f"   Status: {results.get('status', 'completed')}")
        print(f"   Documents Processed: {results.get('documents_processed', 0)}/{results.get('num_documents', 0)}")
        print(f"   Total Entities: {results.get('total_entities', 0)}")
        print(f"   Total Relationships: {results.get('total_relationships', 0)}")
        print(f"   Total MCP Calls: {results.get('mcp_call_count', 0)}")
        print(f"   Execution Time: {results.get('total_execution_time', 0):.2f}s")
        
        # Validation results
        validation = results.get("validation_results", {})
        if validation:
            print(f"\\n🧪 RELATIONSHIP EXTRACTION VALIDATION:")
            print(f"   Validation Status: {validation.get('validation_status', 'unknown')}")
            print(f"   Reason: {validation.get('reason', 'unknown')}")
            
            metrics = validation.get("metrics", {})
            if metrics:
                print(f"   Papers with Relationships: {metrics.get('papers_with_relationships', 0)}")
                print(f"   Relationship Extraction Rate: {metrics.get('relationship_extraction_rate', 0):.1%}")
                print(f"   Avg Entities per Paper: {metrics.get('avg_entities_per_paper', 0):.1f}")
                print(f"   Avg Relationships per Paper: {metrics.get('avg_relationships_per_paper', 0):.1f}")
            
            comparison = validation.get("comparison_to_original_issue", {})
            if comparison:
                print(f"\\n🔄 COMPARISON TO ORIGINAL ISSUE:")
                print(f"   Original Problem: {comparison.get('original_problem', 'unknown')}")
                print(f"   MCP Result: {comparison.get('mcp_result', 'unknown')}")
                print(f"   Fix Effectiveness: {comparison.get('fix_effectiveness', 'unknown')}")
        
        # Architecture assessment
        success_rate = results.get('successful_operations', 0) / results.get('num_documents', 1)
        if success_rate >= 0.8 and results.get('total_relationships', 0) > 0:
            print(f"\\n🎉 MCP ARCHITECTURE VALIDATION SUCCESS:")
            print(f"   ✅ MCP communication: Working reliably")
            print(f"   ✅ Relationship extraction: Fixed via MCP")
            print(f"   ✅ Format conversion: Working in MCP calls")
            print(f"   ✅ Tool chain execution: Stable via MCP protocol")
            print(f"   🚀 Recommendation: Continue MCP migration")
        else:
            print(f"\\n⚠️ MCP ARCHITECTURE NEEDS IMPROVEMENT:")
            print(f"   Success rate: {success_rate:.1%}")
            print(f"   Relationships found: {results.get('total_relationships', 0)}")
            print(f"   🔧 Recommendation: Debug MCP communication issues")
        
        return results
        
    except Exception as e:
        print(f"💥 MCP MULTI-DOCUMENT STRESS TEST CATASTROPHIC FAILURE: {e}")
        return {
            "status": "catastrophic_failure",
            "error": str(e),
            "architecture": "mcp_communication_failed"
        }

if __name__ == "__main__":
    asyncio.run(run_mcp_multi_document_stress_test())