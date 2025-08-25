import uuid
import numpy as np
import os
from typing import List, Dict, Set, Tuple, Optional, Any, Union

# LangChain imports
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

class Hyperedge:
    def __init__(self, id=None, content=None, edge_type=None, domain_type=None, components=None, roles=None):
        """
        Initialize a hyperedge in the hybrid system.
        
        Args:
            id (str): Unique identifier for the hyperedge
            content (str): Text content if this is an atomic hyperedge
            edge_type (str): One of the 8 SH types: 'C', 'P', 'M', 'B', 'T', 'J', 'R', 'S'
            domain_type (str): Optional domain-specific type (e.g., 'PoliticalActor', 'Claim')
            components (list): List of Hyperedge objects for non-atomic edges
            roles (list): List of role strings corresponding to components
        """
        self.id = id or str(uuid.uuid4())
        self.content = content
        self.edge_type = edge_type 
        self.domain_type = domain_type
        self.components = components or []
        self.roles = roles or []
        
    @property
    def is_atomic(self):
        """Return True if this is an atomic hyperedge (has no components)."""
        return len(self.components) == 0
        
    def to_string(self):
        """Convert the hyperedge to its string representation."""
        if self.is_atomic:
            base = f"{self.content}/{self.edge_type}"
            return f"{base}:{self.domain_type}" if self.domain_type else base
        
        components_str = " ".join([comp.to_string() for comp in self.components])
        return f"({components_str})"


class HypergraphStore:
    def __init__(self):
        """Initialize the hypergraph store with indices for both SH and OG-RAG approaches."""
        # SH-style structural storage
        self.edges_by_id = {}
        self.edge_hash_to_id = {}
        
        # OG-RAG style semantic indices
        self.nodes = {}  # Hypernode storage
        self.node_to_edges = {}  # Maps nodes to containing edges
        self.node_embeddings = {}  # Store embeddings for nodes
        
        # Indices for each system
        self.sh_indices = {
            'type': {},      # SH type -> set of edge IDs
            'content': {},   # Content -> set of edge IDs (for atomic edges)
            'component': {}  # Component ID -> set of edge IDs containing it
        }
        self.og_indices = {
            'domain_type': {},  # Domain type -> set of edge IDs
            'role': {}          # Role -> set of edge IDs using that role
        }
        
    def add_hyperedge(self, edge):
        """
        Add a hyperedge to the store with all its components.
        
        Args:
            edge (Hyperedge): The edge to add
            
        Returns:
            str: The ID of the added edge
        """
        # Check if this exact edge already exists (via hash)
        edge_hash = hash(edge.to_string())
        if edge_hash in self.edge_hash_to_id:
            return self.edge_hash_to_id[edge_hash]
        
        # Store the edge
        self.edges_by_id[edge.id] = edge
        self.edge_hash_to_id[edge_hash] = edge.id
        
        # Update indices
        # Index by type
        if edge.edge_type:
            if edge.edge_type not in self.sh_indices['type']:
                self.sh_indices['type'][edge.edge_type] = set()
            self.sh_indices['type'][edge.edge_type].add(edge.id)
        
        # Index by domain type
        if edge.domain_type:
            if edge.domain_type not in self.og_indices['domain_type']:
                self.og_indices['domain_type'][edge.domain_type] = set()
            self.og_indices['domain_type'][edge.domain_type].add(edge.id)
        
        # Index atomic edge by content
        if edge.is_atomic and edge.content:
            if edge.content not in self.sh_indices['content']:
                self.sh_indices['content'][edge.content] = set()
            self.sh_indices['content'][edge.content].add(edge.id)
        
        # For complex edges, add component references and process components recursively
        for i, component in enumerate(edge.components):
            # Add the component
            component_id = self.add_hyperedge(component)
            
            # Index the relationship
            if component_id not in self.sh_indices['component']:
                self.sh_indices['component'][component_id] = set()
            self.sh_indices['component'][component_id].add(edge.id)
            
            # Index by role if applicable
            if i < len(edge.roles) and edge.roles[i]:
                role = edge.roles[i]
                if role not in self.og_indices['role']:
                    self.og_indices['role'][role] = set()
                self.og_indices['role'][role].add(edge.id)
        
        return edge.id


def cosine_similarity(vec1, vec2):
    """Calculate cosine similarity between two vectors."""
    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    magnitude1 = sum(x * x for x in vec1) ** 0.5
    magnitude2 = sum(x * x for x in vec2) ** 0.5
    
    if magnitude1 == 0 or magnitude2 == 0:
        return 0
    
    return dot_product / (magnitude1 * magnitude2)


