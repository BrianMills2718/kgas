import uuid
import numpy as np

# --------------------------------------------------------------------------------
# HYPERGRAPH SYSTEM PROTOTYPE V1.0
# This module implements a hybrid semantic hypergraph system combining Semantic Hypergraphs (SH)
# and Ontology-Grounded RAG (OG-RAG) for discourse analysis.
# --------------------------------------------------------------------------------

# ----- Core Data Structures -----

class Hyperedge:
    def __init__(self, id=None, content=None, edge_type=None, domain_type=None, components=None, roles=None):
        """
        Initialize a hyperedge in the hybrid system.
        
        Args:
            id (str): Unique identifier for the hyperedge.
            content (str): Text content if this is an atomic hyperedge.
            edge_type (str): One of the 8 SH types: 'C', 'P', 'M', 'B', 'T', 'J', 'R', 'S'.
            domain_type (str): Optional domain-specific type (e.g., 'PoliticalActor', 'Claim').
            components (list): List of Hyperedge objects for non-atomic edges.
            roles (list): List of role strings corresponding to components.
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
        self.nodes = {}  # Hypernode storage: node_id -> (key, value)
        self.node_to_edges = {}  # Maps edge_id to a set of node_ids
        self.node_embeddings = {}  # Maps node identifiers (with key/value suffix) to embedding vectors
        
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
    
    def add_hyperedge(self, edge: Hyperedge):
        """
        Add a hyperedge to the store.
        
        Args:
            edge (Hyperedge): The hyperedge to add.
            
        Returns:
            str: The unique ID of the added hyperedge.
        """
        self.edges_by_id[edge.id] = edge
        # (Indices updates for a full implementation would go here)
        return edge.id

# ----- Helper Functions for Parsing and LLM Interaction -----

def extract_hypergraph_from_response(response):
    """
    Dummy extractor for converting an LLM response to a hypergraph string.
    In production, implement robust extraction.
    """
    return response.strip()

def parse_hypergraph_string(hypergraph_str):
    """
    Minimal parser for a hypergraph string.
    For a non-atomic string (starting with '('), returns a hyperedge with the string as content.
    For an atomic string, expects the format 'content/edge_type[:domain_type]'.
    """
    hypergraph_str = hypergraph_str.strip()
    if hypergraph_str.startswith('('):
        # For a non-atomic hyperedge, this stub simply encapsulates the string.
        return Hyperedge(content=hypergraph_str, edge_type='C')
    else:
        # Parse atomic hyperedge
        parts = hypergraph_str.split(':')
        domain_type = parts[1] if len(parts) > 1 else None
        content_edge = parts[0]
        content_parts = content_edge.split('/')
        content = content_parts[0]
        edge_type = content_parts[1] if len(content_parts) > 1 else None
        return Hyperedge(content=content, edge_type=edge_type, domain_type=domain_type)

def text_to_hypergraph(text, llm_client):
    """
    Convert natural language text to a hybrid semantic hypergraph.
    
    Args:
        text (str): The input text to convert.
        llm_client: Client for accessing the LLM API.
        
    Returns:
        Hyperedge: The root hyperedge representing the text.
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

# ----- Flattening Algorithm (OG-RAG Style) -----

def flatten_hyperedge(edge: Hyperedge):
    """
    Flatten a complex hyperedge into semantic hypernodes for efficient retrieval.
    
    Args:
        edge (Hyperedge): The hyperedge to flatten.
        
    Returns:
        list: List of hypernodes (key-value pairs).
    """
    if edge.is_atomic:
        return []
    
    hypernodes = []
    
    # Generate key-value pairs for direct relationships
    if len(edge.components) >= 2:
        connector = edge.components[0]
        for i in range(1, len(edge.components)):
            role = edge.roles[i] if i < len(edge.roles) else ""
            key = f"{connector.content}/{connector.edge_type}.{role}"
            value_comp = edge.components[i]
            value = value_comp.to_string()
            hypernodes.append((key, value))
            
            # Recursively flatten nested components
            if not value_comp.is_atomic:
                nested_hypernodes = flatten_hyperedge(value_comp)
                for nested_key, nested_value in nested_hypernodes:
                    expanded_key = f"{key} {nested_key}"
                    hypernodes.append((expanded_key, nested_value))
    
    return hypernodes

