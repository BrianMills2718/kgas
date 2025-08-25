#!/usr/bin/env python3
"""
Test the Extensible Framework - Show how easy it is to add tools
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from framework import ToolFramework, ExtensibleTool, ToolCapabilities, ToolResult
from data_types import DataType, DataSchema
from semantic_types import SemanticType, SemanticContext, Domain
from data_references import ProcessingStrategy
from tool_context import ToolContext


# ============================================================
# EXAMPLE 1: Adding a simple tool
# ============================================================

class SimpleWordCounter(ExtensibleTool):
    """Dead simple tool - count words"""
    
    def get_capabilities(self) -> ToolCapabilities:
        return ToolCapabilities(
            tool_id="WordCounter",
            name="Word Counter",
            description="Count words in text",
            input_type=DataType.TEXT,
            output_type=DataType.METRICS
        )
    
    def process(self, input_data, context=None):
        if hasattr(input_data, 'content'):
            text = input_data.content
        else:
            text = str(input_data)
        
        word_count = len(text.split())
        
        result = DataSchema.Metrics(
            values={"word_count": word_count},
            units={"word_count": "words"}
        )
        
        return ToolResult(success=True, data=result)


# ============================================================
# EXAMPLE 2: Domain-specific tool with semantic types
# ============================================================

class FinancialSentimentAnalyzer(ExtensibleTool):
    """Financial domain tool with semantic awareness"""
    
    def get_capabilities(self) -> ToolCapabilities:
        return ToolCapabilities(
            tool_id="FinancialSentiment",
            name="Financial Sentiment Analyzer",
            description="Analyze sentiment in financial text",
            input_type=DataType.TEXT,
            output_type=DataType.METRICS,
            semantic_input=SemanticType(
                base_type="TEXT",
                semantic_tag="financial_reports",
                context=SemanticContext(domain=Domain.FINANCIAL)
            ),
            semantic_output=SemanticType(
                base_type="METRICS",
                semantic_tag="financial_sentiment",
                context=SemanticContext(
                    domain=Domain.FINANCIAL,
                    metadata={"metrics": ["bullish", "bearish", "neutral"]}
                )
            )
        )
    
    def process(self, input_data, context=None):
        # Mock sentiment analysis
        sentiment_scores = {
            "bullish": 0.3,
            "bearish": 0.2,
            "neutral": 0.5
        }
        
        result = DataSchema.Metrics(
            values=sentiment_scores,
            units={k: "probability" for k in sentiment_scores}
        )
        
        return ToolResult(success=True, data=result)


# ============================================================
# EXAMPLE 3: Tool that uses context for configuration
# ============================================================

class ConfigurableEntityExtractor(ExtensibleTool):
    """Entity extractor that uses context for configuration"""
    
    def get_capabilities(self) -> ToolCapabilities:
        return ToolCapabilities(
            tool_id="ConfigurableExtractor",
            name="Configurable Entity Extractor",
            description="Extract entities based on context configuration",
            input_type=DataType.TEXT,
            output_type=DataType.ENTITIES,
            required_params=["entity_types", "confidence_threshold"],
            optional_params=["use_context_window", "max_entities"],
            accepts_context=True
        )
    
    def process(self, input_data, context=None):
        # Get configuration from context
        if context:
            entity_types = context.get_param(self.get_capabilities().tool_id, "entity_types", ["PERSON", "ORG"])
            confidence_threshold = context.get_param(self.get_capabilities().tool_id, "confidence_threshold", 0.5)
            max_entities = context.get_param(self.get_capabilities().tool_id, "max_entities", 100)
        else:
            entity_types = ["PERSON", "ORG"]
            confidence_threshold = 0.5
            max_entities = 100
        
        print(f"      Using entity types: {entity_types}")
        print(f"      Confidence threshold: {confidence_threshold}")
        
        # Mock extraction
        from datetime import datetime
        entities = []
        for i, etype in enumerate(entity_types[:3]):  # Mock: just create a few
            entities.append(DataSchema.Entity(
                id=f"e{i}",
                text=f"Sample {etype}",
                type=etype,
                confidence=0.7 + i * 0.1
            ))
        
        result = DataSchema.EntitiesData(
            entities=entities,
            source_checksum="test_checksum",
            extraction_model="configurable_extractor",
            extraction_timestamp=datetime.now().isoformat()
        )
        
        return ToolResult(success=True, data=result)


# ============================================================
# EXAMPLE 4: Tool with memory management
# ============================================================

class LargeFileProcessor(ExtensibleTool):
    """Tool that handles large files efficiently"""
    
    def get_capabilities(self) -> ToolCapabilities:
        return ToolCapabilities(
            tool_id="LargeFileProcessor",
            name="Large File Processor",
            description="Process large files using streaming",
            input_type=DataType.FILE,
            output_type=DataType.TEXT,
            processing_strategy=ProcessingStrategy.STREAMING,
            max_input_size=10 * 1024 * 1024 * 1024,  # 10GB
            supports_streaming=True
        )
    
    def process(self, input_data, context=None):
        # Would use streaming/memory mapping for large files
        print(f"      Processing file: {input_data.path if hasattr(input_data, 'path') else 'unknown'}")
        print(f"      Using streaming strategy for efficiency")
        
        # Mock result
        result = DataSchema.TextData(
            content="Processed content from large file",
            source=input_data.path if hasattr(input_data, 'path') else "unknown",
            char_count=100,
            line_count=10
        )
        
        return ToolResult(success=True, data=result)


# ============================================================
# MAIN: Demonstrate the extensible framework
# ============================================================

def main():
    print("="*60)
    print("EXTENSIBLE FRAMEWORK DEMONSTRATION")
    print("="*60)
    print("\nShowing how easy it is to add tools to the framework\n")
    
    # Create framework
    framework = ToolFramework()
    
    # ========== Add tools with one line each ==========
    print("📦 REGISTERING TOOLS:")
    print("-" * 40)
    
    framework.register_tool(SimpleWordCounter())
    framework.register_tool(FinancialSentimentAnalyzer())
    framework.register_tool(ConfigurableEntityExtractor())
    framework.register_tool(LargeFileProcessor())
    
    # ========== Framework automatically discovers chains ==========
    print("\n🔍 AUTOMATIC CHAIN DISCOVERY:")
    print("-" * 40)
    
    # Find text processing chains
    print("\n1. Text → Metrics chains:")
    chains = framework.find_chains(DataType.TEXT, DataType.METRICS)
    for chain in chains:
        print(f"   • {' → '.join(chain)}")
    
    # Find entity extraction chains
    print("\n2. Text → Entities chains:")
    chains = framework.find_chains(DataType.TEXT, DataType.ENTITIES)
    for chain in chains:
        print(f"   • {' → '.join(chain)}")
    
    # Find financial-specific chains
    print("\n3. Financial domain chains (TEXT → METRICS):")
    chains = framework.find_chains(DataType.TEXT, DataType.METRICS, domain=Domain.FINANCIAL)
    for chain in chains:
        caps = framework.capabilities[chain[0]]
        if caps.semantic_input and caps.semantic_input.context.domain == Domain.FINANCIAL:
            print(f"   • {' → '.join(chain)} [FINANCIAL]")
    
    # ========== Execute a chain with context ==========
    print("\n⚡ EXECUTING CHAIN WITH CONTEXT:")
    print("-" * 40)
    
    # Create context with configuration
    context = ToolContext()
    context.set_param("ConfigurableExtractor", "entity_types", ["COMPANY", "PRODUCT", "MONEY"])
    context.set_param("ConfigurableExtractor", "confidence_threshold", 0.8)
    
    # Create test data
    test_text = DataSchema.TextData(
        content="Apple Inc. released the iPhone 15 for $999.",
        source="test",
        char_count=44,
        line_count=1,
        checksum="test_checksum_12345"
    )
    
    # Execute chain
    chain = ["ConfigurableExtractor"]
    print(f"\nExecuting: {' → '.join(chain)}")
    result = framework.execute_chain(chain, test_text, context)
    
    if result.success:
        print(f"\n✅ Chain executed successfully!")
        if hasattr(result.data, 'entities'):
            print(f"   Extracted {len(result.data.entities)} entities:")
            for entity in result.data.entities:
                print(f"     - {entity.text} ({entity.type})")
    
    # ========== Show memory-aware chain selection ==========
    print("\n💾 MEMORY-AWARE CHAIN SELECTION:")
    print("-" * 40)
    
    # Find chains that can handle large files
    print("\nChains for processing large files (FILE → TEXT):")
    chains = framework.find_chains(DataType.FILE, DataType.TEXT)
    for chain in chains:
        tool_caps = framework.capabilities[chain[0]]
        if tool_caps.supports_streaming:
            print(f"   • {chain[0]} [STREAMING - up to {tool_caps.max_input_size / (1024**3):.1f}GB]")
        else:
            print(f"   • {chain[0]} [MEMORY - max {tool_caps.max_input_size / (1024**2):.1f}MB]")
    
    # ========== Show how to add existing tools ==========
    print("\n🔧 ADDING EXISTING TOOLS:")
    print("-" * 40)
    
    # Could add existing tools from the codebase
    # framework.add_tool_simple(TextLoader)
    # framework.add_tool_simple(EntityExtractor, semantic_output=MEDICAL_ENTITIES)
    # framework.add_tool_simple(GraphBuilder)
    
    print("\nExisting tools can be added with one line:")
    print("   framework.add_tool_simple(TextLoader)")
    print("   framework.add_tool_simple(EntityExtractor, semantic_output=MEDICAL_ENTITIES)")
    print("   framework.add_tool_simple(GraphBuilder)")
    
    # ========== Summary ==========
    print("\n" + "="*60)
    print("FRAMEWORK CAPABILITIES DEMONSTRATED:")
    print("="*60)
    print("✅ Tools registered with single line")
    print("✅ Automatic chain discovery based on types")
    print("✅ Semantic domain filtering (Financial)")
    print("✅ Context-based configuration")
    print("✅ Memory-aware processing strategies")
    print("✅ Easy integration of existing tools")
    print("\n🎯 This is an EXTENSIBLE FRAMEWORK where tools can be")
    print("   modularly chained together for flexible workflows!")


if __name__ == "__main__":
    main()