def parse_hypergraph_string(hypergraph_str):
    """
    Parse a string representation of a hypergraph into a Hyperedge object.
    
    Args:
        hypergraph_str (str): The string to parse
        
    Returns:
        Hyperedge: The parsed hyperedge
    """
    # Remove whitespace
    hypergraph_str = hypergraph_str.strip()
    
    # Check if this is a complex edge (enclosed in parentheses)
    if hypergraph_str.startswith('(') and hypergraph_str.endswith(')'):
        # Remove outer parentheses and parse inner content
        inner_content = hypergraph_str[1:-1].strip()
        
        # Parse components with proper handling of nested parentheses
        components = []
        roles = []
        
        i = 0
        current_component = ""
        paren_depth = 0
        
        while i < len(inner_content):
            char = inner_content[i]
            
            if char == '(' and (i == 0 or inner_content[i-1] != '\\'):
                paren_depth += 1
                current_component += char
            elif char == ')' and (i == 0 or inner_content[i-1] != '\\'):
                paren_depth -= 1
                current_component += char
            elif char == ' ' and paren_depth == 0:
                # End of a component
                if current_component:
                    component_edge = parse_hypergraph_string(current_component)
                    
                    # Extract role if present
                    role = ""
                    if component_edge.content and '.' in component_edge.content and component_edge.is_atomic:
                        parts = component_edge.content.split('.')
                        if len(parts) > 1:
                            component_edge.content = parts[0]
                            role = parts[1]
                    
                    components.append(component_edge)
                    roles.append(role)
                    current_component = ""
            else:
                current_component += char
                
            i += 1
            
        # Add final component if exists
        if current_component:
            component_edge = parse_hypergraph_string(current_component)
            
            # Extract role if present
            role = ""
            if component_edge.content and '.' in component_edge.content and component_edge.is_atomic:
                parts = component_edge.content.split('.')
                if len(parts) > 1:
                    component_edge.content = parts[0]
                    role = parts[1]
            
            components.append(component_edge)
            roles.append(role)
        
        return Hyperedge(components=components, roles=roles)
    else:
        # This is an atomic edge
        # Check for domain type
        domain_type = None
        content_type = hypergraph_str
        
        if ':' in hypergraph_str:
            parts = hypergraph_str.split(':')
            content_type = parts[0]
            domain_type = parts[1]
        
        # Split content and type
        if '/' in content_type:
            parts = content_type.split('/')
            content = parts[0]
            edge_type = parts[1]
        else:
            content = content_type
            edge_type = 'C'  # Default to concept
            
        return Hyperedge(content=content, edge_type=edge_type, domain_type=domain_type)


def extract_hypergraph_from_response(response):
    """Extract hypergraph string from LLM response."""
    # Look for parentheses-wrapped content
    response = response.strip()
    
    # If the response is already a valid hypergraph string, return it
    if response.startswith('(') and response.endswith(')'):
        return response
    
    # Search for parentheses-wrapped content in the response
    start_idx = response.find('(')
    if start_idx == -1:
        return response  # No parentheses found
    
    paren_count = 0
    for i in range(start_idx, len(response)):
        if response[i] == '(':
            paren_count += 1
        elif response[i] == ')':
            paren_count -= 1
            if paren_count == 0:
                return response[start_idx:i+1]
    
    # If we reached here, matching parentheses weren't found
    return response


class EmbeddingModel:
    def __init__(self, api_key=None):
        """Initialize with OpenAI embeddings from LangChain."""
        # If no API key provided, it will try to use OPENAI_API_KEY environment variable
        self.embeddings = OpenAIEmbeddings(openai_api_key="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")
        
    def embed(self, text):
        """Embed text using OpenAI embeddings."""
        return self.embeddings.embed_query(text)


class LLMClient:
    def __init__(self, api_key=None, model_name="gpt-4o-mini"): #gpt-4o-mini is a recent model, do not change
        """Initialize with OpenAI chat model from LangChain."""
        # If no API key provided, it will try to use OPENAI_API_KEY environment variable
        self.chat_model = ChatOpenAI(
            openai_api_key=api_key,
            model_name=model_name,
            temperature=0.2
        )
        
    def generate(self, system=None, user=None, max_tokens=1000):
        """Generate text using OpenAI chat model."""
        messages = []
        if system:
            messages.append(SystemMessage(content=system))
        if user:
            messages.append(HumanMessage(content=user))
        
        response = self.chat_model.invoke(messages)
        return response.content