# ----- Pattern Matching (SH Style) -----

def _find_candidate_edges(store: HypergraphStore, pattern: Hyperedge):
    """
    For a minimal prototype, candidate edges are all edges in the store.
    """
    return list(store.edges_by_id.keys())

def _edge_matches_pattern(edge: Hyperedge, pattern: Hyperedge):
    """Check if an edge matches a given pattern."""
    # Structural type check
    if pattern.edge_type and edge.edge_type != pattern.edge_type:
        return False
        
    # Domain type check (if specified)
    if pattern.domain_type and edge.domain_type != pattern.domain_type:
        return False
        
    # For atomic patterns
    if pattern.is_atomic:
        if edge.is_atomic:
            # Variables (uppercase) match anything of the right type
            if pattern.content.isupper():
                return True
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

def find_pattern_matches(store: HypergraphStore, pattern: Hyperedge):
    """
    Find hyperedges in the store that match a specific SH pattern.
    
    Args:
        store (HypergraphStore): The hypergraph store.
        pattern (Hyperedge): The pattern to match.
        
    Returns:
        list: List of matching hyperedges.
    """
    matches = []
    candidates = _find_candidate_edges(store, pattern)
    for edge_id in candidates:
        edge = store.edges_by_id[edge_id]
        if _edge_matches_pattern(edge, pattern):
            matches.append(edge)
    return matches

# ----- Greedy Node Coverage (OG-RAG Style) -----

def cosine_similarity(vec1, vec2):
    """
    Compute cosine similarity between two vectors.
    """
    vec1 = np.array(vec1)
    vec2 = np.array(vec2)
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return np.dot(vec1, vec2) / (norm1 * norm2)

def retrieval_by_coverage(store: HypergraphStore, query, embedding_model, k=5, max_edges=3):
    """
    Retrieve hyperedges using OG-RAG's node coverage algorithm.
    
    Args:
        store (HypergraphStore): The hypergraph store.
        query (str): The query text.
        embedding_model: Model to generate embeddings.
        k (int): Number of top hypernode matches to consider.
        max_edges (int): Maximum number of hyperedges to return.
        
    Returns:
        list: List of hyperedges that maximally cover query-relevant nodes.
    """
    query_embedding = embedding_model.embed(query)
    
    # Find relevant hypernodes (both keys and values)
    key_matches = []
    value_matches = []
    
    for node_id, node in store.nodes.items():
        key, value = node
        key_embedding = embedding_model.embed(key)
        key_similarity = cosine_similarity(query_embedding, key_embedding)
        
        value_embedding = embedding_model.embed(value)
        value_similarity = cosine_similarity(query_embedding, value_embedding)
        
        key_matches.append((node_id, key_similarity))
        value_matches.append((node_id, value_similarity))
    
    key_matches = sorted(key_matches, key=lambda x: x[1], reverse=True)[:k]
    value_matches = sorted(value_matches, key=lambda x: x[1], reverse=True)[:k]
    
    relevant_nodes = set([node_id for node_id, _ in key_matches + value_matches])
    
    # Greedy algorithm to find covering hyperedges
    selected_edges = []
    uncovered_nodes = relevant_nodes.copy()
    
    while uncovered_nodes and len(selected_edges) < max_edges:
        best_edge = None
        best_coverage = 0
        
        # Evaluate each edge for coverage of uncovered nodes
        for edge_id, edge in store.edges_by_id.items():
            edge_nodes = set()
            for node_id in store.node_to_edges.get(edge_id, []):
                if node_id in uncovered_nodes:
                    edge_nodes.add(node_id)
            coverage = len(edge_nodes)
            if coverage > best_coverage:
                best_coverage = coverage
                best_edge = edge_id
        
        if best_edge and best_coverage > 0:
            selected_edges.append(store.edges_by_id[best_edge])
            for node_id in store.node_to_edges.get(best_edge, []):
                if node_id in uncovered_nodes:
                    uncovered_nodes.remove(node_id)
        else:
            break
    
    return selected_edges

