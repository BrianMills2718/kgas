# MVP PROTOTYPE HYPERGRAPH RAG SYSTEM V1.0
# This module implements a minimal viable hypergraph-based Retrieval-Augmented Generation system.
# It integrates with LangChain's LLM for both hypergraph construction and query pattern generation.

import uuid
import re

# ------------------------------
# Core Component: Hyperedge Class
# ------------------------------
class Hyperedge:
    def __init__(self, id=None, content=None, edge_type=None, components=None, roles=None):
        """
        Initialize a hyperedge.
        
        Args:
            id (str): Unique identifier (auto-generated if None)
            content (str): Atomic content (if applicable)
            edge_type (str): One-character type (e.g., 'C', 'P', etc.)
            components (list): List of constituent Hyperedge objects
            roles (list): List of role strings corresponding to components
        """
        self.id = id or str(uuid.uuid4())
        self.content = content
        self.edge_type = edge_type
        self.components = components or []
        self.roles = roles or []
    
    @property
    def is_atomic(self):
        return len(self.components) == 0
    
    def to_string(self):
        if self.is_atomic:
            return f"{self.content}/{self.edge_type}"
        components_str = " ".join([comp.to_string() for comp in self.components])
        return f"({components_str})"
    
    def infer_type(self):
        """Infer complex hyperedge type based on the first (connector) component."""
        if self.is_atomic:
            return self.edge_type
        connector = self.components[0]
        connector_type = connector.edge_type
        if connector_type == 'M':  # Modifier: retains type
            return self.components[1].edge_type
        elif connector_type == 'B':  # Builder: yields a concept
            return 'C'
        elif connector_type == 'T':  # Trigger: yields a specifier
            return 'S'
        elif connector_type == 'P':  # Predicate: yields a relation
            return 'R'
        elif connector_type == 'J':  # Conjunction: inherits first element's type
            return self.components[1].edge_type
        else:
            raise ValueError(f"Unknown connector type: {connector_type}")

# ------------------------------
# LLM-Integrated Text-to-Hypergraph Converter
# ------------------------------
def text_to_hypergraph(text, llm_client):
    system_prompt = """
You are an expert in converting natural language to semantic hypergraphs.
RULES:
1. Each hyperedge is enclosed in parentheses: (...)
2. The first element must be a connector (P, M, B, T, J)
3. Atomic elements are represented as name/type (e.g., berlin/C)
4. Use argument roles when appropriate (e.g., is/P.sc for subject-complement)

TYPES:
- C: Concept
- P: Predicate
- M: Modifier
- B: Builder
- T: Trigger
- J: Conjunction

EXAMPLES:
"Berlin is nice." → (is/P.sc berlin/C nice/C)
"The red car." → (the/M (red/M car/C))
"Capital of Germany" → (of/B.ma capital/C germany/C)
"She eats quickly." → (eats/P.s she/C (quickly/M))
"""
    user_prompt = f"Convert this text to a semantic hypergraph:\n\n{text}"
    # Call the LLM via LangChain (llm_client is expected to be a callable)
    response = llm_client(user_prompt, system_prompt)
    hypergraph_str = extract_hypergraph_from_response(response)
    return parse_hypergraph_string(hypergraph_str)

def extract_hypergraph_from_response(response):
    """Extract the hypergraph string from the LLM response using regex."""
    match = re.search(r'\(.*\)', response, re.DOTALL)
    if match:
        return match.group(0)
    else:
        raise ValueError("No hypergraph found in response")

# ------------------------------
# Hypergraph Parser Implementation
# ------------------------------
def parse_hypergraph_string(hypergraph_str):
    def parse_element(text, pos):
        if text[pos] == '(':
            return parse_complex_element(text, pos)
        else:
            return parse_atomic_element(text, pos)
    
    def parse_atomic_element(text, pos):
        # Determine end position by whitespace or closing parenthesis
        end_pos_space = text.find(' ', pos)
        end_pos_paren = text.find(')', pos)
        if end_pos_space == -1 or (end_pos_paren != -1 and end_pos_paren < end_pos_space):
            end_pos = end_pos_paren
        else:
            end_pos = end_pos_space
        atom_text = text[pos:end_pos].strip()
        role_parts = atom_text.split('.')
        atom_parts = role_parts[0].split('/')
        if len(atom_parts) != 2:
            raise ValueError(f"Invalid atom format: {atom_text}")
        content, edge_type = atom_parts
        roles = role_parts[1] if len(role_parts) > 1 else ""
        return Hyperedge(content=content, edge_type=edge_type), end_pos, roles
    
    def parse_complex_element(text, pos):
        components = []
        roles_list = []
        current_pos = pos + 1  # Skip opening parenthesis
        while current_pos < len(text) and text[current_pos] != ')':
            if text[current_pos].isspace():
                current_pos += 1
                continue
            comp, next_pos, role = parse_element(text, current_pos)
            components.append(comp)
            roles_list.append(role)
            current_pos = next_pos
            while current_pos < len(text) and text[current_pos].isspace():
                current_pos += 1
        if current_pos >= len(text) or text[current_pos] != ')':
            raise ValueError("Unclosed parenthesis in hypergraph")
        edge = Hyperedge(components=components, roles=roles_list)
        edge.edge_type = edge.infer_type()
        return edge, current_pos + 1, ""
    
    hypergraph, _, _ = parse_element(hypergraph_str, 0)
    return hypergraph

