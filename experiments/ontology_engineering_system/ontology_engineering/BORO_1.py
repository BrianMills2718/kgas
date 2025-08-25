# BORO ANALYSIS DECISION TREE IMPLEMENTATION V1.0
import streamlit as st
import streamlit.components.v1 as components
from pyvis.network import Network
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

# Load environment variables
load_dotenv()

# --- FUNCTION: INITIALIZE LANGCHAIN LLM ---
def init_llm():
    """
    Initializes and returns a LangChain ChatOpenAI instance.
    """
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in environment variables")
        
    return ChatOpenAI(
        model="gpt-4",
        temperature=0,
        max_tokens=4000
    )

def call_llm_chain(llm: ChatOpenAI, prompt_template: str, **kwargs) -> str:
    """
    Creates and executes a LangChain chain with the given prompt template and variables.
    Returns cleaned response text.
    """
    try:
        prompt = PromptTemplate(
            template=prompt_template,
            input_variables=list(kwargs.keys())
        )
        chain = LLMChain(llm=llm, prompt=prompt)
        response = chain.run(**kwargs)
        
        # Clean and validate response
        if not response:
            raise ValueError("Empty response from LLM")
        
        return response.strip()
    except Exception as e:
        st.error(f"LLM chain execution failed: {str(e)}")
        return ""