class PlaceholderEmbeddingModel:
    """Placeholder embedding model that doesn't require API access."""
    
    def __init__(self):
        """Initialize the placeholder embedding model."""
        pass
    
    def embed(self, text):
        """Generate a simple embedding based on keywords in the text."""
        # Very simple embedding: count occurrences of key terms
        text = text.lower()
        
        # Key terms related to climate change discourse
        key_terms = ["biden", "climate", "change", "threat", "security", "elon", "musk", 
                    "electric", "vehicles", "carbon", "emissions", "scientists", 
                    "temperature", "global", "warming", "renewable", "energy"]
        
        # Count occurrences of key terms
        counts = [text.count(term) for term in key_terms]
        
        # Normalize to create a unit vector
        magnitude = sum(x*x for x in counts) ** 0.5
        if magnitude == 0:
            return [0] * len(key_terms)
        
        embedding = [count / magnitude for count in counts]
        return embedding


class PlaceholderLLMClient:
    """Placeholder LLM client that doesn't require API access."""
    
    def __init__(self):
        """Initialize the placeholder LLM client."""
        pass
    
    def generate(self, system=None, user=None, max_tokens=1000):
        """Generate simple responses based on pattern matching."""
        if not user:
            return "No input provided."
        
        user_lower = user.lower()
        
        # For text to hypergraph conversion
        if "convert this text to a hybrid semantic hypergraph" in user_lower:
            text = user.split(":\n\n")[-1]
            
            if "biden" in text.lower() and "climate" in text.lower():
                return "(claims/P.sr biden/C:PoliticalActor (is/P.sc (+/B climate/C:Topic change/C:Topic) (threat/C (+/B.ma serious/M) (+/B.ma national/M security/C:Topic)))))"
            
            if "elon" in text.lower() and "electric" in text.lower():
                return "(argues/P.sr (+/B elon/C:PoliticalActor musk/C:PoliticalActor) (are/P.sc (+/B electric/M vehicles/C:Topic) (essential/C (for/B reducing/P (+/B carbon/C emissions/C:Topic)))))"
            
            if "scientists" in text.lower() and "climate" in text.lower():
                return "(report/P.so (+/B climate/C scientists/C:PoliticalActor) (rising/M (+/B global/M temperatures/C:Topic) (over/B (+/B past/M decade/C:Topic))))"
            
            # Default pattern for other texts
            return "(says/P.so subject/C:PoliticalActor (is/P.sc topic/C:Topic important/C:Sentiment))"
        
        # For RAG responses
        if "context" in user_lower and "question" in user_lower:
            if "biden" in user_lower and "climate" in user_lower:
                return "Based on the information provided, Biden claims that climate change is a serious threat to national security."
            
            if "elon" in user_lower and "electric" in user_lower:
                return "According to the information, Elon Musk argues that electric vehicles are essential for reducing carbon emissions."
            
            if "developing nations" in user_lower:
                return "The information suggests that leaders from developing nations often highlight the unfair dynamics of climate action, noting that industrialized countries built their wealth through carbon-intensive development."
            
            if "economic" in user_lower:
                return "The economic implications of climate change are complex. Some economists like Nicholas Stern argue that the costs of inaction outweigh the costs of reducing emissions, while others warn that aggressive climate policies could slow economic growth."
            
            if "public opinion" in user_lower:
                return "According to the information, public concern about climate change varies by country and demographic group, with younger generations generally expressing higher levels of concern than older populations."
            
            return "I don't have enough information in the provided context to answer that question."
        
        return "I'm a placeholder LLM that can't process this request properly."


def text_to_hypergraph(text, llm_client):
    """
    Convert natural language text to a hybrid semantic hypergraph.
    
    Args:
        text (str): The input text to convert
        llm_client: Client for accessing the LLM API
        
    Returns:
        Hyperedge: The root hyperedge representing the text
    """
    system_prompt = """
    Convert this text to a semantic hypergraph with both structural and domain types.
    
    STRUCTURAL TYPES:
    - C: Concept (nouns, objects)
    - P: Predicate (verbs, actions)
    - M: Modifier (adjectives, adverbs)
    - B: Builder (prepositions, compounds)
    - T: Trigger (specifications)
    - J: Conjunction (and, or, but)
    
    DOMAIN TYPES (add after structural type with colon):
    - PoliticalActor: Political figures or entities
    - SocialMediaUser: Users on social platforms
    - Claim: Assertions about something
    - Topic: Subjects of discussion
    - Sentiment: Emotional content
    
    EXAMPLES:
    "Biden claims climate change is serious" → 
    (claims/P.sr (+/B president/C:PoliticalActor biden/C:PoliticalActor) (is/P.sc (+/B climate/C:Topic change/C:Topic) serious/C:Sentiment))
    """
    
    user_prompt = f"Convert this text to a hybrid semantic hypergraph:\n\n{text}"
    
    response = llm_client.generate(
        system=system_prompt,
        user=user_prompt,
        max_tokens=1000
    )
    
    hypergraph_str = extract_hypergraph_from_response(response)
    return parse_hypergraph_string(hypergraph_str)


