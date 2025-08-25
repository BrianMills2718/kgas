import uuid
import json
from typing import List, Dict, Set, Optional, Union, Tuple, Any
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI

class Hyperedge:
    """Represents a hyperedge in the semantic hypergraph."""
    
    def __init__(self, id=None, content=None, edge_type=None, components=None, roles=None):
        """
        Initialize a hyperedge.
        
        Args:
            id (str): Unique identifier for the hyperedge
            content (str): Content of the hyperedge if atomic
            edge_type (str): One of 'C', 'P', 'M', 'B', 'T', 'J', 'R', 'S'
            components (list): List of Hyperedge objects for non-atomic edges
            roles (list): List of role strings corresponding to components
        """
        self.id = id or str(uuid.uuid4())
        self.content = content
        self.edge_type = edge_type
        self.components = components or []
        self.roles = roles or []
        
    @property
    def is_atomic(self):
        """Return True if this is an atomic hyperedge (has no components)."""
        return len(self.components) == 0
        
    def to_string(self):
        """Convert the hyperedge to its string representation."""
        if self.is_atomic:
            return f"{self.content}/{self.edge_type}"
        
        components_str = " ".join([
            f"{comp.to_string()}" + (f".{self.roles[i]}" if i < len(self.roles) and self.roles[i] else "")
            for i, comp in enumerate(self.components)
        ])
        return f"({components_str})"
        
    def infer_type(self):
        """Infer the type of this hyperedge based on its components."""
        if self.is_atomic:
            return self.edge_type
            
        if not self.components:
            return None
            
        connector = self.components[0]
        connector_type = connector.edge_type
        
        if connector_type == 'M':  # Modifier
            if len(self.components) > 1:
                return self.components[1].edge_type
            return None
        elif connector_type == 'B':  # Builder
            return 'C'  # Concept
        elif connector_type == 'T':  # Trigger
            return 'S'  # Specifier
        elif connector_type == 'P':  # Predicate
            return 'R'  # Relation
        elif connector_type == 'J':  # Conjunction
            if len(self.components) > 1:
                return self.components[1].edge_type
            return None
        else:
            return None


class HypergraphStore:
    """Storage for hyperedges with deduplication and indexing capabilities."""
    
    def __init__(self):
        """Initialize the hypergraph store."""
        self.edges_by_id = {}
        self.edge_hash_to_id = {}
        self.indices = {
            'type': {},      # type -> set of edge IDs
            'content': {},   # content -> set of edge IDs (for atomic edges)
            'component': {}  # component ID -> set of edge IDs containing it
        }
        
    def add_hyperedge(self, edge):
        """
        Add a hyperedge to the store, ensuring uniqueness.
        
        Args:
            edge (Hyperedge): The hyperedge to add
            
        Returns:
            Hyperedge: The stored hyperedge (may be pre-existing)
        """
        # Recursively ensure all components are stored
        for i, component in enumerate(edge.components):
            stored_component = self.add_hyperedge(component)
            edge.components[i] = stored_component
            
        # Generate a hash for deduplication
        edge_hash = self._compute_edge_hash(edge)
        
        # Check if this exact edge already exists
        if edge_hash in self.edge_hash_to_id:
            print(f"Edge already exists with ID: {self.edge_hash_to_id[edge_hash]}")
            return self.edges_by_id[self.edge_hash_to_id[edge_hash]]
            
        # Store the new edge
        self.edges_by_id[edge.id] = edge
        self.edge_hash_to_id[edge_hash] = edge.id
        
        # Index the edge
        self._index_edge(edge)
            
        return edge
        
    def _compute_edge_hash(self, edge):
        """Compute a hash for deduplication."""
        if edge.is_atomic:
            return f"a:{edge.content}/{edge.edge_type}"
        
        # For complex edges, hash the components and their arrangement
        component_hashes = [self._compute_edge_hash(comp) for comp in edge.components]
        role_str = "".join(edge.roles)
        return f"c:{','.join(component_hashes)}:{role_str}"
        
    def _index_edge(self, edge):
        """Index an edge for efficient retrieval."""
        # Index by type
        if edge.edge_type not in self.indices['type']:
            self.indices['type'][edge.edge_type] = set()
        self.indices['type'][edge.edge_type].add(edge.id)
        
        # For atomic edges, index by content
        if edge.is_atomic:
            if edge.content not in self.indices['content']:
                self.indices['content'][edge.content] = set()
            self.indices['content'][edge.content].add(edge.id)
            
        # For complex edges, index by components
        for component in edge.components:
            if component.id not in self.indices['component']:
                self.indices['component'][component.id] = set()
            self.indices['component'][component.id].add(edge.id)
            
    def get_edges_by_type(self, edge_type):
        """Get all edges of a specific type."""
        edge_ids = self.indices['type'].get(edge_type, set())
        print(f"Store has {len(edge_ids)} edges of type {edge_type}")
        return [self.edges_by_id[edge_id] for edge_id in edge_ids]
            
    def get_edges_by_content(self, content):
        """Get all edges with specific content."""
        edge_ids = self.indices['content'].get(content, set())
        print(f"Store has {len(edge_ids)} edges with content '{content}'")
        return [self.edges_by_id[edge_id] for edge_id in edge_ids]


