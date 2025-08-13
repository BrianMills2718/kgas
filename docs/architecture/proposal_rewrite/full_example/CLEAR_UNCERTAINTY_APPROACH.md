# Clear Uncertainty Approach - No More Circles

## Core Decisions (Final)

### 1. Uncertainty is ALWAYS part of tool output
```python
class ToolResult(BaseModel):
    """Every tool returns this"""
    data: Dict[str, Any]  # The actual results
    uncertainty: UniversalUncertainty  # Always included
    metadata: Dict[str, Any]  # Execution stats, etc.
```

**NOT** separate API calls, **NOT** post-hoc assessment.

### 2. Tools assess their own uncertainty
```python
class AnyTool(KGASTool):
    def execute(self, request: ToolRequest) -> ToolResult:
        # Do the work
        results = self.do_calculation(request.input_data)
        
        # Assess uncertainty as part of execution
        uncertainty = self.assess_uncertainty(results, request)
        
        return ToolResult(
            data=results,
            uncertainty=uncertainty,
            metadata={"stats": self.execution_stats}
        )
```

### 3. Theory extraction follows meta-schema
The T302_THEORY_EXTRACTION tool outputs an instance of the meta-schema v13:

```python
theory_instance = {
    "theory_id": "self_categorization_theory",
    "theory_name": "Self-Categorization Theory",
    "version": "1.0.0",
    "metadata": {
        "authors": ["Turner", "Oakes"],
        "publication_year": 1986,
        ...
    },
    "algorithms": {
        "mathematical": [{
            "name": "meta_contrast_ratio",
            "formula": "MCR = Σ|x_i - x_outgroup| / Σ|x_i - x_ingroup|",
            ...
        }]
    },
    ...
}

# Tool returns this WITH uncertainty
return ToolResult(
    data={"theory_schema": theory_instance},
    uncertainty=UniversalUncertainty(
        uncertainty=0.15,
        reasoning="Core formula clear, some procedural details require interpretation"
    ),
    metadata={"source": "Turner_1986.pdf", "pages": 47}
)
```

### 4. Should uncertainty be IN the meta-schema?

**NO** - The meta-schema defines the THEORY structure. Uncertainty is about the EXTRACTION process.

The theory schema is timeless (SCT is what it is). The uncertainty is about our extraction/implementation of it.

## Example: How it ACTUALLY works

### Step 1: Theory Extraction
```python
# T302_THEORY_EXTRACTION
def execute(self, request):
    pdf_path = request.input_data["pdf_path"]
    
    # Extract theory into meta-schema format
    theory_text = extract_text(pdf_path)
    theory_instance = llm_extract_to_schema(theory_text, THEORY_META_SCHEMA_V13)
    
    # Assess extraction uncertainty
    uncertainty = UniversalUncertainty(
        uncertainty=0.15,
        reasoning="Formula explicit, normative fit details sparse"
    )
    
    return ToolResult(
        data={"theory_schema": theory_instance},
        uncertainty=uncertainty,
        metadata={"pages_processed": 47}
    )
```

### Step 2: Data Loading
```python
# T05_CSV_LOAD
def execute(self, request):
    csv_path = request.input_data["csv_path"]
    
    # Load data
    df = pd.read_csv(csv_path)
    valid_rows = df.dropna()
    
    # Assess based on actual loading results
    coverage = len(valid_rows) / len(df)
    uncertainty = UniversalUncertainty(
        uncertainty=0.08,
        reasoning=f"CSV loaded successfully, {coverage:.0%} complete rows",
        data_coverage=coverage
    )
    
    return ToolResult(
        data={"dataframe": df.to_dict()},
        uncertainty=uncertainty,
        metadata={"total_rows": len(df), "valid_rows": len(valid_rows)}
    )
```

### Step 3: Dynamic Tool Generation (e.g., MCR)
```python
# Generate tool FROM theory schema
def generate_mcr_tool(theory_schema):
    mcr_spec = theory_schema["algorithms"]["mathematical"][0]  # MCR formula
    
    generated_code = f'''
class GeneratedMCRTool(KGASTool):
    def execute(self, request):
        # Implementation of {mcr_spec["formula"]}
        results = self.calculate_mcr(request.input_data)
        
        # Self-assess based on runtime
        processed = results["processed_count"]
        total = results["total_count"]
        coverage = processed / total
        
        if coverage > 0.8:
            uncertainty = UniversalUncertainty(
                uncertainty=0.15,
                reasoning=f"High coverage {{coverage:.0%}} for MCR",
                data_coverage=coverage
            )
        else:
            uncertainty = UniversalUncertainty(
                uncertainty=0.30,
                reasoning=f"Limited coverage {{coverage:.0%}} for MCR",
                data_coverage=coverage
            )
        
        return ToolResult(
            data=results,
            uncertainty=uncertainty,
            metadata={{"formula": "{mcr_spec["formula"]}"}}
        )
    '''
    
    return compile_tool(generated_code)
```

## The Pattern is Simple

1. **Every tool** returns `ToolResult` with `uncertainty` field
2. **Tools assess themselves** during execution (not separate)
3. **Generated tools** include self-assessment logic
4. **Theory schemas** don't contain uncertainty (that's about extraction, not the theory)

## Stop Going in Circles

This is the approach. It's in the OVERVIEW.md under "Pattern 2: Self-Assessment in Generated Tools" but we keep forgetting to follow it consistently.

**Key principle**: Uncertainty assessment happens INSIDE tools during execution, using the actual runtime data available at that moment.