def flatten_hyperedge(edge):
    """
    Flatten a complex hyperedge into semantic hypernodes for efficient retrieval.
    This adapts OG-RAG's flattening algorithm.
    
    Args:
        edge (Hyperedge): The hyperedge to flatten
        
    Returns:
        list: List of hypernodes (key-value pairs)
    """
    if edge.is_atomic:
        return []
    
    hypernodes = []
    
    # Generate key-value pairs for direct relationships
    if len(edge.components) >= 2:
        connector = edge.components[0]
        
        for i in range(1, len(edge.components)):
            role = edge.roles[i] if i < len(edge.roles) else ""
            
            # Create a key combining the connector and role
            key = f"{connector.content}/{connector.edge_type}.{role}"
            
            # Get the value component
            value_comp = edge.components[i]
            value = value_comp.to_string()
            
            # Add the hypernode
            hypernodes.append((key, value))
            
            # Recursively flatten nested components
            if not value_comp.is_atomic:
                nested_hypernodes = flatten_hyperedge(value_comp)
                
                # Add the nested relationships with expanded keys
                for nested_key, nested_value in nested_hypernodes:
                    expanded_key = f"{key} {nested_key}"
                    hypernodes.append((expanded_key, nested_value))
    
    return hypernodes


def find_pattern_matches(store, pattern):
    """
    Find hyperedges that match a specific SH pattern.
    
    Args:
        store (HypergraphStore): The hypergraph store
        pattern (Hyperedge): The pattern to match
        
    Returns:
        list: List of matching hyperedges
    """
    matches = []
    candidates = _find_candidate_edges(store, pattern)
    
    for edge_id in candidates:
        edge = store.edges_by_id[edge_id]
        if _edge_matches_pattern(edge, pattern):
            matches.append(edge)
            
    return matches


def _find_candidate_edges(store, pattern):
    """Find candidate edges that might match the pattern."""
    # Start with all edges
    candidates = set(store.edges_by_id.keys())
    
    # Filter by edge type if specified
    if pattern.edge_type and pattern.edge_type in store.sh_indices['type']:
        candidates &= store.sh_indices['type'][pattern.edge_type]
    
    # Filter by domain type if specified
    if pattern.domain_type and pattern.domain_type in store.og_indices['domain_type']:
        candidates &= store.og_indices['domain_type'][pattern.domain_type]
    
    # Filter by content for atomic patterns
    if pattern.is_atomic and pattern.content and not pattern.content.isupper():
        if pattern.content in store.sh_indices['content']:
            candidates &= store.sh_indices['content'][pattern.content]
        else:
            # No matches if content doesn't exist and it's not a variable
            return set()
    
    return candidates


def _edge_matches_pattern(edge, pattern):
    """Check if an edge matches a pattern."""
    # Type check
    if pattern.edge_type and edge.edge_type != pattern.edge_type:
        return False
        
    # Domain type check (if specified)
    if pattern.domain_type and edge.domain_type != pattern.domain_type:
        return False
        
    # For atomic patterns
    if pattern.is_atomic:
        if edge.is_atomic:
            # Variables (uppercase) match anything of the right type
            if pattern.content and pattern.content.isupper():
                return True
            # Specific content must match exactly
            else:
                return pattern.content == edge.content
        return False
        
    # For complex patterns
    if len(pattern.components) > len(edge.components):
        return False
        
    # Check connector match
    if not _edge_matches_pattern(edge.components[0], pattern.components[0]):
        return False
        
    # Match remaining components
    for i in range(1, len(pattern.components)):
        if i >= len(edge.components):
            return False
        if not _edge_matches_pattern(edge.components[i], pattern.components[i]):
            return False
            
    return True


