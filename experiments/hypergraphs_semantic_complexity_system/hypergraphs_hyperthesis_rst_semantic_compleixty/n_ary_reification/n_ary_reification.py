import json
import networkx as nx
from itertools import combinations
import logging
from datetime import datetime, timedelta
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv
from networkx.algorithms import community
from networkx.algorithms.components import connected_components
from pyvis.network import Network

# Set up logging with a cleaner format
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Disable verbose logging from other libraries
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)
logging.getLogger("openai").setLevel(logging.WARNING)

# Load environment variables
load_dotenv()

# Configure LangSmith tracing - only if key is properly set
if os.getenv("LANGCHAIN_API_KEY") and os.getenv("LANGCHAIN_API_KEY") != "your_langsmith_key":
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
else:
    os.environ["LANGCHAIN_TRACING_V2"] = "false"

class NaryReificationFinder:
    def __init__(self, graph_file):
        self.graph_file = graph_file
        self.graph = nx.DiGraph()
        self.load_graph()
        
        # Initialize LLM with GPT-4o-mini
        self.llm = ChatOpenAI(
            model="gpt-4o-mini", #this is the most current mode
            temperature=0,
            verbose=True
        )
        
        # Set up output parser
        self.output_parser = JsonOutputParser()
        
        # Create prompt template
        self.prompt = PromptTemplate(
            template="""You are an expert in knowledge graph analysis and n-ary relationship identification.

Analyze these connected entities and their relationships to determine if they should be reified into a single n-ary relationship.

Entities and Relationships:
{entities_and_relations}

Examples of valid n-ary patterns:

1. Movie Casting:
   - Movie --[CAST_IN]--> Actor --[PLAYED_ROLE]--> Character
   Reified as: CastingRelationship
   - CastingRelationship --[Movie_Role]--> Movie
   - CastingRelationship --[Actor_Role]--> Actor
   - CastingRelationship --[Character_Role]--> Character

2. System Integration:
   - Component --[PART_OF]--> Platform
   - Component --[INFLUENCES]--> OtherComponent
   Reified as: SystemIntegration
   - SystemIntegration --[Platform_Role]--> Platform
   - SystemIntegration --[Component_Role]--> Component
   - SystemIntegration --[Influencer_Role]--> OtherComponent

3. Publication Authorship:
   - Author --[WROTE]--> Paper
   - Author --[AFFILIATED_WITH]--> Institution
   - Paper --[PUBLISHED_IN]--> Journal
   Reified as: AuthorshipRelation
   - AuthorshipRelation --[Author_Role]--> Author
   - AuthorshipRelation --[Paper_Role]--> Paper
   - AuthorshipRelation --[Institution_Role]--> Institution
   - AuthorshipRelation --[Journal_Role]--> Journal

Consider:
1. Semantic Coherence: Do these relationships form a meaningful unit that describes a single concept or event?
2. Role Identification: Can each entity's role in the relationship be clearly defined?
3. Information Preservation: Would reification preserve or enhance the original meaning?
4. Pattern Recognition: Does this match known n-ary patterns like the examples above?
5. Context Utilization: Do the provided text snippets support the relationship's coherence?
6. Only reify if you can do so without losing any information or creating ambiguity.

Return your analysis in the following JSON format:
{format_instructions}

The JSON should include:
- should_reify: boolean indicating if these should be combined
- suggested_name: string name for the reified relationship (or null if should_reify is false)
- explanation: detailed explanation including:
  - Pattern identification
  - Role assignments
  - Reasoning based on context
  - How the reification enhances understanding
""",
            input_variables=["entities_and_relations"],
            partial_variables={"format_instructions": self.output_parser.get_format_instructions()}
        )

        # Create the chain
        self.chain = self.prompt | self.llm | self.output_parser
        
    def load_graph(self):
        """Load the graph from JSON file."""
        try:
            with open(self.graph_file, 'r') as f:
                data = json.load(f)
                
            # Store metadata
            self.metadata = data.get('metadata', {})
            
            # Store documents for context
            self.documents = data.get('documents', {})
            
            # Load nodes with their metadata
            for node in data.get('nodes', []):
                self.graph.add_node(
                    node['id'],
                    label=node.get('label', ''),
                    type=node.get('type', ''),
                    documents=node.get('documents', {}),
                    text_units=node.get('text_units', {})
                )
                
            # Load edges with their relationships and metadata
            for edge in data.get('edges', []):
                self.graph.add_edge(
                    edge['source'], 
                    edge['target'],
                    relationship=edge.get('relationship', ''),
                    documents=edge.get('documents', {}),
                    text_units=edge.get('text_units', {})
                )
            
            logger.info(f"Loaded graph with {self.graph.number_of_nodes()} nodes and "
                        f"{self.graph.number_of_edges()} edges")
            
            # Log sample data to verify content
            logger.debug(f"Graph metadata: {self.metadata}")
            if self.graph.nodes:
                sample_node = list(self.graph.nodes(data=True))[0]
                logger.debug(f"Sample node: {sample_node}")
                
        except Exception as e:
            logger.error(f"Error loading graph: {str(e)}")
            
    def _is_valid_nary_candidate(self, subgraph):
        """Enhanced validation of potential n-ary relationships."""
        # Check for semantic consistency
        relations = set(data['relationship'] for _, _, data in subgraph.edges(data=True))
        
        # Example semantic rules (these would need to be customized):
        incompatible_pairs = {
            ('PART_OF', 'INFLUENCES'),  # Updated with actual relationships from your graph
            ('INFLUENCES', 'RELATED_TO')
        }
        
        for rel1, rel2 in combinations(relations, 2):
            if (rel1, rel2) in incompatible_pairs:
                return False
            
        return True
    
    def find_potential_nary_subgraphs(self, min_size=3, max_size=5, density_threshold=0.5):
        """Find potential n-ary relationships using a clustering-first approach."""
        logger.info("\n=== Starting N-ary Relationship Detection ===")
        logger.info(f"Parameters:")
        logger.info(f"- Minimum cluster size: {min_size}")
        logger.info(f"- Maximum cluster size: {max_size}")
        logger.info(f"- Density threshold: {density_threshold}")
        
        potential_reifications = []
        
        # Convert to undirected graph for initial clustering
        logger.info("\n=== Phase 1: Initial Graph Analysis ===")
        undirected = self.graph.to_undirected()
        logger.info(f"Converting directed graph ({self.graph.number_of_nodes()} nodes, {self.graph.number_of_edges()} edges) to undirected")
        logger.info(f"Undirected graph has {undirected.number_of_edges()} edges")
        
        # First get connected components
        logger.info("\n=== Phase 2: Connected Components Analysis ===")
        components = list(connected_components(undirected))
        logger.info(f"Found {len(components)} connected components")
        
        # Component size distribution
        component_sizes = [len(c) for c in components]
        logger.info(f"Component size distribution:")
        logger.info(f"- Min: {min(component_sizes)}")
        logger.info(f"- Max: {max(component_sizes)}")
        logger.info(f"- Average: {sum(component_sizes)/len(component_sizes):.1f}")
        
        logger.info("\n=== Phase 3: Community Detection ===")
        for idx, component in enumerate(components, 1):
            if len(component) < min_size:
                continue
            
            logger.info(f"\nAnalyzing component {idx} ({len(component)} nodes)")
            
            # Get the subgraph for this component
            component_graph = undirected.subgraph(component)
            
            # Find communities within the component using Louvain method
            logger.info("Applying Louvain community detection...")
            communities = community.louvain_communities(component_graph)
            logger.info(f"Found {len(communities)} clusters")
            
            # Analyze each community
            logger.info("\n=== Phase 4: Cluster Analysis ===")
            for cluster_idx, cluster in enumerate(communities):
                if min_size <= len(cluster) <= max_size:
                    logger.info(f"\nAnalyzing cluster {cluster_idx + 1}:")
                    logger.info(f"- Size: {len(cluster)} nodes")
                    
                    # Get the directed subgraph for this cluster
                    cluster_graph = self.graph.subgraph(cluster)
                    
                    # Check edge density
                    n = len(cluster)
                    max_edges = n * (n-1)  # Maximum possible directed edges
                    actual_edges = cluster_graph.number_of_edges()
                    density = actual_edges / max_edges
                    
                    logger.info(f"- Edge density: {density:.2f} ({actual_edges} edges out of {max_edges} possible)")
                    
                    if density >= density_threshold:
                        # Get node labels for logging
                        node_labels = [f"{n}({self.graph.nodes[n].get('label', 'Unknown')})" for n in cluster]
                        logger.info(f"Found densely connected cluster above threshold {density_threshold}:")
                        logger.info(f"- Nodes: {', '.join(node_labels)}")
                        
                        # Get relations for the cluster
                        relations = self._get_subgraph_relations(cluster_graph)
                        logger.info(f"- Relationships: {[rel['relationship'] for rel in relations]}")
                        
                        # Only add to potential reifications if density threshold is met
                        potential_reifications.append({
                            'nodes': list(cluster),
                            'relationships': relations
                        })
                        
        logger.info(f"\n=== Analysis Complete ===")
        logger.info(f"Found {len(potential_reifications)} potential n-ary relationships")
        return potential_reifications
    
    def _is_fully_connected(self, subgraph):
        """Check if a subgraph is fully connected."""
        n = subgraph.number_of_nodes()
        return subgraph.number_of_edges() == (n * (n-1)) // 2
    
    def _get_subgraph_relations(self, subgraph):
        """Get all relations in a subgraph."""
        relations = []
        for edge in subgraph.edges(data=True):
            relations.append({
                'source': edge[0],
                'target': edge[1],
                'relationship': edge[2].get('relationship', ''),
                'documents': edge[2].get('documents', {}),
                'text_units': edge[2].get('text_units', {})
            })
        return relations
    
    def _format_input(self, subgraph_info):
        """Format input for LLM analysis with proper context."""
        # Format entities with their labels and types
        entities_text = "Entities:\n" + "\n".join(
            f"- Entity {n} ({self.graph.nodes[n].get('label', 'Unknown')}) "
            f"[{self.graph.nodes[n].get('type', 'Unknown')}]"
            for n in subgraph_info['nodes']
        )
        
        # Format relationships with document context
        relations_text = "\nRelationships and their context:\n"
        for rel in subgraph_info['relationships']:
            source_label = self.graph.nodes[rel['source']].get('label', str(rel['source']))
            target_label = self.graph.nodes[rel['target']].get('label', str(rel['target']))
            
            relations_text += (f"\n- {source_label} --[{rel['relationship']}]--> {target_label}\n")
            
            # Add context from documents
            if rel.get('text_units') and rel.get('documents'):
                for doc_id, units in rel['text_units'].items():
                    if doc_id in self.documents:
                        doc = self.documents[doc_id]
                        for unit_id in units:
                            for unit in doc.get('units', []):
                                if unit['unit_id'] == unit_id:
                                    relations_text += f"  Context: {unit['text']}\n"
        
        return f"{entities_text}\n{relations_text}"
    
    def analyze_potential_reification(self, subgraph_info):
        """Analyze if a fully connected subgraph should be reified using LangChain."""
        try:
            # Format input
            formatted_input = self._format_input(subgraph_info)
            
            # Use LCEL for chain execution
            result = self.chain.invoke({"entities_and_relations": formatted_input})
            
            logger.debug(f"LLM Analysis Result: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Error in LLM analysis: {str(e)}")
            return {
                "should_reify": False,
                "suggested_name": None,
                "explanation": f"Error in analysis: {str(e)}"
            }

    def save_analysis_results(self, potential_reifications, output_file="n_ary_analysis_results.json"):
        """Save the analysis results of potential n-ary relationships."""
        logger.info(f"\nStarting analysis of {len(potential_reifications)} potential reifications")
        
        results = {
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "total_subgraphs_analyzed": len(potential_reifications),
                "graph_info": self.metadata
            },
            "subgraphs": []
        }
        
        for idx, subgraph_info in enumerate(potential_reifications, 1):
            logger.info(f"\nAnalyzing subgraph {idx}/{len(potential_reifications)}")
            
            # Get node details
            nodes = [{
                "id": n,
                "label": self.graph.nodes[n].get('label', 'Unknown'),
                "type": self.graph.nodes[n].get('type', 'Unknown')
            } for n in subgraph_info['nodes']]
            
            node_summary = [f"{n['id']}({n['label']})" for n in nodes]
            logger.info(f"Nodes: {', '.join(node_summary)}")
            
            # Get relationship details with context
            relationships = []
            for rel in subgraph_info['relationships']:
                source_label = self.graph.nodes[rel['source']].get('label', 'Unknown')
                target_label = self.graph.nodes[rel['target']].get('label', 'Unknown')
                logger.debug(f"Processing relationship: {source_label} --[{rel['relationship']}]--> {target_label}")
                
                rel_info = {
                    "source": {"id": rel['source'], "label": source_label},
                    "target": {"id": rel['target'], "label": target_label},
                    "relationship": rel['relationship'],
                    "context": []
                }
                
                # Add document context
                if rel.get('text_units') and rel.get('documents'):
                    context_count = 0
                    for doc_id, units in rel['text_units'].items():
                        if doc_id in self.documents:
                            doc = self.documents[doc_id]
                            for unit_id in units:
                                for unit in doc.get('units', []):
                                    if unit['unit_id'] == unit_id:
                                        context_count += 1
                                        rel_info["context"].append({
                                            "doc_id": doc_id,
                                            "text": unit['text']
                                        })
                    logger.debug(f"Found {context_count} context snippets for relationship")
                
                relationships.append(rel_info)
            
            # Get LLM analysis
            logger.info("Requesting LLM analysis...")
            analysis = self.analyze_potential_reification(subgraph_info)
            logger.info(f"LLM recommendation: {analysis.get('should_reify', False)}")
            if analysis.get('should_reify'):
                logger.info(f"Suggested name: {analysis.get('suggested_name')}")
            
            # Combine all information
            subgraph_result = {
                "nodes": nodes,
                "relationships": relationships,
                "llm_analysis": analysis
            }
            
            results["subgraphs"].append(subgraph_result)
        
        # Save to file
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            logger.info(f"\nAnalysis results saved to {output_file}")
        except Exception as e:
            logger.error(f"Error saving analysis results: {str(e)}")

    def visualize_graph(self, output_file="graph_visualization.html", height="750px", width="100%"):
        """Create interactive visualization of the graph."""
        net = Network(height=height, width=width, notebook=False, directed=True)
        net.barnes_hut()  # Add physics
        
        # Add nodes with labels
        for node_id in self.graph.nodes():
            label = self.graph.nodes[node_id].get('label', str(node_id))
            node_type = self.graph.nodes[node_id].get('type', 'Unknown')
            title = f"ID: {node_id}\nType: {node_type}"
            net.add_node(node_id, label=label, title=title)
        
        # Add edges with relationships
        for edge in self.graph.edges(data=True):
            source, target = edge[0], edge[1]
            relationship = edge[2].get('relationship', '')
            net.add_edge(source, target, label=relationship)
        
        # Generate the HTML file
        try:
            net.write_html(output_file)
            logger.info(f"Graph visualization saved to {output_file}")
        except Exception as e:
            logger.error(f"Error saving visualization: {str(e)}")

    def visualize_reified_graph(self, reification_results, output_file="reified_graph_visualization.html"):
        """Create visualization of the graph after reification."""
        net = Network(height="750px", width="100%", notebook=False, directed=True)
        net.barnes_hut()
        net.toggle_physics(True)
        
        # Track nodes that are part of reifications
        reified_nodes = set()
        
        # First add all original nodes
        for node_id in self.graph.nodes():
            label = self.graph.nodes[node_id].get('label', str(node_id))
            node_type = self.graph.nodes[node_id].get('type', 'Unknown')
            title = f"ID: {node_id}\nType: {node_type}"
            net.add_node(node_id, 
                        label=label, 
                        title=title,
                        color='#97c2fc',
                        size=20)
        
        # Add reification nodes and edges with roles
        next_node_id = max(self.graph.nodes()) + 1
        
        for result in reification_results["subgraphs"]:
            if result["llm_analysis"]["should_reify"]:
                # Create reification node
                reification_name = result["llm_analysis"]["suggested_name"]
                reification_id = next_node_id
                next_node_id += 1
                
                # Get roles for this reification
                nodes = [n["id"] for n in result["nodes"]]
                pattern_name, roles = self._determine_roles(nodes, result["relationships"])
                
                # Safely get explanation and truncate if needed
                explanation = result["llm_analysis"].get("explanation", "No explanation provided")
                truncated_explanation = (explanation[:197] + "...") if len(explanation) > 200 else explanation
                
                net.add_node(reification_id, 
                            label=reification_name,
                            title=f"Pattern: {pattern_name}\n\n{truncated_explanation}",
                            color='#ff7f50',
                            shape='diamond',
                            size=30)
                
                # Add role-based edges
                for node in result["nodes"]:
                    node_id = node["id"]
                    reified_nodes.add(node_id)
                    role = roles[node_id]
                    
                    # Edge from reification to participant with role
                    net.add_edge(reification_id, 
                                node_id, 
                                label=role,
                                title=f"Role in {reification_name}",
                                color="#ff7f50",
                                arrows="to")
        
        # Add remaining original edges
        for edge in self.graph.edges(data=True):
            source, target = edge[0], edge[1]
            if not (source in reified_nodes and target in reified_nodes):
                relationship = edge[2].get('relationship', '')
                net.add_edge(source, 
                            target, 
                            label=relationship,
                            color="#97c2fc",
                            arrows="to")
        
        try:
            net.write_html(output_file)
            logger.info(f"Reified graph visualization saved to {output_file}")
        except Exception as e:
            logger.error(f"Error saving reified visualization: {str(e)}")

    def _determine_roles(self, nodes, relationships):
        """Determine the semantic roles of nodes in the n-ary relationship."""
        role_patterns = {
            "Casting": {
                "indicators": {"CAST_IN", "PLAYED_ROLE"},
                "roles": {
                    "Movie_Role": lambda n: any(r["relationship"] == "CAST_IN" and r["source"] == n 
                                              for r in relationships),
                    "Actor_Role": lambda n: any(r["relationship"] == "CAST_IN" and r["target"] == n 
                                              for r in relationships),
                    "Character_Role": lambda n: any(r["relationship"] == "PLAYED_ROLE" and r["target"] == n 
                                                  for r in relationships)
                }
            },
            "SystemIntegration": {
                "indicators": {"PART_OF", "INFLUENCES"},
                "roles": {
                    "Platform_Role": lambda n: any(r["relationship"] == "PART_OF" and r["target"] == n 
                                                 for r in relationships),
                    "Component_Role": lambda n: any(r["relationship"] == "PART_OF" and r["source"] == n 
                                                  for r in relationships),
                    "Influencer_Role": lambda n: any(r["relationship"] == "INFLUENCES" and r["source"] == n 
                                                   for r in relationships)
                }
            },
            "Authorship": {
                "indicators": {"WROTE", "AFFILIATED_WITH", "PUBLISHED_IN"},
                "roles": {
                    "Author_Role": lambda n: any(r["relationship"] == "WROTE" and r["source"] == n 
                                               for r in relationships),
                    "Paper_Role": lambda n: any(r["relationship"] == "WROTE" and r["target"] == n 
                                              for r in relationships),
                    "Institution_Role": lambda n: any(r["relationship"] == "AFFILIATED_WITH" and r["target"] == n 
                                                    for r in relationships),
                    "Journal_Role": lambda n: any(r["relationship"] == "PUBLISHED_IN" and r["target"] == n 
                                                for r in relationships)
                }
            }
        }
        
        # Find matching pattern
        for pattern_name, pattern in role_patterns.items():
            relationship_types = {r["relationship"] for r in relationships}
            if pattern["indicators"].issubset(relationship_types):
                roles = {}
                for node in nodes:
                    for role_name, role_check in pattern["roles"].items():
                        if role_check(node):
                            roles[node] = role_name
                            break
                    if node not in roles:
                        roles[node] = "Participant"  # Default role
                return pattern_name, roles
        
        # Default roles if no pattern matches
        return "Generic", {node: "Participant" for node in nodes}

    def maintain_edges(self, original_graph, reified_subgraphs):
        """Maintain edge consistency after reification with semantic roles."""
        logger.info("\n=== Starting Edge Maintenance ===")
        
        reified_graph = original_graph.copy()
        maintenance_log = []
        
        for subgraph in reified_subgraphs:
            if not subgraph["llm_analysis"]["should_reify"]:
                continue
            
            reification_name = subgraph["llm_analysis"]["suggested_name"]
            nodes = [n["id"] for n in subgraph["nodes"]]
            logger.info(f"\nProcessing reification: {reification_name}")
            
            # Changed "relations" to "relationships"
            pattern_name, roles = self._determine_roles(nodes, subgraph["relationships"])
            logger.info(f"Identified pattern: {pattern_name}")
            logger.info("Assigned roles:")
            for node, role in roles.items():
                node_label = self.graph.nodes[node].get('label', str(node))
                logger.info(f"- {node_label}: {role}")
            
            # Create reification node
            reification_id = max(reified_graph.nodes()) + 1
            reified_graph.add_node(
                reification_id,
                label=reification_name,
                type="Reification",
                pattern=pattern_name,
                explanation=subgraph["llm_analysis"]["explanation"]
            )
            
            # Track edges to remove and add
            edges_to_remove = []
            edges_to_add = []
            
            # Remove original edges and create role-based edges
            for source, target, data in original_graph.edges(data=True):
                if source in nodes and target in nodes:
                    edges_to_remove.append((source, target))
                    
            for node in nodes:
                # Add edge from reification to node with role
                edges_to_add.append({
                    'source': reification_id,
                    'target': node,
                    'data': {
                        'relationship': roles[node],  # Use the role as the relationship type
                        'role': roles[node],
                        'pattern': pattern_name,
                        'reification': reification_name
                    }
                })
            
            # Log changes with roles
            maintenance_log.append({
                'reification_id': reification_id,
                'reification_name': reification_name,
                'pattern': pattern_name,
                'roles': {str(k): v for k, v in roles.items()},
                'removed_edges': [
                    {
                        'source': source,
                        'target': target,
                        'relationship': reified_graph.edges[source, target].get('relationship')
                    }
                    for source, target in edges_to_remove
                ],
                'added_edges': edges_to_add
            })
            
            # Apply changes
            logger.info(f"Removing {len(edges_to_remove)} original edges")
            for source, target in edges_to_remove:
                reified_graph.remove_edge(source, target)
            
            logger.info(f"Adding {len(edges_to_add)} role-based edges")
            for edge in edges_to_add:
                reified_graph.add_edge(
                    edge['source'],
                    edge['target'],
                    **edge['data']
                )
        
        # Save maintenance log with role information
        try:
            log_file = os.path.join(os.path.dirname(self.graph_file), "output", "edge_maintenance_log.json")
            with open(log_file, 'w') as f:
                json.dump(maintenance_log, f, indent=2)
            logger.info(f"\nEdge maintenance log saved to {log_file}")
        except Exception as e:
            logger.error(f"Error saving maintenance log: {str(e)}")
        
        return reified_graph

    def apply_reification(self, reification_results):
        """Apply reification changes to the graph."""
        logger.info("\n=== Applying Reification Changes ===")
        
        # Maintain edge consistency
        self.graph = self.maintain_edges(self.graph, reification_results["subgraphs"])
        
        # Update visualization
        output_dir = os.path.join(os.path.dirname(self.graph_file), "output")
        self.visualize_reified_graph(reification_results, os.path.join(output_dir, "reified_graph.html"))
        
        # Save updated graph
        try:
            updated_graph_file = os.path.join(output_dir, "reified_graph.json")
            graph_data = {
                "metadata": {
                    "timestamp": datetime.now().isoformat(),
                    "original_graph": self.graph_file,
                    "reification_count": len([s for s in reification_results["subgraphs"] 
                                           if s["llm_analysis"]["should_reify"]])
                },
                "nodes": [
                    {
                        "id": n,
                        "label": self.graph.nodes[n].get('label', ''),
                        "type": self.graph.nodes[n].get('type', ''),
                        **{k: v for k, v in self.graph.nodes[n].items() 
                           if k not in ['label', 'type']}
                    }
                    for n in self.graph.nodes()
                ],
                "edges": [
                    {
                        "source": u,
                        "target": v,
                        **data
                    }
                    for u, v, data in self.graph.edges(data=True)
                ]
            }
            
            with open(updated_graph_file, 'w') as f:
                json.dump(graph_data, f, indent=2)
            logger.info(f"Updated graph saved to {updated_graph_file}")
            
        except Exception as e:
            logger.error(f"Error saving updated graph: {str(e)}")

def main():
    # Create output directory if it doesn't exist
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(script_dir, "output")
    os.makedirs(output_dir, exist_ok=True)
    
    # Initialize finder with correct path
    graph_path = os.path.join(script_dir, "graph.json")
    finder = NaryReificationFinder(graph_path)
    
    # Create initial visualization
    finder.visualize_graph(os.path.join(output_dir, "original_graph.html"))
    
    # Find and analyze potential n-ary relationships
    potential_nary = finder.find_potential_nary_subgraphs()
    logger.info(f"Found {len(potential_nary)} potential n-ary relationships")
    
    # Save analysis results
    results_file = os.path.join(output_dir, "n_ary_analysis_results.json")
    finder.save_analysis_results(potential_nary, results_file)
    
    # Load results and apply reification
    with open(results_file, 'r') as f:
        results = json.load(f)
    
    # Apply reification changes
    finder.apply_reification(results)

if __name__ == "__main__":
    main()