def boro_analysis(concept: str, graph: Network, visited: set, depth: int = 0, max_depth: int = 10) -> None:
    """
    Recursively applies the BORO analysis decision tree to the given concept.
    """
    # Clean the concept string
    concept = concept.strip()
    if not concept:
        return

    # Check if we've already analyzed this concept
    if concept.lower() in {v.lower() for v in visited}:
        st.write(f"DEBUG: Concept '{concept}' has already been analyzed. Skipping recursion.")
        return

    # Check max depth
    if depth > max_depth:
        st.write(f"DEBUG: Maximum recursion depth ({max_depth}) reached for concept: '{concept}'.")
        return

    # Add to visited set
    visited.add(concept)
    st.write(f"DEBUG: Analyzing concept '{concept}' at depth {depth}")

    try:
        llm = init_llm()
    except Exception as e:
        st.error(f"Failed to initialize LLM: {str(e)}")
        return

    # --- Step 1: Check for spatio-temporal extent ---
    prompt_extent = """BORO ANALYSIS: Analyze if the concept '{concept}' has spatio-temporal extent.
    
    Guidelines:
    - Spatio-temporal extent means the concept exists in both space and time
    - Physical objects have spatio-temporal extent
    - Abstract concepts do not have spatio-temporal extent
    
    Respond with either:
    - "Yes: [brief justification]" 
    - "No: [brief justification]"
    
    Be certain in your answer as it determines the ontological classification.
    """
    
    answer_extent = call_llm_chain(llm, prompt_extent, concept=concept)
    st.write(f"DEBUG: LLM response (spatio-temporal extent) for '{concept}': {answer_extent}")
    
    if "yes" in answer_extent.lower():
        classification = "Individual"
        st.write(f"DEBUG: Classified '{concept}' as {classification}.")
        graph.add_node(concept, title=f"{concept} ({classification})", 
                      label=f"{concept}\n({classification})",
                      color="#00ff00")  # Green for Individuals
        return  # Individuals don't need further analysis
    
    # --- Step 2: Check if the concept has members (exemplars) ---
    prompt_members = """BORO ANALYSIS: Determine if the concept '{concept}' has members or instances.
    
    Guidelines:
    - Types have members (e.g., "Dog" has members like specific dogs)
    - Tuples represent relationships and do not have members
    - Consider if you can list specific examples of this concept
    
    Respond with either:
    - "Yes: [brief explanation]"
    - "No: [brief explanation]"
    
    Be certain in your answer as it determines the ontological classification.
    """
    
    answer_members = call_llm_chain(llm, prompt_members, concept=concept)
    st.write(f"DEBUG: LLM response (members check) for '{concept}': {answer_members}")
    
    if "yes" in answer_members.lower():
        classification = "Type"
        st.write(f"DEBUG: Classified '{concept}' as {classification}.")
        graph.add_node(concept, title=f"{concept} ({classification})", 
                      label=f"{concept}\n({classification})",
                      color="#0000ff")  # Blue for Types
        
        prompt_exemplars = """BORO ANALYSIS: List exactly 3 concrete exemplar members of the type '{concept}'.
        
        Guidelines:
        - Provide specific, real-world examples
        - Each example should be a distinct instance
        - Use clear, unambiguous names
        - Separate examples with commas
        
        Format your response as: example1, example2, example3
        """
        
        answer_exemplars = call_llm_chain(llm, prompt_exemplars, concept=concept)
        st.write(f"DEBUG: LLM response (exemplar members) for '{concept}': {answer_exemplars}")
        exemplars = [ex.strip() for ex in answer_exemplars.split(',') if ex.strip()]
        
        for exemplar in exemplars[:3]:  # Limit to 3 exemplars to prevent explosion
            if exemplar.lower() not in {v.lower() for v in visited}:
                st.write(f"DEBUG: Adding exemplar '{exemplar}' under type '{concept}'.")
                graph.add_node(exemplar, title=exemplar)
                graph.add_edge(concept, exemplar, title="exemplar")
                boro_analysis(exemplar, graph, visited, depth=depth + 1, max_depth=max_depth)
    else:
        classification = "Tuple"
        st.write(f"DEBUG: Classified '{concept}' as {classification}.")
        graph.add_node(concept, title=f"{concept} ({classification})", 
                      label=f"{concept}\n({classification})",
                      color="#ff0000")  # Red for Tuples
        
        prompt_tuple = """BORO ANALYSIS: For the tuple concept '{concept}', identify exactly 2 main entities involved in the relationship.
        
        Guidelines:
        - List the key entities that participate in this relationship
        - Use clear, unambiguous names
        - Separate entities with commas
        - Limit to 2 main entities for clarity
        
        Format your response as: entity1, entity2
        """
        
        answer_tuple = call_llm_chain(llm, prompt_tuple, concept=concept)
        st.write(f"DEBUG: LLM response (related entities) for '{concept}': {answer_tuple}")
        related_entities = [entity.strip() for entity in answer_tuple.split(',') if entity.strip()]
        
        for entity in related_entities[:2]:  # Limit to 2 related entities to prevent explosion
            if entity.lower() not in {v.lower() for v in visited}:
                st.write(f"DEBUG: Adding related entity '{entity}' under tuple '{concept}'.")
                graph.add_node(entity, title=entity)
                graph.add_edge(concept, entity, title="related")
                boro_analysis(entity, graph, visited, depth=depth + 1, max_depth=max_depth)



def main():
    """
    The main function that initializes the Streamlit interface,
    collects user input, executes the BORO analysis, and renders the PyVis graph.
    """
    st.title("BORO Analysis Decision Tree")
    st.write("This application recursively analyzes a concept using the BORO decision tree methodology "
             "and visualizes the resulting ontology structure.")
    
    concept_input = st.text_input("Enter the concept for analysis:", value="Car")
    
    if st.button("Run BORO Analysis"):
        st.write("DEBUG: Initiating BORO analysis...")
        with st.spinner("Running BORO analysis. Please wait..."):
            # Initialize graph with pixel values instead of percentages
            graph = Network(height="750px", width="1000px", bgcolor="#222222", font_color="white", directed=True)
            visited = set()
            boro_analysis(concept_input, graph, visited)
            st.write("DEBUG: BORO analysis complete. Preparing graph rendering...")
            
            graph.save_graph("graph.html")
            HtmlFile = open("graph.html", "r", encoding="utf-8")
            source_code = HtmlFile.read()
            # Use numeric values for width
            components.html(source_code, height=750, width=1000)

if __name__ == '__main__':
    main()