def retrieval_by_coverage(store, query, embedding_model, k=5, max_edges=3, debug=False):
    """
    Retrieve hyperedges using OG-RAG's node coverage algorithm.
    
    Args:
        store (HypergraphStore): The hypergraph store
        query (str): The query text
        embedding_model: Model to generate embeddings
        k (int): Number of top hypernode matches to consider
        max_edges (int): Maximum number of hyperedges to return
        debug (bool): Whether to print debug information
        
    Returns:
        list: List of hyperedges that maximally cover query-relevant nodes
    """
    if debug:
        print(f"Retrieving for query: '{query}'")
        print(f"Store contains {len(store.nodes)} nodes and {len(store.edges_by_id)} edges")
    
    query_embedding = embedding_model.embed(query)
    
    # Find relevant hypernodes (both keys and values)
    key_matches = []
    value_matches = []
    
    for node_id, node in store.nodes.items():
        key, value = node
        
        # Get or compute embeddings
        key_embedding_id = f"{node_id}_key"
        value_embedding_id = f"{node_id}_value"
        
        if key_embedding_id not in store.node_embeddings:
            store.node_embeddings[key_embedding_id] = embedding_model.embed(key)
        
        if value_embedding_id not in store.node_embeddings:
            store.node_embeddings[value_embedding_id] = embedding_model.embed(value)
            
        key_embedding = store.node_embeddings[key_embedding_id]
        value_embedding = store.node_embeddings[value_embedding_id]
        
        # Compute similarities
        key_similarity = cosine_similarity(query_embedding, key_embedding)
        value_similarity = cosine_similarity(query_embedding, value_embedding)
        
        # Add to appropriate lists with similarities
        key_matches.append((node_id, key_similarity))
        value_matches.append((node_id, value_similarity))
    
    # Get top-k matches from each
    key_matches = sorted(key_matches, key=lambda x: x[1], reverse=True)[:k]
    value_matches = sorted(value_matches, key=lambda x: x[1], reverse=True)[:k]
    
    if debug:
        print("Top key matches:")
        for node_id, sim in key_matches[:3]:  # Show top 3
            key, _ = store.nodes[node_id]
            print(f"  - {key} (similarity: {sim:.4f})")
    
    # Combine matches
    relevant_nodes = set([node_id for node_id, _ in key_matches + value_matches])
    
    # Greedy algorithm to find covering hyperedges
    selected_edges = []
    uncovered_nodes = relevant_nodes.copy()
    
    while uncovered_nodes and len(selected_edges) < max_edges:
        best_edge = None
        best_coverage = 0
        
        # Find edge with maximum coverage of uncovered nodes
        for edge_id, edge in store.edges_by_id.items():
            # Get hypernodes in this edge
            edge_nodes = set()
            edge_node_ids = store.node_to_edges.get(edge_id, set())
            for node_id in edge_node_ids:
                if node_id in uncovered_nodes:
                    edge_nodes.add(node_id)
            
            coverage = len(edge_nodes)
            if coverage > best_coverage:
                best_coverage = coverage
                best_edge = edge_id
        
        if best_edge and best_coverage > 0:
            selected_edges.append(store.edges_by_id[best_edge])
            if debug:
                print(f"Selected edge {best_edge} covering {best_coverage} nodes")
            # Remove covered nodes
            for node_id in store.node_to_edges.get(best_edge, []):
                if node_id in uncovered_nodes:
                    uncovered_nodes.remove(node_id)
        else:
            break
    
    if debug:
        print(f"Retrieved {len(selected_edges)} edges")
    return selected_edges


def hybrid_retrieval(store, query, embedding_model, pattern=None, debug=False):
    """
    Perform hybrid retrieval combining pattern matching and node coverage.
    
    Args:
        store (HypergraphStore): The hypergraph store
        query (str): The query text
        embedding_model: Model to generate embeddings
        pattern (Hyperedge, optional): Optional SH pattern to filter results
        debug (bool): Whether to print debug information
        
    Returns:
        list: List of relevant hyperedges
    """
    # First, get semantically relevant edges via node coverage
    semantic_matches = retrieval_by_coverage(store, query, embedding_model, debug=debug)
    
    if debug and pattern:
        print(f"Filtering with pattern: {pattern.to_string()}")
    
    # If a pattern is provided, filter semantic matches by pattern
    if pattern:
        pattern_matches = find_pattern_matches(store, pattern)
        
        if debug:
            print(f"Found {len(pattern_matches)} edges matching pattern")
            
        filtered_matches = [edge for edge in semantic_matches if edge.id in [m.id for m in pattern_matches]]
        
        if debug:
            print(f"After filtering, {len(filtered_matches)} edges remain")
            
        return filtered_matches
    
    return semantic_matches