# ------------------------------
# Hypergraph Storage with Deduplication and Indexing
# ------------------------------
class HypergraphStore:
    def __init__(self, db_connection=None):
        self.edges_by_id = {}
        self.edge_hash_to_id = {}
        self.indices = {
            'type': {},      # type -> set(edge IDs)
            'content': {},   # content -> set(edge IDs) for atomic edges
            'component': {}  # component ID -> set(edge IDs) containing it
        }
        self.db = db_connection
    
    def add_hyperedge(self, edge):
        # Recursively store all components
        for i, component in enumerate(edge.components):
            stored_component = self.add_hyperedge(component)
            edge.components[i] = stored_component
        
        edge_hash = self._compute_edge_hash(edge)
        if edge_hash in self.edge_hash_to_id:
            return self.edges_by_id[self.edge_hash_to_id[edge_hash]]
        self.edges_by_id[edge.id] = edge
        self.edge_hash_to_id[edge_hash] = edge.id
        self._index_edge(edge)
        if self.db:
            self._persist_edge(edge)
        return edge
    
    def _compute_edge_hash(self, edge):
        if edge.is_atomic:
            return f"a:{edge.content}/{edge.edge_type}"
        component_hashes = [self._compute_edge_hash(comp) for comp in edge.components]
        role_str = "".join(edge.roles)
        return f"c:{','.join(component_hashes)}:{role_str}"
    
    def _index_edge(self, edge):
        # Index by type
        if edge.edge_type not in self.indices['type']:
            self.indices['type'][edge.edge_type] = set()
        self.indices['type'][edge.edge_type].add(edge.id)
        # Index atomic edges by content
        if edge.is_atomic:
            if edge.content not in self.indices['content']:
                self.indices['content'][edge.content] = set()
            self.indices['content'][edge.content].add(edge.id)
        # Index complex edges by their components
        for component in edge.components:
            if component.id not in self.indices['component']:
                self.indices['component'][component.id] = set()
            self.indices['component'][component.id].add(edge.id)
    
    def _persist_edge(self, edge):
        # Database persistence logic would be implemented here.
        pass

# ------------------------------
# Pattern Matching and Retrieval Functions
# ------------------------------
def query_to_pattern(query, llm_client):
    # Preprocess query to remove meta-instructions
    query = re.sub(r'based on (the )?data\??', '', query, flags=re.IGNORECASE).strip()
    query = re.sub(r'according to (the )?data\??', '', query, flags=re.IGNORECASE).strip()
    
    system_prompt = """
Convert the given question into a semantic hypergraph pattern for retrieval.

Use uppercase variables for unknown elements (e.g., ACTOR, CLAIM).

Examples:
"Who is the president of France?" → (is/P.sc WHO/C (of/B.ma president/C france/C))
"What did Biden say about climate change?" → (says/P.sr biden/C CLAIM)
"""
    user_prompt = f"Convert this question to a hypergraph pattern:\n\n{query}"
    response = llm_client(user_prompt, system_prompt)
    pattern_str = extract_hypergraph_from_response(response)
    return parse_hypergraph_string(pattern_str)

def find_matches(store, pattern):
    matches = []
    candidates = _find_candidate_edges(store, pattern)
    print(f"DEBUG - Candidate edges: {len(candidates)} found")
    for edge_id in candidates:
        edge = store.edges_by_id[edge_id]
        if _edge_matches_pattern(edge, pattern):
            matches.append(edge)
    print(f"DEBUG - Final matches: {len(matches)} found")
    return matches

def _find_candidate_edges(store, pattern):
    if pattern.is_atomic:
        if pattern.content.isupper():
            candidates = store.indices['type'].get(pattern.edge_type, set())
            print(f"DEBUG - Atomic pattern with variable {pattern.content}, type {pattern.edge_type}. Found {len(candidates)} candidates.")
            return candidates
        else:
            content_matches = store.indices['content'].get(pattern.content, set())
            type_matches = store.indices['type'].get(pattern.edge_type, set())
            candidates = content_matches.intersection(type_matches)
            print(f"DEBUG - Atomic pattern with content '{pattern.content}', type {pattern.edge_type}. Found {len(candidates)} candidates.")
            return candidates
    else:
        candidates = store.indices['type'].get(pattern.edge_type, set())
        print(f"DEBUG - Complex pattern with type {pattern.edge_type}. Found {len(candidates)} candidates.")
        return candidates

