#!/usr/bin/env python3
"""
Thesis Evidence Collector
Runs the KGAS pipeline on ground truth documents and collects metrics
"""

import os
import sys
import json
import time
import sqlite3
from typing import Dict, List, Any, Tuple
from datetime import datetime
from dataclasses import dataclass, asdict
import traceback

# Add paths
sys.path.append('/home/brian/projects/Digimons')
sys.path.append('/home/brian/projects/Digimons/tool_compatability/poc/vertical_slice')

@dataclass
class PipelineResult:
    """Result from running pipeline on a document"""
    document_id: str
    success: bool
    entities_found: List[Dict[str, str]]
    relationships_found: List[Dict[str, str]]
    reported_uncertainty: float
    execution_time: float
    memory_used: int
    error_message: str = None
    step_uncertainties: List[float] = None
    step_reasonings: List[str] = None

@dataclass 
class EvidenceMetrics:
    """Calculated metrics for a document"""
    document_id: str
    precision: float
    recall: float
    f1_score: float
    uncertainty_error: float  # abs(reported - expected)
    entity_precision: float
    entity_recall: float
    relationship_precision: float
    relationship_recall: float
    execution_time: float
    complexity_level: str

class ThesisEvidenceCollector:
    """Collect evidence for thesis evaluation"""
    
    def __init__(self, ground_truth_dir: str, output_dir: str = "thesis_results"):
        self.ground_truth_dir = ground_truth_dir
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # Initialize framework components
        self._initialize_framework()
        
        # Results storage
        self.results_db = f"{output_dir}/thesis_results.db"
        self._setup_results_database()
    
    def _initialize_framework(self):
        """Initialize the KGAS framework and tools"""
        from neo4j import GraphDatabase
        from dotenv import load_dotenv
        
        # Load environment
        load_dotenv('/home/brian/projects/Digimons/.env')
        
        # Initialize framework
        from framework.clean_framework import CleanToolFramework, ToolCapabilities, DataType
        from tools.text_loader_v3 import TextLoaderV3
        from tools.knowledge_graph_extractor import KnowledgeGraphExtractor
        from tools.graph_persister import GraphPersister
        
        # Create framework
        self.neo4j_driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "devpassword"))
        self.framework = CleanToolFramework("bolt://localhost:7687", "vertical_slice.db")
        
        # Register tools
        self.framework.register_tool(TextLoaderV3(), ToolCapabilities(
            tool_id="TextLoaderV3",
            input_type=DataType.FILE,
            output_type=DataType.TEXT,
            input_construct="file_path",
            output_construct="character_sequence",
            transformation_type="text_extraction"
        ))
        
        self.framework.register_tool(KnowledgeGraphExtractor(), ToolCapabilities(
            tool_id="KnowledgeGraphExtractor",
            input_type=DataType.TEXT,
            output_type=DataType.KNOWLEDGE_GRAPH,
            input_construct="character_sequence",
            output_construct="knowledge_graph",
            transformation_type="knowledge_graph_extraction"
        ))
        
        self.framework.register_tool(
            GraphPersister(self.framework.neo4j, self.framework.identity, self.framework.crossmodal),
            ToolCapabilities(
                tool_id="GraphPersister",
                input_type=DataType.KNOWLEDGE_GRAPH,
                output_type=DataType.NEO4J_GRAPH,
                input_construct="knowledge_graph",
                output_construct="persisted_graph",
                transformation_type="graph_persistence"
            )
        )
        
        print("✅ Framework initialized with 3 tools")
    
    def _setup_results_database(self):
        """Create results database for metrics"""
        conn = sqlite3.connect(self.results_db)
        
        # Pipeline results table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS pipeline_results (
                document_id TEXT PRIMARY KEY,
                complexity_level TEXT,
                success BOOLEAN,
                entities_found_count INTEGER,
                relationships_found_count INTEGER,
                reported_uncertainty REAL,
                expected_uncertainty REAL,
                execution_time REAL,
                memory_used INTEGER,
                error_message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Metrics table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS evidence_metrics (
                document_id TEXT PRIMARY KEY,
                complexity_level TEXT,
                precision REAL,
                recall REAL,
                f1_score REAL,
                entity_precision REAL,
                entity_recall REAL,
                relationship_precision REAL,
                relationship_recall REAL,
                uncertainty_error REAL,
                execution_time REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Entity comparison table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS entity_comparison (
                document_id TEXT,
                entity_name TEXT,
                entity_type TEXT,
                found BOOLEAN,
                expected BOOLEAN,
                confidence REAL,
                PRIMARY KEY (document_id, entity_name, entity_type)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def run_pipeline_on_document(self, document_path: str, metadata: Dict) -> PipelineResult:
        """Run the KGAS pipeline on a single document"""
        import psutil
        process = psutil.Process()
        
        start_time = time.time()
        start_memory = process.memory_info().rss
        
        try:
            # Find and execute chain
            chain = self.framework.find_chain(DataType.FILE, DataType.NEO4J_GRAPH)
            result = self.framework.execute_chain(chain, document_path)
            
            if result.success:
                # Extract entities and relationships from Neo4j
                entities_found, relationships_found = self._extract_from_neo4j(metadata['document_id'])
                
                return PipelineResult(
                    document_id=metadata['document_id'],
                    success=True,
                    entities_found=entities_found,
                    relationships_found=relationships_found,
                    reported_uncertainty=result.total_uncertainty,
                    execution_time=time.time() - start_time,
                    memory_used=process.memory_info().rss - start_memory,
                    step_uncertainties=result.step_uncertainties,
                    step_reasonings=result.step_reasonings
                )
            else:
                return PipelineResult(
                    document_id=metadata['document_id'],
                    success=False,
                    entities_found=[],
                    relationships_found=[],
                    reported_uncertainty=1.0,
                    execution_time=time.time() - start_time,
                    memory_used=process.memory_info().rss - start_memory,
                    error_message=str(result.error) if hasattr(result, 'error') else "Unknown error"
                )
                
        except Exception as e:
            return PipelineResult(
                document_id=metadata['document_id'],
                success=False,
                entities_found=[],
                relationships_found=[],
                reported_uncertainty=1.0,
                execution_time=time.time() - start_time,
                memory_used=process.memory_info().rss - start_memory,
                error_message=str(e)
            )
    
    def _extract_from_neo4j(self, document_id: str) -> Tuple[List[Dict], List[Dict]]:
        """Extract entities and relationships from Neo4j for a document"""
        entities = []
        relationships = []
        
        with self.neo4j_driver.session() as session:
            # Get entities (using VSEntity namespace)
            entity_query = """
            MATCH (e:VSEntity)
            WHERE e.source_document = $doc_id OR e.document_id = $doc_id
            RETURN e.entity_id as id, e.canonical_name as name, e.entity_type as type
            """
            entity_result = session.run(entity_query, doc_id=document_id)
            entities = [dict(record) for record in entity_result]
            
            # Get relationships
            rel_query = """
            MATCH (s:VSEntity)-[r]->(t:VSEntity)
            WHERE s.source_document = $doc_id OR s.document_id = $doc_id
            RETURN s.canonical_name as source, t.canonical_name as target, type(r) as type
            """
            rel_result = session.run(rel_query, doc_id=document_id)
            relationships = [dict(record) for record in rel_result]
            
            # Clean up after extraction (for next document)
            cleanup_query = """
            MATCH (e:VSEntity)
            WHERE e.source_document = $doc_id OR e.document_id = $doc_id
            DETACH DELETE e
            """
            session.run(cleanup_query, doc_id=document_id)
        
        return entities, relationships
    
    def calculate_metrics(self, result: PipelineResult, ground_truth: Dict) -> EvidenceMetrics:
        """Calculate precision, recall, and F1 for a document"""
        
        # Entity metrics
        expected_entities = set((e['name'], e['type']) for e in ground_truth['expected_entities'])
        found_entities = set((e['name'], e['type']) for e in result.entities_found)
        
        entity_tp = len(expected_entities & found_entities)
        entity_fp = len(found_entities - expected_entities)
        entity_fn = len(expected_entities - found_entities)
        
        entity_precision = entity_tp / (entity_tp + entity_fp) if (entity_tp + entity_fp) > 0 else 0
        entity_recall = entity_tp / (entity_tp + entity_fn) if (entity_tp + entity_fn) > 0 else 0
        
        # Relationship metrics
        expected_rels = set((r['source'], r['target'], r['type']) for r in ground_truth['expected_relationships'])
        found_rels = set((r['source'], r['target'], r['type']) for r in result.relationships_found)
        
        rel_tp = len(expected_rels & found_rels)
        rel_fp = len(found_rels - expected_rels)
        rel_fn = len(expected_rels - found_rels)
        
        rel_precision = rel_tp / (rel_tp + rel_fp) if (rel_tp + rel_fp) > 0 else 0
        rel_recall = rel_tp / (rel_tp + rel_fn) if (rel_tp + rel_fn) > 0 else 0
        
        # Combined metrics
        precision = (entity_precision + rel_precision) / 2
        recall = (entity_recall + rel_recall) / 2
        f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        
        # Uncertainty error
        uncertainty_error = abs(result.reported_uncertainty - ground_truth['expected_uncertainty'])
        
        return EvidenceMetrics(
            document_id=ground_truth['document_id'],
            precision=precision,
            recall=recall,
            f1_score=f1_score,
            uncertainty_error=uncertainty_error,
            entity_precision=entity_precision,
            entity_recall=entity_recall,
            relationship_precision=rel_precision,
            relationship_recall=rel_recall,
            execution_time=result.execution_time,
            complexity_level=ground_truth['complexity_level']
        )
    
    def save_results(self, result: PipelineResult, metrics: EvidenceMetrics, ground_truth: Dict):
        """Save results to database"""
        conn = sqlite3.connect(self.results_db)
        
        # Save pipeline result
        conn.execute("""
            INSERT OR REPLACE INTO pipeline_results 
            (document_id, complexity_level, success, entities_found_count, relationships_found_count,
             reported_uncertainty, expected_uncertainty, execution_time, memory_used, error_message)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            result.document_id,
            ground_truth['complexity_level'],
            result.success,
            len(result.entities_found),
            len(result.relationships_found),
            result.reported_uncertainty,
            ground_truth['expected_uncertainty'],
            result.execution_time,
            result.memory_used,
            result.error_message
        ))
        
        # Save metrics
        conn.execute("""
            INSERT OR REPLACE INTO evidence_metrics
            (document_id, complexity_level, precision, recall, f1_score,
             entity_precision, entity_recall, relationship_precision, relationship_recall,
             uncertainty_error, execution_time)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            metrics.document_id,
            metrics.complexity_level,
            metrics.precision,
            metrics.recall,
            metrics.f1_score,
            metrics.entity_precision,
            metrics.entity_recall,
            metrics.relationship_precision,
            metrics.relationship_recall,
            metrics.uncertainty_error,
            metrics.execution_time
        ))
        
        # Save entity comparison
        for expected in ground_truth['expected_entities']:
            found = any(e['name'] == expected['name'] and e['type'] == expected['type'] 
                       for e in result.entities_found)
            conn.execute("""
                INSERT OR REPLACE INTO entity_comparison
                (document_id, entity_name, entity_type, found, expected, confidence)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                result.document_id,
                expected['name'],
                expected['type'],
                found,
                True,
                expected.get('confidence', 0.0)
            ))
        
        conn.commit()
        conn.close()
    
    def run_full_collection(self):
        """Run evidence collection on all ground truth documents"""
        print("\n=== Starting Thesis Evidence Collection ===\n")
        
        # Load master metadata
        with open(f"{self.ground_truth_dir}/master_metadata.json") as f:
            master_data = json.load(f)
        
        all_results = []
        all_metrics = []
        
        for doc_summary in master_data['documents']:
            doc_id = doc_summary['id']
            print(f"\n📄 Processing: {doc_id}")
            
            # Load ground truth
            metadata_path = f"{self.ground_truth_dir}/metadata/{doc_id}.json"
            document_path = f"{self.ground_truth_dir}/documents/{doc_id}.txt"
            
            with open(metadata_path) as f:
                ground_truth = json.load(f)
            
            # Run pipeline
            result = self.run_pipeline_on_document(document_path, ground_truth)
            
            # Calculate metrics
            if result.success:
                metrics = self.calculate_metrics(result, ground_truth)
                print(f"   ✅ Success - F1: {metrics.f1_score:.3f}, Uncertainty: {result.reported_uncertainty:.3f}")
            else:
                metrics = EvidenceMetrics(
                    document_id=doc_id,
                    precision=0, recall=0, f1_score=0,
                    uncertainty_error=1.0,
                    entity_precision=0, entity_recall=0,
                    relationship_precision=0, relationship_recall=0,
                    execution_time=result.execution_time,
                    complexity_level=ground_truth['complexity_level']
                )
                print(f"   ❌ Failed: {result.error_message}")
            
            # Save results
            self.save_results(result, metrics, ground_truth)
            all_results.append(result)
            all_metrics.append(metrics)
        
        # Generate summary report
        self._generate_summary_report(all_metrics)
        
        print("\n✅ Evidence collection complete!")
        print(f"📊 Results saved to: {self.output_dir}")
        
        return all_results, all_metrics
    
    def _generate_summary_report(self, metrics: List[EvidenceMetrics]):
        """Generate summary statistics"""
        import numpy as np
        
        # Group by complexity
        by_complexity = {}
        for m in metrics:
            if m.complexity_level not in by_complexity:
                by_complexity[m.complexity_level] = []
            by_complexity[m.complexity_level].append(m)
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "total_documents": len(metrics),
            "overall_metrics": {
                "mean_f1": np.mean([m.f1_score for m in metrics]),
                "mean_precision": np.mean([m.precision for m in metrics]),
                "mean_recall": np.mean([m.recall for m in metrics]),
                "mean_uncertainty_error": np.mean([m.uncertainty_error for m in metrics])
            },
            "by_complexity": {}
        }
        
        for complexity, complexity_metrics in by_complexity.items():
            report["by_complexity"][complexity] = {
                "count": len(complexity_metrics),
                "mean_f1": np.mean([m.f1_score for m in complexity_metrics]),
                "mean_precision": np.mean([m.precision for m in complexity_metrics]),
                "mean_recall": np.mean([m.recall for m in complexity_metrics]),
                "mean_uncertainty_error": np.mean([m.uncertainty_error for m in complexity_metrics])
            }
        
        # Save report
        with open(f"{self.output_dir}/summary_report.json", 'w') as f:
            json.dump(report, f, indent=2)
        
        print("\n📊 Summary Report:")
        print(f"   Overall F1: {report['overall_metrics']['mean_f1']:.3f}")
        print(f"   Overall Precision: {report['overall_metrics']['mean_precision']:.3f}")
        print(f"   Overall Recall: {report['overall_metrics']['mean_recall']:.3f}")
        print(f"   Mean Uncertainty Error: {report['overall_metrics']['mean_uncertainty_error']:.3f}")


if __name__ == "__main__":
    collector = ThesisEvidenceCollector(
        ground_truth_dir="/home/brian/projects/Digimons/tool_compatability/poc/vertical_slice/thesis_evidence/ground_truth_data",
        output_dir="/home/brian/projects/Digimons/tool_compatability/poc/vertical_slice/thesis_evidence/thesis_results"
    )
    
    try:
        results, metrics = collector.run_full_collection()
    finally:
        # Clean up
        collector.framework.cleanup()
        collector.neo4j_driver.close()