def add_text_to_store(text, store, llm_client, embedding_model):
    """
    Process text and add it to the hypergraph store.
    
    Args:
        text (str): The text to process
        store (HypergraphStore): The hypergraph store
        llm_client: Client for accessing the LLM API
        embedding_model: Model to generate embeddings
        
    Returns:
        str: The ID of the added hyperedge
    """
    # Convert text to hypergraph
    print(f"Converting text to hypergraph: {text}")
    hyperedge = text_to_hypergraph(text, llm_client)
    print(f"Generated hyperedge: {hyperedge.to_string()}")
    
    # Store the hyperedge and its components
    edge_id = store.add_hyperedge(hyperedge)
    
    # Generate flattened nodes for OG-RAG style retrieval
    hypernodes = flatten_hyperedge(hyperedge)
    print(f"Flattened into {len(hypernodes)} hypernodes")
    
    # Add hypernodes to the store
    for i, (key, value) in enumerate(hypernodes):
        node_id = f"{edge_id}_node_{i}"
        store.nodes[node_id] = (key, value)
        
        # Map node to containing edge
        if edge_id not in store.node_to_edges:
            store.node_to_edges[edge_id] = set()
        store.node_to_edges[edge_id].add(node_id)
        
        # Generate and store embeddings
        key_embedding = embedding_model.embed(key)
        value_embedding = embedding_model.embed(value)
        store.node_embeddings[f"{node_id}_key"] = key_embedding
        store.node_embeddings[f"{node_id}_value"] = value_embedding
    
    return edge_id


def hybrid_hypergraph_rag(query, store, llm_client, embedding_model, pattern=None, debug=False):
    """
    Perform retrieval-augmented generation using the hybrid hypergraph.
    
    Args:
        query (str): The question to answer
        store (HypergraphStore): The hypergraph store
        llm_client: Client for accessing the LLM API
        embedding_model: Model to generate embeddings
        pattern (str, optional): Optional pattern to filter results
        debug (bool): Whether to print debug information
        
    Returns:
        str: The generated response
    """
    # Parse pattern if provided
    if pattern:
        pattern_edge = parse_hypergraph_string(pattern)
    else:
        pattern_edge = None
    
    # Retrieve relevant hyperedges
    relevant_edges = hybrid_retrieval(store, query, embedding_model, pattern_edge, debug=debug)
    
    # Format edges for context
    context = format_edges_for_context(relevant_edges)
    
    if debug:
        print(f"Using {len(relevant_edges)} edges for context")
    
    # Generate response with context
    system_prompt = """
    You are a helpful assistant with access to a knowledge base of social media discourse.
    Use the provided context to answer the question accurately.
    If the context doesn't contain enough information, say so clearly.
    """
    
    user_prompt = f"""
    Context:
    {context}
    
    Question: {query}
    """
    
    response = llm_client.generate(
        system=system_prompt,
        user=user_prompt,
        max_tokens=1000
    )
    
    return response


def format_edges_for_context(edges, max_edges=10):
    """Format edges as context for LLM."""
    formatted = []
    
    for i, edge in enumerate(edges[:max_edges]):
        # Convert to a readable format
        text = edge_to_text(edge)
        formatted.append(f"{i+1}. {text}")
        
    return "\n".join(formatted)


def edge_to_text(edge):
    """Convert an edge to natural language."""
    # For atomic edges, just return the content
    if edge.is_atomic:
        return edge.content if edge.content else ""
    
    # Handle common patterns
    if len(edge.components) >= 3:
        connector = edge.components[0]
        
        # Handle claims and arguments
        if connector.content in ["claims", "argues", "says", "states"]:
            subject = edge_to_text(edge.components[1])
            claim = edge_to_text(edge.components[2])
            return f"{subject} {connector.content} that {claim}"
        
        # Handle reports
        if connector.content == "report":
            subject = edge_to_text(edge.components[1])
            object = edge_to_text(edge.components[2])
            return f"{subject} report {object}"
        
        # Handle "is" statements
        if connector.content == "is":
            subject = edge_to_text(edge.components[1])
            predicate = edge_to_text(edge.components[2])
            return f"{subject} is {predicate}"
    
    # Default: just concatenate the text of all components
    return " ".join([edge_to_text(comp) for comp in edge.components])