def _edge_matches_pattern(edge, pattern):
    if pattern.edge_type and edge.edge_type != pattern.edge_type:
        print(f"DEBUG - Type mismatch: pattern {pattern.edge_type} vs edge {edge.edge_type}")
        return False
    if pattern.is_atomic:
        if edge.is_atomic:
            result = pattern.content.isupper() or (pattern.content == edge.content)
            print(f"DEBUG - Atomic match: {pattern.content} vs {edge.content} = {result}")
            return result
        print(f"DEBUG - Atomic pattern but edge is complex")
        return False
    if len(pattern.components) > len(edge.components):
        print(f"DEBUG - Pattern has more components than edge")
        return False
    if not _edge_matches_pattern(edge.components[0], pattern.components[0]):
        print(f"DEBUG - First component mismatch")
        return False
    for i in range(1, len(pattern.components)):
        if i >= len(edge.components) or not _edge_matches_pattern(edge.components[i], pattern.components[i]):
            print(f"DEBUG - Component {i} mismatch")
            return False
    print(f"DEBUG - Full match successful: {edge.to_string()}")
    return True

# ------------------------------
# RAG System Integration
# ------------------------------
def hypergraph_rag(query, store, llm_client):
    print("\nDEBUG === Starting RAG process ===")
    print(f"DEBUG - Query: '{query}'")
    print(f"DEBUG - Store has {len(store.edges_by_id)} edges")
    
    # Convert natural language query into a hypergraph pattern.
    pattern = query_to_pattern(query, llm_client)
    print(f"DEBUG - Generated pattern: {pattern.to_string()}")
    
    # Retrieve matching hyperedges.
    matches = find_matches(store, pattern)
    print(f"DEBUG - Found {len(matches)} matching hyperedges")
    
    # Format the matching hyperedges as context.
    context = format_matches_for_context(matches)
    print(f"DEBUG - Context for LLM:\n{context}")
    
    system_prompt = """
You are a helpful assistant with access to a knowledge base.
Use the provided context to answer the question accurately.
If the context doesn't contain enough information, say so clearly.
"""
    user_prompt = f"Context:\n{context}\n\nQuestion: {query}"
    response = llm_client(user_prompt, system_prompt)
    return response

def format_matches_for_context(matches, max_matches=10):
    formatted = []
    for i, edge in enumerate(matches[:max_matches]):
        text = hyperedge_to_text(edge)
        formatted.append(f"{i+1}. {text}")
    if not formatted:
        return "No matching information found in the knowledge base."
    return "\n".join(formatted)

def hyperedge_to_text(edge):
    if edge.is_atomic:
        return edge.content
    connector = edge.components[0]
    if connector.edge_type == 'P' and len(edge.components) >= 3:
        if connector.content == "is":
            subj = hyperedge_to_text(edge.components[1])
            obj = hyperedge_to_text(edge.components[2])
            return f"{subj} is {obj}."
        elif len(edge.roles) >= 3 and 's' in edge.roles[1] and 'o' in edge.roles[2]:
            subj = hyperedge_to_text(edge.components[1])
            verb = connector.content
            obj = hyperedge_to_text(edge.components[2])
            return f"{subj} {verb}s {obj}."
    return edge.to_string()

# ------------------------------
# Demonstration of MVP Usage
# ------------------------------
if __name__ == "__main__":
    # Example minimal LLM client using LangChain's OpenAI interface.
    from langchain_openai import OpenAI
    # Instantiate the LLM with zero temperature for deterministic outputs.
    llm = OpenAI(temperature=0)
    
    # Define a simple llm_client wrapper that uses invoke() instead of direct calling
    def llm_client(user_prompt, system_prompt):
        prompt = system_prompt + "\n" + user_prompt
        return llm.invoke(prompt)
    
    # Initialize an empty HypergraphStore.
    store = HypergraphStore()
    
    # Example: Convert input text into a hypergraph and store it.
    text_input = "Berlin is nice."
    try:
        print("\nDEBUG === Creating and storing hypergraph ===")
        hypergraph = text_to_hypergraph(text_input, llm_client)
        print(f"DEBUG - Created hypergraph: {hypergraph.to_string()}")
        stored_edge = store.add_hyperedge(hypergraph)
        print("Stored Hypergraph:", stored_edge.to_string())
        print(f"DEBUG - Store index stats:")
        print(f"  - Edges by ID: {len(store.edges_by_id)}")
        print(f"  - Type index: {', '.join([f'{k}: {len(v)}' for k, v in store.indices['type'].items()])}")
        print(f"  - Content index: {', '.join([f'{k}: {len(v)}' for k, v in store.indices['content'].items()])}")
    except Exception as e:
        print("Error in processing hypergraph:", e)
    
    # Example: Use RAG to answer a query based on stored hypergraph data.
    query = "is berlin nice?"
    try:
        answer = hypergraph_rag(query, store, llm_client)
        print("RAG Answer:", answer)
    except Exception as e:
        print("Error in hypergraph RAG process:", e)