# ----- Hybrid Retrieval -----

def hybrid_retrieval(store: HypergraphStore, query, embedding_model, pattern=None):
    """
    Perform hybrid retrieval combining pattern matching and node coverage.
    
    Args:
        store (HypergraphStore): The hypergraph store.
        query (str): The query text.
        embedding_model: Model to generate embeddings.
        pattern (Hyperedge, optional): Optional SH pattern to filter results.
        
    Returns:
        list: List of relevant hyperedges.
    """
    # Retrieve semantically relevant edges via node coverage
    semantic_matches = retrieval_by_coverage(store, query, embedding_model)
    
    if pattern:
        pattern_matches = find_pattern_matches(store, pattern)
        semantic_ids = {edge.id for edge in semantic_matches}
        pattern_ids = {edge.id for edge in pattern_matches}
        return [edge for edge in semantic_matches if edge.id in (semantic_ids & pattern_ids)]
    
    return semantic_matches

# ----- Adding New Content -----

def add_text_to_store(text, store: HypergraphStore, llm_client, embedding_model):
    """
    Process text and add it to the hypergraph store.
    
    Args:
        text (str): The text to process.
        store (HypergraphStore): The hypergraph store.
        llm_client: Client for accessing the LLM API.
        embedding_model: Model to generate embeddings.
        
    Returns:
        str: The ID of the added hyperedge.
    """
    # Convert text to hyperedge
    hyperedge = text_to_hypergraph(text, llm_client)
    
    # Store the hyperedge and its components
    edge_id = store.add_hyperedge(hyperedge)
    
    # Generate flattened nodes for OG-RAG style retrieval
    hypernodes = flatten_hyperedge(hyperedge)
    
    # Add hypernodes to the store
    for i, (key, value) in enumerate(hypernodes):
        node_id = f"{edge_id}_node_{i}"
        store.nodes[node_id] = (key, value)
        
        if edge_id not in store.node_to_edges:
            store.node_to_edges[edge_id] = set()
        store.node_to_edges[edge_id].add(node_id)
        
        key_embedding = embedding_model.embed(key)
        value_embedding = embedding_model.embed(value)
        store.node_embeddings[f"{node_id}_key"] = key_embedding
        store.node_embeddings[f"{node_id}_value"] = value_embedding
    
    return edge_id

# ----- Complete RAG System -----

def hybrid_hypergraph_rag(query, store: HypergraphStore, llm_client, embedding_model, pattern=None):
    """
    Perform retrieval-augmented generation using the hybrid hypergraph.
    
    Args:
        query (str): The question to answer.
        store (HypergraphStore): The hypergraph store.
        llm_client: Client for accessing the LLM API.
        embedding_model: Model to generate embeddings.
        pattern (str, optional): Optional pattern (in hypergraph string form) to filter results.
        
    Returns:
        str: The generated response.
    """
    if pattern:
        pattern_edge = parse_hypergraph_string(pattern)
    else:
        pattern_edge = None
    
    # Retrieve relevant hyperedges using hybrid retrieval
    relevant_edges = hybrid_retrieval(store, query, embedding_model, pattern_edge)
    
    # Format edges for context
    context = format_edges_for_context(relevant_edges)
    
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
    """
    Format a list of hyperedges as context for LLM consumption.
    
    Args:
        edges (list): List of Hyperedge objects.
        max_edges (int): Maximum number of edges to include.
        
    Returns:
        str: A formatted string representing the context.
    """
    formatted = []
    for i, edge in enumerate(edges[:max_edges]):
        text = edge_to_text(edge)
        formatted.append(f"{i+1}. {text}")
    return "\n".join(formatted)

def edge_to_text(edge: Hyperedge):
    """
    Convert a hyperedge to natural language text.
    This is a placeholder; in practice, implement a template-based conversion or LLM call.
    """
    return edge.to_string()

# --------------------------------------------------------------------------------
# END OF HYPERGRAPH SYSTEM PROTOTYPE V1.0
# --------------------------------------------------------------------------------