def inspect_hypergraph_store(store):
    """Print detailed information about the contents of the hypergraph store."""
    print("\n===== HYPERGRAPH STORE INSPECTION =====")
    print(f"Total edges: {len(store.edges_by_id)}")
    print(f"Total nodes: {len(store.nodes)}")
    
    # Analyze edge types
    edge_types = {}
    domain_types = {}
    
    for edge_id, edge in store.edges_by_id.items():
        # Count edge types
        if edge.edge_type:
            edge_type = edge.edge_type
            edge_types[edge_type] = edge_types.get(edge_type, 0) + 1
        
        # Count domain types
        if edge.domain_type:
            domain_types[edge.domain_type] = domain_types.get(edge.domain_type, 0) + 1
    
    print("\nEdge types:")
    for type_name, count in edge_types.items():
        print(f"  - {type_name}: {count} edges")
    
    print("\nDomain types:")
    for type_name, count in domain_types.items():
        print(f"  - {type_name}: {count} edges")
    
    # Show sample edges
    print("\nSample edges:")
    for i, (edge_id, edge) in enumerate(list(store.edges_by_id.items())[:5]):
        print(f"  - Edge {i+1} (ID: {edge_id}): {edge.to_string()}")
    
    # Show sample nodes
    print("\nSample nodes:")
    for i, (node_id, node) in enumerate(list(store.nodes.items())[:5]):
        key, value = node
        print(f"  - Node {i+1} (ID: {node_id}): Key='{key}', Value='{value}'")
    
    print("========================================")


def create_sample_text_file(file_path):
    """Create a sample text file with extensive content for testing."""
    content = """# Climate Change: Global Perspectives and Political Responses

## Introduction
Climate change represents one of the most significant challenges facing humanity in the 21st century. Rising temperatures, shifting weather patterns, and extreme weather events all indicate substantial changes in our global climate system. This document explores various perspectives on climate change, political responses, and technological solutions.

## Scientific Consensus
Climate scientists around the world have reached a strong consensus that global temperatures are rising due to human activities, particularly the emission of greenhouse gases. According to the Intergovernmental Panel on Climate Change (IPCC), global temperatures have already increased by approximately 1.1°C above pre-industrial levels, and are projected to continue rising if emissions are not drastically reduced.

Dr. Jane Roberts, leading climate scientist at the Global Climate Institute, reports that ice core samples provide clear evidence of accelerated warming over the past century compared to natural climate variations over the previous millennium.

## Political Perspectives

### United States
In the United States, perspectives on climate change often fall along partisan lines. While Democratic politicians generally support aggressive action to combat climate change, Republican lawmakers have historically been more skeptical about both the severity of the problem and the economic impacts of proposed solutions.

President Biden has claimed that climate change presents a serious threat to national security and economic stability. His administration has set ambitious goals to reduce greenhouse gas emissions by 50-52% below 2005 levels by 2030 and to achieve net-zero emissions by 2050.

Former President Trump, during his administration, expressed skepticism about climate science and withdrew the United States from the Paris Climate Agreement, arguing that it placed an unfair economic burden on American workers and businesses.

### European Union
The European Union has positioned itself as a global leader in climate action. The European Green Deal, announced in 2019, aims to make Europe the first climate-neutral continent by 2050. European Commission President Ursula von der Leyen has stated that addressing climate change is both a moral imperative and an economic opportunity.

German Chancellor Olaf Scholz has emphasized that transitioning to renewable energy sources is essential for long-term economic stability and energy independence. France's President Emmanuel Macron has argued that nuclear power must be part of the solution to reduce carbon emissions while meeting energy demands.

### Developing Nations
Leaders from developing nations often highlight the unfair dynamics of climate action, noting that industrialized countries built their wealth through carbon-intensive development that is now being discouraged for emerging economies.

India's Prime Minister Narendra Modi has advocated for "climate justice," arguing that developing nations need financial support from wealthy countries to transition to cleaner technologies while still pursuing economic growth and poverty reduction.

## Technological Solutions

### Renewable Energy
Technological advancements have dramatically reduced the cost of renewable energy sources over the past decade. Solar panel efficiency has improved while costs have fallen by more than 80%, making solar energy competitive with fossil fuels in many markets.

Elon Musk has argued that electric vehicles, combined with renewable energy generation, are essential for reducing carbon emissions from the transportation sector, which accounts for approximately one-quarter of global emissions.

### Carbon Capture
Carbon capture and storage (CCS) technologies aim to remove carbon dioxide from industrial emissions or directly from the atmosphere. While promising, these technologies are currently expensive and not yet deployed at scale.

Bill Gates has invested significantly in carbon capture technologies, stating that innovation in this area is critical for achieving net-zero emissions, particularly for industries that are difficult to decarbonize such as cement and steel production.

## Economic Implications
The economic implications of climate change and climate policy are complex and widely debated.

Economists like Nicholas Stern argue that the long-term costs of inaction far outweigh the short-term costs of reducing emissions. According to the Stern Review, climate change could reduce global GDP by up to 20% if left unaddressed.

In contrast, some industry groups and conservative economists warn that aggressive climate policies could slow economic growth, eliminate jobs in fossil fuel industries, and increase energy costs for consumers.

## Public Opinion
Public concern about climate change varies significantly between countries and demographic groups. Younger generations generally express higher levels of concern and support for climate action than older populations.

A recent global survey by the Pew Research Center found that 67% of respondents consider climate change a major threat to their country, though this varies from over 80% in some European and Asian countries to under 50% in certain other nations.

## Conclusion
The challenge of climate change requires coordinated global action across political, technological, and economic dimensions. While perspectives differ on the pace and methods of addressing climate change, there is growing recognition that some form of response is necessary. The coming decades will be crucial in determining whether humanity can successfully mitigate the worst potential impacts of climate change while adapting to the changes that are already occurring."""
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Created sample text file: {file_path}")
    return file_path