class HypergraphParser:
    """Parses string representations of hypergraphs."""
    
    @staticmethod
    def parse_hypergraph_string(hypergraph_str):
        """
        Parse a string representation of a hypergraph into a Hyperedge object.
        
        Args:
            hypergraph_str (str): String representation of the hypergraph
            
        Returns:
            Hyperedge: The parsed hypergraph
        """
        def parse_element(text, pos):
            """Parse a single element (atomic or complex) starting at position pos."""
            text = text.strip()
            if pos >= len(text):
                return None, pos, ""
                
            if text[pos] == '(':
                return parse_complex_element(text, pos)
            else:
                return parse_atomic_element(text, pos)
        
        def parse_atomic_element(text, pos):
            """Parse an atomic element like 'berlin/C'."""
            end_pos = pos
            # Look for element boundary (space followed by a word with a slash, or closing parenthesis)
            while end_pos < len(text):
                # Check if we've reached the end of this element
                if text[end_pos] == ')':
                    break
                # Check if next part might be another element by looking for '/' character
                if text[end_pos] == ' ':
                    next_slash_pos = text.find('/', end_pos)
                    next_paren_pos = text.find(')', end_pos)
                    if next_slash_pos != -1 and (next_paren_pos == -1 or next_slash_pos < next_paren_pos):
                        # Found another element
                        break
                end_pos += 1
            
            atom_text = text[pos:end_pos].strip()
            
            # Handle argument roles
            role_parts = atom_text.split('.')
            atom_parts = role_parts[0].split('/')
            
            if len(atom_parts) != 2:
                raise ValueError(f"Invalid atom format: {atom_text}")
            
            content, edge_type = atom_parts
            roles = role_parts[1] if len(role_parts) > 1 else ""
            
            return Hyperedge(content=content, edge_type=edge_type), end_pos, roles
        
        def parse_complex_element(text, pos):
            """Parse a complex element like '(is/P berlin/C nice/C)'."""
            components = []
            roles_list = []
            current_pos = pos + 1  # Skip opening parenthesis
            
            # Parse components until closing parenthesis
            while current_pos < len(text) and text[current_pos] != ')':
                # Skip whitespace
                if text[current_pos].isspace():
                    current_pos += 1
                    continue
                
                # Parse next component
                component, next_pos, role = parse_element(text, current_pos)
                if component:
                    components.append(component)
                    roles_list.append(role)
                    current_pos = next_pos
                    
                    # Check for role specified after component with a space
                    if current_pos < len(text) and text[current_pos].isspace():
                        role_pos = current_pos
                        while role_pos < len(text) and text[role_pos].isspace():
                            role_pos += 1
                        
                        # Check if next token might be a role (not containing a slash and not a parenthesis)
                        if role_pos < len(text) and text[role_pos] != '(' and text[role_pos] != ')':
                            potential_role_end = role_pos
                            while (potential_role_end < len(text) and 
                                   text[potential_role_end] != ' ' and 
                                   text[potential_role_end] != '(' and 
                                   text[potential_role_end] != ')'):
                                potential_role_end += 1
                            
                            potential_role = text[role_pos:potential_role_end]
                            # If it doesn't contain a slash, it might be a role
                            if '/' not in potential_role and potential_role.strip():
                                roles_list[-1] = potential_role  # Assign to the last component
                                current_pos = potential_role_end
                
                # Skip any trailing whitespace
                while current_pos < len(text) and text[current_pos].isspace():
                    current_pos += 1
            
            if current_pos >= len(text) or text[current_pos] != ')':
                raise ValueError("Unclosed parenthesis in hypergraph")
            
            # Create the complex hyperedge
            edge = Hyperedge(components=components, roles=roles_list)
            edge.edge_type = edge.infer_type()
            
            return edge, current_pos + 1, ""  # +1 to skip closing parenthesis
        
        # Start parsing from the beginning
        try:
            hypergraph, _, _ = parse_element(hypergraph_str, 0)
            return hypergraph
        except Exception as e:
            print(f"Error parsing hypergraph: {e}")
            print(f"Problematic string: {hypergraph_str}")
            return None


