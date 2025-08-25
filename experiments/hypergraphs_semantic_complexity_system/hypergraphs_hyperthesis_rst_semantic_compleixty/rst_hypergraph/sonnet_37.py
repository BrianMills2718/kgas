import re
import uuid
import json
import copy
from typing import List, Dict, Any, Tuple

import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
import numpy as np

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

class RSTHypergraphGenerator:
    def __init__(self, openai_api_key: str = None, model_name: str = "gpt-4o"):
        """Initialize the RST Hypergraph Generator.
        
        Args:
            openai_api_key: Your OpenAI API key
            model_name: The name of the OpenAI model to use
        """
        self.llm = ChatOpenAI(
            model=model_name,
            temperature=0,
            openai_api_key=openai_api_key
        )
        
        # Define the prompt template for RST hypergraph generation
        self.prompt = ChatPromptTemplate.from_template(
            """You are an expert in Rhetorical Structure Theory (RST) and discourse analysis. 
            I want you to create a rhetorical hypergraph directly from text without first creating a binary parse tree.

            # Comprehensive Background on RST and Hypergraphs:
            
            ## Rhetorical Structure Theory Basics:
            - RST analyzes how parts of a text relate to each other to create a coherent whole
            - Elementary Discourse Units (EDUs) are the minimal units of discourse analysis (typically clauses)
            - Relations connect EDUs to reflect the author's rhetorical intention
            - Traditional RST uses tree structures, but hypergraphs allow for more flexible representations
            
            ## Nucleus-Satellite vs. Multi-Nuclear Relations:
            - Nucleus-Satellite relations: One element (nucleus) is more central/important than the other(s) (satellites)
            - Multi-Nuclear relations: All connected elements have equal status/importance
            
            ## Elementary Discourse Units (EDUs):
            - Typically correspond to clauses or simple sentences
            - Should capture a single, complete thought or proposition
            - May include connectives ("because", "and", "if") to signal relations
            - Are indexed starting from 1 (not 0)
            - IMPORTANT: Separate causes and effects into different EDUs even within the same sentence
              CORRECT: "Because of all these issues" and "I won't be coming back" as separate EDUs
              INCORRECT: "Because of all these issues, I won't be coming back" as a single EDU
            
            ## Complete List of Common RST Relations:
            1. **Elaboration**: Satellite provides additional details about the nucleus
               Example: "I love this restaurant. [N] Their pasta dishes are exceptional. [S]"
            
            2. **Background**: Satellite provides context needed to understand the nucleus
               Example: "The company was founded in 1995. [S] Today, it's a global leader in AI. [N]"
            
            3. **Cause-Effect**: One element causes another
               - Primary pattern: Effect is nucleus, cause is satellite
               - Example: "I won't be coming back [N] because of all these issues. [S]"
               - Example: "Because it started raining, [S] I got soaked. [N]"
               - CRITICAL: Do NOT use "condition" for causality that has already occurred
            
            4. **Condition**: Satellite presents a hypothetical, future, or otherwise unrealized situation, and nucleus is contingent on it
               Example: "If it rains tomorrow, [S] we'll cancel the picnic. [N]"
               NOTE: ONLY use for hypothetical or unrealized situations, never for actual causes that have happened
            
            5. **Contrast**: Multi-nuclear relation comparing/contrasting elements
               Example: "John loves coffee [N] while Mary prefers tea. [N]"
            
            6. **Joint**: Multi-nuclear relation connecting elements of equal status without specific semantic relation
               Example: "The car needs new tires, [N] the oil needs changing, [N] and the brakes are squeaking. [N]"
               CRITICAL: Always group ALL parallel items in a SINGLE joint relation, never chain them
            
            7. **Concession**: Satellite appears to be incompatible but is actually compatible with nucleus
               Example: "Although I was tired, [S] I finished the report. [N]"
            
            8. **Enablement**: Satellite helps the reader perform action in nucleus
               Example: "To make the cake, [S] mix flour, sugar, and eggs. [N]"
            
            9. **Evaluation**: Satellite assesses the nucleus
               Example: "The stock market crashed yesterday. [N] This is a disaster for investors. [S]"
            
            10. **Purpose**: Satellite presents a goal, and nucleus is the means
                Example: "To lose weight, [S] I've been exercising daily. [N]"
            
            11. **Evidence**: Satellite provides evidence for the claim in nucleus
                Example: "Global warming is accelerating. [N] Arctic ice has decreased by 13% per decade. [S]"
            
            12. **Restatement**: Satellite restates nucleus in different words
                Example: "This is the best solution. [N] It's the optimal approach to our problem. [S]"
            
            13. **Result**: Satellite presents an outcome or result of the nucleus
                Example: "The company invested in new technology, [N] resulting in a 30% increase in productivity. [S]"
                
            ## Hypergraph Structure Requirements:
            - A hypergraph allows relations to connect multiple elements simultaneously
            - Each relation is represented as a hyperedge connecting nodes (EDUs or other relations)
            - Relations must form a connected structure with a single root that encompasses the entire text
            - Relations should represent the author's intended rhetorical organization, not just sequential order
            
            # CRITICAL RULES for Creating Valid RST Hypergraphs:
            
            1. **Proper EDU Segmentation**:
               - Split text into complete clauses
               - CRITICAL: Separate causes and effects into different EDUs even within the same sentence
               - Example: "Because it was raining, I stayed home" → Two EDUs: "Because it was raining" and "I stayed home"
            
            2. **One-Based Indexing**: Always use 1-based indexing for EDUs (start at 1, not 0)
               CORRECT: "nuclei": [1, 2, 3]
               INCORRECT: "nuclei": [0, 1, 2]
            
            3. **Joint Relations Must Group All Related Items**: For parallel items, include ALL of them in a SINGLE "joint" relation
               CORRECT: One joint relation with all items - "nuclei": [1, 2, 3, 4, 5]
               INCORRECT: Chaining joint relations - r1(1,2) → r2(r1,3) → r3(r2,4)
            
            4. **Correct Relation Types**:
               - Use "cause-effect" for causal relationships, not "condition"
               - "Condition" is ONLY for hypothetical or unrealized situations (often signaled by "if")
               - Choose the most specific relation type that applies
            
            5. **Nucleus vs. Satellites**:
               - Multi-nuclear relations (joint, contrast) only have nuclei, no satellites
               - Nucleus-satellite relations must clearly identify which elements are central (nuclei) vs. supporting (satellites)
               - In "cause-effect" relations, the EFFECT is typically the nucleus and the CAUSE is the satellite
               - CRITICAL: Do not default to making everything a nucleus
            
            6. **Consistent Reference Format**:
               - Use integers for EDU references (e.g., 1, 2, 3)
               - Use strings with "r" prefix for relation references (e.g., "r1", "r2")
               - Never mix formats inconsistently (e.g., don't use 3 and "3" interchangeably)
            
            7. **Root Relation**: Every hypergraph MUST have a single top-level relation that encompasses the entire text
               - The root relation should be the highest-level rhetorical move that organizes the discourse
               - All other relations should connect directly or indirectly to this root
               - There should be no "orphaned" or disconnected parts of the hypergraph
            
            8. **Include Natural Language Descriptions**: 
               - Each relation should include a "description" field with a natural language explanation
               - Describe HOW the elements are related and WHY the relation is classified as that type
               - Be specific about which element is nucleus/satellite and why (for non-symmetric relations)
               
            9. **Avoid Redundant Relations**:
               - Direct connections are better than unnecessary intermediate relations
               - Don't create chains of the same relation type (e.g., elaboration → elaboration)
               - CORRECT: One elaboration relation connecting a nucleus to multiple satellites
               - INCORRECT: Chain of elaborations where each elaborates on the previous one
               
            10. **Prefer Flatter Structures**:
                - Minimize unnecessary nesting of relations
                - Aim for a hierarchical depth of no more than 3-4 levels when possible
                - Group related items at the same level rather than creating deep chains

            # Example Analysis 1:
            Text: "Your work is going to fill a large part of your life, and the only way to be truly satisfied is to do what you believe is great work. And the only way to do great work is to love what you do. If you haven't found it yet, keep looking. Don't settle. As with all matters of the heart, you'll know when you find it."
            
            EDUs:
            1. "Your work is going to fill a large part of your life"
            2. "and the only way to be truly satisfied is to do what you believe is great work"
            3. "And the only way to do great work is to love what you do"
            4. "If you haven't found it yet"
            5. "keep looking"
            6. "Don't settle"
            7. "As with all matters of the heart, you'll know when you find it"
            
            Correct Relations:
            ```json
            [
              {{
                "type": "joint",
                "nuclei": [1, 2],
                "satellites": [],
                "id": "r1",
                "description": "These first two EDUs present related facts about work - its importance and how to be satisfied with it."
              }},
              {{
                "type": "elaboration",
                "nuclei": ["r1"],
                "satellites": [3],
                "id": "r2",
                "description": "EDU 3 elaborates on the concept of 'great work' mentioned in relation r1, explaining how to achieve it."
              }},
              {{
                "type": "condition",
                "nuclei": [5],
                "satellites": [4],
                "id": "r3",
                "description": "EDU 4 presents a condition ('If you haven't found it yet') for the advice in EDU 5 ('keep looking')."
              }},
              {{
                "type": "joint",
                "nuclei": [5, 6],
                "satellites": [],
                "id": "r4",
                "description": "EDUs 5 and 6 present parallel pieces of advice of equal importance."
              }},
              {{
                "type": "evidence",
                "nuclei": ["r4"],
                "satellites": [7],
                "id": "r5",
                "description": "EDU 7 provides supporting evidence for the advice in relation r4, comparing the situation to matters of the heart."
              }},
              {{
                "type": "elaboration",
                "nuclei": ["r2"],
                "satellites": ["r5"],
                "id": "r6",
                "description": "Relation r5 (the advice and evidence) elaborates on the main point established in r2 about loving your work."
              }}
            ]
            ```

            # Example Analysis 2:
            Text: "I was excited to try this new sushi restaurant, but the excitement quickly faded. The lighting was too dim, the service was slow, and the fish didn't taste fresh. Because of all these issues, I won't be coming back."
            
            EDUs:
            1. "I was excited to try this new sushi restaurant"
            2. "but the excitement quickly faded"
            3. "The lighting was too dim"
            4. "the service was slow"
            5. "and the fish didn't taste fresh"
            6. "Because of all these issues"
            7. "I won't be coming back"
            
            CORRECT Relations (Direct Structure):
            ```json
            [
              {{
                "type": "contrast",
                "nuclei": [1, 2],
                "satellites": [],
                "id": "r1",
                "description": "EDUs 1 and 2 present contrasting attitudes toward the restaurant - initial excitement versus subsequent disappointment."
              }},
              {{
                "type": "joint",
                "nuclei": [3, 4, 5],
                "satellites": [],
                "id": "r2",
                "description": "These three complaints about the restaurant (lighting, service, and food quality) are presented as parallel issues of equal importance."
              }},
              {{
                "type": "elaboration",
                "nuclei": [2],
                "satellites": ["r2"],
                "id": "r3",
                "description": "The specific complaints in relation r2 elaborate on why 'the excitement quickly faded' from EDU 2, providing detailed reasons."
              }},
              {{
                "type": "cause-effect",
                "nuclei": [7],
                "satellites": [6],
                "id": "r4",
                "description": "EDU 7 ('I won't be coming back') is the effect or result, while EDU 6 ('Because of all these issues') is the cause or reason. The decision not to return is the main point."
              }},
              {{
                "type": "result",
                "nuclei": ["r3"],
                "satellites": ["r4"],
                "id": "r5",
                "description": "The decision not to return (r4) is a direct result of the negative experience detailed in r3. This relation connects the issues with their outcome."
              }}
            ]
            ```
            
            INCORRECT Relations (Redundant Structure):
            ```json
            [
              {{
                "type": "contrast",
                "nuclei": [1, 2],
                "satellites": [],
                "id": "r1",
                "description": "EDUs 1 and 2 present contrasting attitudes toward the restaurant."
              }},
              {{
                "type": "joint",
                "nuclei": [3, 4, 5],
                "satellites": [],
                "id": "r2",
                "description": "These three complaints are of equal importance."
              }},
              {{
                "type": "elaboration",
                "nuclei": [2],
                "satellites": ["r2"],
                "id": "r3",
                "description": "The complaints elaborate on why the excitement faded."
              }},
              {{
                "type": "elaboration",
                "nuclei": ["r3"],
                "satellites": ["r4"],
                "id": "r5",
                "description": "This further elaborates on the experience."
              }},
              {{
                "type": "cause-effect",
                "nuclei": [7],
                "satellites": [6],
                "id": "r4",
                "description": "The issues caused the decision not to return."
              }}
            ]
            ```
            
            # Common Errors to Avoid:
            
            1. **INCORRECT: Bad EDU Segmentation**
            Text: "Because of all these issues, I won't be coming back."
            
            INCORRECT (keeping as one EDU):
            ```json
            "edus": ["Because of all these issues, I won't be coming back."]
            ```
            
            CORRECT (split into cause and effect):
            ```json
            "edus": ["Because of all these issues", "I won't be coming back"]
            ```
            
            2. **INCORRECT: Chaining Joint Relations**
            INCORRECT (sequential chaining):
            ```json
            [
              {{
                "type": "joint",
                "nuclei": [1, 2],
                "satellites": [],
                "id": "r1",
                "description": "These two complaints are of equal importance."
              }},
              {{
                "type": "joint",
                "nuclei": ["r1", 3],
                "satellites": [],
                "id": "r2",
                "description": "This complaint is joined with the previous complaints."
              }}
            ]
            ```
            
            CORRECT (single joint relation):
            ```json
            [
              {{
                "type": "joint",
                "nuclei": [1, 2, 3],
                "satellites": [],
                "id": "r1",
                "description": "These three complaints are presented as parallel issues of equal importance."
              }}
            ]
            ```
            
            3. **INCORRECT: Redundant Relation Chains**
            INCORRECT (chaining elaborations):
            ```json
            [
              {{
                "type": "elaboration",
                "nuclei": [1],
                "satellites": [2],
                "id": "r1",
                "description": "EDU 2 elaborates on EDU 1."
              }},
              {{
                "type": "elaboration",
                "nuclei": ["r1"],
                "satellites": [3],
                "id": "r2",
                "description": "EDU 3 further elaborates on the previous elaboration."
              }}
            ]
            ```
            
            CORRECT (direct connections):
            ```json
            [
              {{
                "type": "elaboration",
                "nuclei": [1],
                "satellites": [2, 3],
                "id": "r1",
                "description": "EDUs 2 and 3 both elaborate on different aspects of EDU 1."
              }}
            ]
            ```
            
            4. **INCORRECT: Incorrect Connection of Cause-Effect**
            INCORRECT (cause-effect as elaboration satellite):
            ```json
            [
              {{
                "type": "elaboration",
                "nuclei": [1],
                "satellites": ["r2"],
                "id": "r1",
                "description": "The cause-effect elaborates on the main point."
              }},
              {{
                "type": "cause-effect",
                "nuclei": [3],
                "satellites": [2],
                "id": "r2",
                "description": "The cause leads to the effect."
              }}
            ]
            ```
            
            CORRECT (using result relation):
            ```json
            [
              {{
                "type": "result",
                "nuclei": [1],
                "satellites": ["r2"],
                "id": "r1",
                "description": "The cause-effect is a direct result of the main point."
              }},
              {{
                "type": "cause-effect",
                "nuclei": [3],
                "satellites": [2],
                "id": "r2",
                "description": "The cause leads to the effect."
              }}
            ]
            ```

            # Instructions:
            For the following text:
            {text}
            
            1. Break the text into Elementary Discourse Units (EDUs)
            2. Identify discourse relations between EDUs or groups of EDUs
            3. Create a hypergraph representation with correct relation types
            4. Ensure a single root relation encompasses the entire text
            5. Use proper 1-based indexing for EDUs
            6. Group all parallel items in a single joint relation, not chained joints
            7. Split causes and effects into separate EDUs, even within the same sentence
            8. Include natural language descriptions for each relation
            9. Avoid redundant relation chains - prefer direct connections
            10. Choose the most appropriate relation type for each connection
            
            Format your response as a JSON object with these components:
            1. "edus": Array of identified EDUs in the text
            2. "relations": Array of discourse relations where each relation has:
               - "type": The type of relation (e.g., "elaboration", "cause-effect", "joint", etc.)
               - "nuclei": Array of IDs of nuclei (EDU indices or relation IDs)
               - "satellites": Array of IDs of satellites (EDU indices or relation IDs, empty for multi-nuclear relations)
               - "id": A unique identifier for the relation (e.g., "r1", "r2", etc.)
               - "description": A natural language explanation of how the elements are related
            
            Output ONLY valid JSON without any additional explanation or text.
            """
        )
        
        self.chain = self.prompt | self.llm | StrOutputParser()
        
    def validate_hypergraph(self, data):
        """Validate and fix hypergraph structure.
        
        Args:
            data: The hypergraph data as a dictionary
        
        Returns:
            Tuple containing:
            - Validation result dictionary
            - Fixed hypergraph
        """
        # Deep copy to avoid modifying the original
        fixed_data = copy.deepcopy(data)
        
        validation_result = {
            "is_valid": True,
            "issues": [],
            "modified": False
        }
        
        # Check if required keys exist
        required_keys = ["edus", "relations"]
        for key in required_keys:
            if key not in data:
                validation_result["is_valid"] = False
                validation_result["issues"].append(f"Missing required key: {key}")
                return validation_result, fixed_data
        
        # Fix and check relation references for quotes and format
        fixed_data = self._fix_relation_references(fixed_data, validation_result)
        
        # Check for disconnected components and fix them
        fixed_data = self._fix_disconnected_components(fixed_data, validation_result)
        
        # Check for redundant relations and simplify them
        fixed_data = self._simplify_redundant_relations(fixed_data, validation_result)
        
        # Ensure a single root relation
        fixed_data = self._ensure_root_relation(fixed_data, validation_result)
        
        return validation_result, fixed_data

    def _fix_relation_references(self, data, validation_result):
        """Fix relation ID references by removing extra quotes."""
        has_quote_issue = False
        
        # Check and fix relation references
        for relation in data["relations"]:
            # Fix nuclei references
            for i, nucleus in enumerate(relation.get("nuclei", [])):
                if isinstance(nucleus, str) and (nucleus.startswith("'") or nucleus.startswith('"')):
                    # Strip quotes from relation references
                    clean_nucleus = nucleus.strip("'\"")
                    relation["nuclei"][i] = clean_nucleus
                    has_quote_issue = True
            
            # Fix satellite references
            for i, satellite in enumerate(relation.get("satellites", [])):
                if isinstance(satellite, str) and (satellite.startswith("'") or satellite.startswith('"')):
                    # Strip quotes from relation references
                    clean_satellite = satellite.strip("'\"")
                    relation["satellites"][i] = clean_satellite
                    has_quote_issue = True
        
        if has_quote_issue:
            validation_result["modified"] = True
            validation_result["issues"].append("Fixed relation references with extra quotes")
        
        return data

    def _fix_disconnected_components(self, data, validation_result):
        """Identify and fix disconnected components in the hypergraph."""
        # Create a graph to detect disconnected components
        G = nx.Graph()
        
        # Add all EDUs and relations as nodes
        for i in range(1, len(data["edus"]) + 1):
            G.add_node(i)
        
        for relation in data["relations"]:
            G.add_node(relation["id"])
        
        # Add edges for relations
        for relation in data["relations"]:
            for nucleus in relation.get("nuclei", []):
                if isinstance(nucleus, str):
                    G.add_edge(relation["id"], nucleus)
                else:
                    G.add_edge(relation["id"], nucleus)
            
            for satellite in relation.get("satellites", []):
                if isinstance(satellite, str):
                    G.add_edge(relation["id"], satellite)
                else:
                    G.add_edge(relation["id"], satellite)
        
        # Check for disconnected components
        components = list(nx.connected_components(G))
        
        if len(components) > 1:
            validation_result["is_valid"] = False
            validation_result["modified"] = True
            validation_result["issues"].append(f"Found {len(components)} disconnected components in the hypergraph")
            
            # Create a new root relation to connect all components
            component_roots = []
            for component in components:
                # Find possible root in this component
                component_relations = [node for node in component if isinstance(node, str) and node.startswith("r")]
                if component_relations:
                    # Find relation that's not referenced by any other relation
                    referenced_relations = set()
                    for rel_id in component_relations:
                        rel = next((r for r in data["relations"] if r["id"] == rel_id), None)
                        if rel:
                            for n in rel.get("nuclei", []):
                                if isinstance(n, str) and n.startswith("r"):
                                    referenced_relations.add(n)
                            for s in rel.get("satellites", []):
                                if isinstance(s, str) and s.startswith("r"):
                                    referenced_relations.add(s)
                
                    component_root = next((r for r in component_relations if r not in referenced_relations), None)
                    if component_root:
                        component_roots.append(component_root)
            
            if len(component_roots) > 1:
                # Create a new joint relation to connect multiple roots
                new_id = f"r{len(data['relations']) + 1}"
                data["relations"].append({
                    "type": "joint",
                    "nuclei": component_roots,
                    "satellites": [],
                    "id": new_id,
                    "description": "Root relation connecting separate discourse components."
                })
                validation_result["issues"].append(f"Created new root relation {new_id} to connect disconnected components")
        
        return data

    def _simplify_redundant_relations(self, data, validation_result):
        """Simplify redundant relation chains (e.g., elaboration → elaboration)."""
        # Check for chains of the same relation type
        relation_map = {r["id"]: r for r in data["relations"]}
        modified = False
        
        # Look for chains of the same relation type
        for relation in data["relations"]:
            rel_type = relation["type"]
            for i, satellite in enumerate(relation.get("satellites", [])):
                if isinstance(satellite, str) and satellite in relation_map:
                    satellite_rel = relation_map[satellite]
                    if satellite_rel["type"] == rel_type:
                        # Found a chain of the same relation type
                        # Move all nuclei and satellites from the satellite relation to this relation
                        for nucleus in satellite_rel.get("nuclei", []):
                            if nucleus not in relation["nuclei"]:
                                relation["nuclei"].append(nucleus)
                        
                        for sat in satellite_rel.get("satellites", []):
                            if sat not in relation["satellites"]:
                                relation["satellites"].append(sat)
                        
                        # Remove the satellite relation reference
                        relation["satellites"][i] = None
                        modified = True
        
        # Remove None values from satellites
        if modified:
            for relation in data["relations"]:
                relation["satellites"] = [s for s in relation.get("satellites", []) if s is not None]
            
            # Remove relations that are now redundant
            used_relations = set()
            for relation in data["relations"]:
                for nucleus in relation.get("nuclei", []):
                    if isinstance(nucleus, str):
                        used_relations.add(nucleus)
                for satellite in relation.get("satellites", []):
                    if isinstance(satellite, str):
                        used_relations.add(satellite)
            
            data["relations"] = [r for r in data["relations"] if r["id"] in used_relations or any(
                (isinstance(n, str) and n.startswith("r")) for n in r.get("nuclei", []) + r.get("satellites", [])
            )]
            
            validation_result["modified"] = True
            validation_result["issues"].append("Simplified redundant relation chains")
        
        return data

    def _ensure_root_relation(self, data, validation_result):
        """Ensure there is a single root relation in the hypergraph."""
        # Find all relations that are referenced by other relations
        referenced_relations = set()
        for relation in data["relations"]:
            for nucleus in relation.get("nuclei", []):
                if isinstance(nucleus, str) and nucleus.startswith("r"):
                    referenced_relations.add(nucleus)
            for satellite in relation.get("satellites", []):
                if isinstance(satellite, str) and satellite.startswith("r"):
                    referenced_relations.add(satellite)
        
        # Find relations that aren't referenced by any other relation
        all_relation_ids = {r["id"] for r in data["relations"]}
        root_candidates = all_relation_ids - referenced_relations
        
        if len(root_candidates) == 0:
            validation_result["is_valid"] = False
            validation_result["issues"].append("No root relation found - circular reference")
            return data
        
        if len(root_candidates) == 1:
            # Already has one root, which is correct
            return data
        
        # Multiple roots found, need to create a new root relation
        validation_result["is_valid"] = False
        validation_result["modified"] = True
        validation_result["issues"].append(f"Multiple root relations found: {root_candidates}. Creating a new root.")
        
        # Create a new root relation
        new_id = f"r{len(data['relations']) + 1}"
        data["relations"].append({
            "type": "joint",
            "nuclei": list(root_candidates),
            "satellites": [],
            "id": new_id,
            "description": "Root relation connecting multiple discourse components."
        })
        
        return data

    def visualize_hypergraph(self, G, edus, relations, figsize=(12, 8)):
        """Visualize the hypergraph representation."""
        plt.figure(figsize=figsize)
        
        # Create a layout for the graph
        pos = nx.spring_layout(G, seed=42)
        
        # Identify the root relation
        root_relations = []
        relation_ids = {r["id"] for r in relations}
        referenced_relations = set()
        for relation in relations:
            for rel_id in [n for n in relation.get("nuclei", []) if isinstance(n, str)]:
                referenced_relations.add(rel_id)
            for rel_id in [s for s in relation.get("satellites", []) if isinstance(s, str)]:
                referenced_relations.add(rel_id)
        root_relations = list(relation_ids - referenced_relations)
        
        # Draw EDU nodes
        edu_nodes = [n for n, attr in G.nodes(data=True) if attr.get('type') == 'edu']
        nx.draw_networkx_nodes(G, pos, nodelist=edu_nodes, node_color='skyblue', 
                              node_size=1000, node_shape='o')
        
        # Draw relation nodes (hyperedges)
        relation_nodes = [n for n, attr in G.nodes(data=True) if attr.get('type') == 'relation']
        
        # Highlight root relation with a different color
        non_root_relations = [n for n in relation_nodes if n not in root_relations]
        root_relation_nodes = [n for n in relation_nodes if n in root_relations]
        
        nx.draw_networkx_nodes(G, pos, nodelist=non_root_relations, node_color='lightgreen',
                              node_size=700, node_shape='h')
        
        if root_relation_nodes:
            nx.draw_networkx_nodes(G, pos, nodelist=root_relation_nodes, node_color='gold',
                                  node_size=900, node_shape='h', linewidths=2, edgecolors='red')
        
        # Draw edges
        nucleus_edges = [(u, v) for u, v, attr in G.edges(data=True) if attr.get('role') == 'nucleus']
        satellite_edges = [(u, v) for u, v, attr in G.edges(data=True) if attr.get('role') == 'satellite']
        
        nx.draw_networkx_edges(G, pos, edgelist=nucleus_edges, edge_color='blue', width=2)
        nx.draw_networkx_edges(G, pos, edgelist=satellite_edges, edge_color='red', width=1.5, style='dashed')
        
        # Add relation labels
        relation_labels = {node: G.nodes[node]['label'] for node in relation_nodes}
        nx.draw_networkx_labels(G, pos, labels=relation_labels, font_size=10)
        
        # Add EDU labels
        edu_labels = {node: f"EDU {node}\n{edus[node-1][:30]}..." if len(edus[node-1]) > 30 else f"EDU {node}\n{edus[node-1]}" 
                     for node in edu_nodes}
        nx.draw_networkx_labels(G, pos, labels=edu_labels, font_size=8)
        
        # Add a legend
        plt.legend([plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='skyblue', markersize=10),
                   plt.Line2D([0], [0], marker='h', color='w', markerfacecolor='lightgreen', markersize=10),
                   plt.Line2D([0], [0], marker='h', color='w', markerfacecolor='gold', markersize=10, markeredgecolor='red'),
                   plt.Line2D([0], [0], color='blue', lw=2),
                   plt.Line2D([0], [0], color='red', lw=1.5, linestyle='--')],
                  ['EDU', 'Relation', 'Root Relation', 'Nucleus Edge', 'Satellite Edge'],
                  loc='best')
        
        plt.title('RST Hypergraph Representation')
        plt.axis('off')
        plt.tight_layout()
        plt.show()
        
    def generate_hypergraph(self, text: str) -> Tuple[nx.Graph, List[str], Dict, Dict]:
        """Generate a rhetorical hypergraph from text.
        
        Args:
            text: The input text to analyze
            
        Returns:
            A tuple containing:
            - The graph representation (networkx graph)
            - List of EDUs
            - Dictionary of relations
            - Full JSON result
        """
        # Process the text with the LLM
        response = self.chain.invoke({"text": text})
        
        # Extract JSON from the response
        json_pattern = r"```json\n(.*?)\n```"
        json_match = re.search(json_pattern, response, re.DOTALL)
        
        if json_match:
            json_str = json_match.group(1)
        else:
            # If no JSON block found, try to parse the entire response
            json_str = response
        
        try:
            result = json.loads(json_str)
        except json.JSONDecodeError:
            # Handle the case where the response isn't valid JSON
            # Try to find and fix common formatting issues
            cleaned_json = re.sub(r',\s*}', '}', json_str)
            cleaned_json = re.sub(r',\s*]', ']', cleaned_json)
            try:
                result = json.loads(cleaned_json)
            except json.JSONDecodeError:
                print("Failed to parse LLM response as JSON. Raw response:")
                print(response)
                raise
        
        # Validate and fix the hypergraph structure
        validation_result, fixed_result = self.validate_hypergraph(result)
        if not validation_result["is_valid"]:
            print("Validation issues found:")
            for issue in validation_result["issues"]:
                print(f"- {issue}")
            if validation_result["modified"]:
                print("Issues automatically fixed.")
                result = fixed_result
        
        # Create a NetworkX graph for visualization
        G = nx.Graph()
        
        # Add EDU nodes
        edus = result.get("edus", [])
        for i, edu in enumerate(edus, 1):
            G.add_node(i, type="edu", label=edu, shape="rectangle")
        
        # Add relation nodes and edges
        relations = result.get("relations", [])
        for relation in relations:
            relation_id = relation.get("id")
            relation_type = relation.get("type")
            nuclei = relation.get("nuclei", [])
            satellites = relation.get("satellites", [])
            
            # Add the relation node (hyperedge)
            G.add_node(relation_id, type="relation", label=relation_type, shape="star")
            
            # Connect the relation node to its nuclei and satellites
            for nucleus in nuclei:
                G.add_edge(relation_id, nucleus, role="nucleus")
            
            for satellite in satellites:
                G.add_edge(relation_id, satellite, role="satellite")
        
        return G, edus, relations, result
    
    def save_to_json(self, data: Dict, filename: str = "sonnet_37.json"):
        """Save the RST hypergraph data to a JSON file.
        
        Args:
            data: The hypergraph data to save
            filename: Path to the output JSON file
        """
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"RST hypergraph saved to {filename}")

# Demo usage
def main():
    # Replace with your OpenAI API key
    openai_api_key = "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"
    
    rst_generator = RSTHypergraphGenerator(openai_api_key)
    
    # Example text
    text = """I was excited to try this new sushi restaurant, but the excitement quickly faded. The lighting was too dim, the service was slow, and the fish didn't taste fresh. Because of all these issues, I won't be coming back."""
    
    # Generate hypergraph
    G, edus, relations, json_data = rst_generator.generate_hypergraph(text)
    
    # Save the JSON data to a file
    rst_generator.save_to_json(json_data)
    
    # Visualize
    rst_generator.visualize_hypergraph(G, edus, relations)
    
    print("EDUs:")
    for i, edu in enumerate(edus, 1):
        print(f"{i}. {edu}")
    
    print("\nRelations:")
    for relation in relations:
        print(f"ID: {relation['id']}, Type: {relation['type']}")
        print(f"  Nuclei: {relation['nuclei']}")
        print(f"  Satellites: {relation['satellites']}")

if __name__ == "__main__":
    main()