def load_and_process_file(file_path, store, llm_client, embedding_model, chunk_size=1000):
    """
    Load text from a file, chunk it, and process each chunk into the hypergraph store.
    
    Args:
        file_path (str): Path to the text file
        store (HypergraphStore): The hypergraph store
        llm_client: Client for accessing the LLM API
        embedding_model: Model to generate embeddings
        chunk_size (int): Size of text chunks to process
    """
    print(f"Loading text from {file_path}...")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        text = f.read()
    
    # Split text into chunks of approximately chunk_size characters
    chunks = []
    current_chunk = ""
    
    for paragraph in text.split('\n\n'):
        # If adding this paragraph would exceed chunk_size, add current chunk to chunks and start a new one
        if len(current_chunk) + len(paragraph) > chunk_size:
            chunks.append(current_chunk.strip())
            current_chunk = paragraph
        else:
            current_chunk += "\n\n" + paragraph if current_chunk else paragraph
    
    # Add the last chunk if it's not empty
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    print(f"Split text into {len(chunks)} chunks")
    
    # Process each chunk
    for i, chunk in enumerate(chunks):
        print(f"Processing chunk {i+1}/{len(chunks)}...")
        add_text_to_store(chunk, store, llm_client, embedding_model)
    
    return len(chunks)


def main():
    """Main function to demonstrate the hybrid hypergraph system."""
    import os
    
    # Check for OpenAI API key in environment variables
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("Warning: OPENAI_API_KEY environment variable not set.")
        print("Using placeholder embedding and LLM implementations.")
        # Use placeholder models if no API key
        embedding_model = PlaceholderEmbeddingModel()
        llm_client = PlaceholderLLMClient()
    else:
        # Initialize models with real OpenAI implementations
        print("Using OpenAI for embeddings and LLM.")
        embedding_model = EmbeddingModel(api_key)
        llm_client = LLMClient(api_key)
    
    # Initialize hypergraph store
    store = HypergraphStore()
    
    # Create and process sample text file
    file_path = "climate_change_perspectives.txt"
    create_sample_text_file(file_path)
    load_and_process_file(file_path, store, llm_client, embedding_model)
    
    # Inspect the store
    inspect_hypergraph_store(store)
    
    # Save structured data to file for examination
    print("Saving hypergraph data to 'hypergraph_data.txt'...")
    with open('hypergraph_data.txt', 'w') as f:
        f.write("=== EDGES ===\n")
        for edge_id, edge in store.edges_by_id.items():
            f.write(f"Edge ID: {edge_id}\n")
            f.write(f"String: {edge.to_string()}\n")
            f.write(f"Type: {edge.edge_type}, Domain: {edge.domain_type}\n")
            f.write(f"Components: {len(edge.components)}\n")
            f.write("-" * 40 + "\n")

        f.write("\n=== NODES ===\n")
        for node_id, node in store.nodes.items():
            key, value = node
            f.write(f"Node ID: {node_id}\n")
            f.write(f"Key: {key}\n")
            f.write(f"Value: {value}\n")
            f.write("-" * 40 + "\n")
            
        f.write("\n=== INDICES ===\n")
        f.write("SH Indices:\n")
        for idx_name, idx in store.sh_indices.items():
            f.write(f"{idx_name}: {idx}\n")
        f.write("\nOG Indices:\n")
        for idx_name, idx in store.og_indices.items():
            f.write(f"{idx_name}: {idx}\n")
    
    # Perform multiple queries to test the system
    queries = [
        "What does Biden think about climate change?",
        "What is Elon Musk's position on electric vehicles?",
        "How do developing nations view climate change policies?",
        "What are the economic implications of climate change?",
        "How has public opinion on climate change evolved?"
    ]
    
    for query in queries:
        print(f"\nQuery: {query}")
        result = hybrid_hypergraph_rag(query, store, llm_client, embedding_model, debug=True)
        print(f"Result: {result}")


if __name__ == "__main__":
    main()