class HypergraphRAG:
    """Main class for the Hypergraph Retrieval Augmented Generation system."""
    
    def __init__(self, llm_model="gpt-3.5-turbo"):
        """Initialize the Hypergraph RAG system."""
        self.store = HypergraphStore()
        self.parser = HypergraphParser()
        self.llm = ChatOpenAI(model=llm_model)
        
    def add_text(self, text):
        """
        Process text and add resulting hypergraph to the store.
        
        Args:
            text (str): The text to process
            
        Returns:
            Hyperedge: The root hyperedge of the processed text
        """
        print(f"\nProcessing text: \"{text}\"")
        hypergraph_str = self._text_to_hypergraph_string(text)
        print(f"Generated hypergraph: {hypergraph_str}")
        
        if not hypergraph_str:
            print("Failed to generate hypergraph string!")
            return None
            
        hypergraph = self.parser.parse_hypergraph_string(hypergraph_str)
        if hypergraph:
            print(f"Parsed structure: {hypergraph.to_string()}")
            result = self.store.add_hyperedge(hypergraph)
            print(f"Added to store with ID: {result.id}")
            return result
        else:
            print("Failed to parse hypergraph!")
        return None
        
    def query(self, query_text):
        """
        Process a query and return relevant knowledge.
        
        Args:
            query_text (str): The query in natural language
            
        Returns:
            str: The response
        """
        print(f"\nProcessing query: \"{query_text}\"")
        
        # Convert query to pattern
        pattern_str = self._query_to_pattern_string(query_text)
        print(f"Generated pattern: {pattern_str}")
        
        if not pattern_str:
            return "Failed to convert query to pattern."
            
        pattern = self.parser.parse_hypergraph_string(pattern_str)
        if not pattern:
            return "Failed to parse query pattern."
            
        print(f"Parsed pattern: {pattern.to_string()}")
        
        # Find matches
        matches = self._find_matches(pattern)
        print(f"Found {len(matches)} matches")
        
        # Generate response
        if not matches:
            return "No relevant information found."
            
        context = self._format_matches_for_context(matches)
        print(f"Context for response generation:\n{context}")
        
        response = self._generate_response(query_text, context)
        return response
        
    def _text_to_hypergraph_string(self, text):
        """Convert text to hypergraph string representation using LLM."""
        prompt = ChatPromptTemplate.from_messages([
            ("system", """
            You are an expert in converting natural language to semantic hypergraphs.
            
            RULES:
            1. Each hyperedge is enclosed in parentheses: (...)
            2. The first element must be a connector (P, M, B, T, J)
            3. Atomic elements are represented as name/type (e.g., berlin/C)
            4. Use argument roles by attaching them with a dot (e.g., is/P.sc for subject-complement)
            5. Always connect roles directly to their element with a dot, not a space
            
            TYPES:
            - C: Concept (nouns, objects)
            - P: Predicate (verbs, actions)
            - M: Modifier (adjectives, adverbs)
            - B: Builder (prepositions, compounds)
            - T: Trigger (specifications)
            - J: Conjunction (and, or, but)
            
            EXAMPLES:
            "Berlin is nice." → (is/P.sc berlin/C nice/C)
            "The red car." → (the/M (red/M car/C))
            "Capital of Germany" → (of/B.ma capital/C germany/C)
            "She eats quickly." → (eats/P.s she/C (quickly/M))
            "Angela Merkel was Chancellor of Germany" → (was/P.sc angela_merkel/C (of/B.ma chancellor/C germany/C))
            
            Return only the hypergraph notation, nothing else.
            """),
            ("user", f"Convert this text to a semantic hypergraph:\n\n{text}")
        ])
        
        chain = prompt | self.llm | StrOutputParser()
        result = chain.invoke({})
        
        # Try to extract the hypergraph
        import re
        match = re.search(r'\([^()]*(?:\([^()]*\)[^()]*)*\)', result)
        if match:
            return match.group(0)
        return None
        
    def _query_to_pattern_string(self, query):
        """Convert a query to a pattern string using LLM."""
        prompt = ChatPromptTemplate.from_messages([
            ("system", """
            Convert the given question into a semantic hypergraph pattern for retrieval.
            
            Use uppercase variables for unknown elements (e.g., ACTOR, CLAIM).
            
            Examples:
            "Who is the president of France?" → (is/P.sc WHO/C (of/B.ma president/C france/C))
            "What did Biden say about climate change?" → (says/P.sr biden/C CLAIM)
            
            Return only the hypergraph pattern, nothing else.
            """),
            ("user", f"Convert this question to a hypergraph pattern:\n\n{query}")
        ])
        
        chain = prompt | self.llm | StrOutputParser()
        result = chain.invoke({})
        
        # Try to extract the hypergraph
        import re
        match = re.search(r'\([^()]*(?:\([^()]*\)[^()]*)*\)', result)
        if match:
            return match.group(0)
        return None
        
    def _find_matches(self, pattern, max_matches=10):
        """Find hyperedges matching the pattern."""
        # This is a simplified matching implementation
        matches = []
        
        if pattern.is_atomic:
            # For variables (uppercase), match any of that type
            if pattern.content.isupper():
                print(f"Matching any {pattern.edge_type} for variable {pattern.content}")
                candidates = self.store.get_edges_by_type(pattern.edge_type)
                print(f"Found {len(candidates)} candidates of type {pattern.edge_type}")
                matches.extend(candidates[:max_matches])
            else:
                # For specific content, match exactly
                print(f"Matching exact content: {pattern.content}/{pattern.edge_type}")
                candidates = self.store.get_edges_by_content(pattern.content)
                print(f"Found {len(candidates)} candidates with content '{pattern.content}'")
                for edge in candidates:
                    if edge.edge_type == pattern.edge_type:
                        matches.append(edge)
        else:
            # For complex patterns, use a more sophisticated approach
            print(f"Matching complex pattern with {len(pattern.components)} components")
            # This is just a placeholder for the MVP
            if pattern.components and len(pattern.components) > 0:
                # Try to match based on the first component
                first_comp = pattern.components[0]
                print(f"Matching based on first component: {first_comp.to_string()}")
                candidates = self._find_matches(first_comp, max_matches=100)
                
                # For each candidate, check if it's a component of other edges
                for candidate in candidates:
                    edge_ids = self.store.indices['component'].get(candidate.id, set())
                    print(f"Found {len(edge_ids)} edges containing component {candidate.id}")
                    for edge_id in edge_ids:
                        edge = self.store.edges_by_id[edge_id]
                        if edge.edge_type == pattern.edge_type:
                            matches.append(edge)
                            if len(matches) >= max_matches:
                                break
                    if len(matches) >= max_matches:
                        break
        
        return matches[:max_matches]
        
    def _format_matches_for_context(self, matches):
        """Format matches for LLM context."""
        formatted = []
        for i, edge in enumerate(matches):
            # For the MVP, we'll just use the string representation
            formatted.append(f"{i+1}. {edge.to_string()}")
        return "\n".join(formatted)
        
    def _generate_response(self, query, context):
        """Generate a response using LLM with the retrieved context."""
        prompt = ChatPromptTemplate.from_messages([
            ("system", """
            You are a helpful assistant with access to a knowledge base.
            Use the provided context to answer the question accurately.
            If the context doesn't contain enough information, say so clearly.
            """),
            ("user", f"""
            Context:
            {context}
            
            Question: {query}
            """)
        ])
        
        chain = prompt | self.llm | StrOutputParser()
        return chain.invoke({})
        
    def hyperedge_to_text(self, edge):
        """Convert a hyperedge to natural language (using LLM)."""
        prompt = ChatPromptTemplate.from_messages([
            ("system", """
            Convert the semantic hypergraph notation to natural language.
            
            Examples:
            (is/P.sc berlin/C nice/C) → "Berlin is nice."
            (the/M (red/M car/C)) → "The red car."
            (of/B.ma capital/C germany/C) → "Capital of Germany"
            
            Provide only the natural language text, nothing else.
            """),
            ("user", f"Convert this hypergraph to natural language text:\n\n{edge.to_string()}")
        ])
        
        chain = prompt | self.llm | StrOutputParser()
        return chain.invoke({})


# Example usage
if __name__ == "__main__":
    # Initialize the system
    rag = HypergraphRAG()
    
    # Add knowledge
    print("Adding knowledge...")
    rag.add_text("Berlin is the capital of Germany.")
    rag.add_text("Germany is a country in Europe.")
    rag.add_text("Angela Merkel was the Chancellor of Germany from 2005 to 2021.")
    rag.add_text("The current Chancellor of Germany is Olaf Scholz.")
    
    # Query the system
    print("\nQuerying the system...")
    query = "Who is the current Chancellor of Germany?"
    print(f"Query: {query}")
    response = rag.query(query)
    print(f"Response: {response}")
    
    # Another query
    query = "What is Berlin?"
    print(f"\nQuery: {query}")
    response = rag.query(query)
    print(f"Response: {response}")
