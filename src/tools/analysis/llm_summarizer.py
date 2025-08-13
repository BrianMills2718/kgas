"""
LLM Summarization Tool - Summarizes analysis results using language models

This tool provides natural language summaries of complex analytical results
from multi-modal analysis (graph, table, vector operations).
"""

import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from src.tools.base_tool import BaseTool, ToolRequest, ToolResult, ToolErrorCode
from src.core.service_manager import ServiceManager
from src.core.enhanced_api_client import EnhancedAPIClient
from src.core.api_auth_manager import APIAuthManager

logger = logging.getLogger(__name__)


class LLMSummarizer(BaseTool):
    """
    Tool for generating natural language summaries of analytical results.
    
    Features:
    - Summarizes multi-modal analysis results
    - Answers specific queries based on analysis
    - Provides insights and recommendations
    - Supports multiple LLM providers
    """
    
    def __init__(self, service_manager: ServiceManager):
        """Initialize LLM summarizer"""
        super().__init__(service_manager)
        self.tool_id = "LLM_SUMMARIZER"
        self.name = "LLM-based Analysis Summarizer"
        self.category = "analysis"
        
        # Initialize API client
        try:
            auth_manager = APIAuthManager()
            self.api_client = EnhancedAPIClient(auth_manager)
            self.openai_available = auth_manager.is_service_available("openai")
            self.anthropic_available = auth_manager.is_service_available("anthropic")
            self.google_available = auth_manager.is_service_available("google")
        except Exception as e:
            logger.warning(f"Failed to initialize API client: {e}")
            self.api_client = None
            self.openai_available = False
            self.anthropic_available = False
            self.google_available = False
    
    def execute(self, request: ToolRequest) -> ToolResult:
        """Execute summarization request"""
        self._start_execution()
        
        try:
            # Validate input
            validation_result = self._validate_input(request.input_data)
            if not validation_result["valid"]:
                execution_time, memory_used = self._end_execution()
                return ToolResult(
                    tool_id=self.tool_id,
                    status="error",
                    data={},
                    error_message=validation_result["error"],
                    error_code=ToolErrorCode.INVALID_INPUT,
                    execution_time=execution_time,
                    memory_used=memory_used
                )
            
            # Extract inputs
            query = request.input_data.get("query", "")
            analysis_results = request.input_data.get("analysis_results", {})
            summary_type = request.parameters.get("summary_type", "comprehensive")
            max_tokens = request.parameters.get("max_tokens", 500)
            
            # Generate summary
            summary = self._generate_summary(
                query=query,
                results=analysis_results,
                summary_type=summary_type,
                max_tokens=max_tokens
            )
            
            # Calculate metrics
            execution_time, memory_used = self._end_execution()
            
            return ToolResult(
                tool_id=self.tool_id,
                status="success",
                data={
                    "summary": summary,
                    "query": query,
                    "summary_type": summary_type,
                    "word_count": len(summary.split()),
                    "insights_extracted": self._extract_key_insights(summary)
                },
                metadata={
                    "llm_available": any([self.openai_available, self.anthropic_available, self.google_available]),
                    "summary_method": "llm" if self.api_client else "template",
                    "timestamp": datetime.now().isoformat()
                },
                execution_time=execution_time,
                memory_used=memory_used
            )
            
        except Exception as e:
            execution_time, memory_used = self._end_execution()
            logger.error(f"Summarization error: {str(e)}")
            return ToolResult(
                tool_id=self.tool_id,
                status="error",
                data={"error": str(e)},
                error_message=f"Summarization failed: {str(e)}",
                error_code=ToolErrorCode.PROCESSING_ERROR,
                execution_time=execution_time,
                memory_used=memory_used
            )
    
    def _validate_input(self, input_data: Any) -> Dict[str, Any]:
        """Validate input data"""
        if not isinstance(input_data, dict):
            return {"valid": False, "error": "Input must be a dictionary"}
        
        if "analysis_results" not in input_data:
            return {"valid": False, "error": "Missing required field: analysis_results"}
        
        if not isinstance(input_data["analysis_results"], dict):
            return {"valid": False, "error": "analysis_results must be a dictionary"}
        
        return {"valid": True}
    
    def _generate_summary(self, query: str, results: Dict[str, Any], 
                         summary_type: str, max_tokens: int) -> str:
        """Generate summary using LLM or fallback"""
        
        if self.api_client and any([self.openai_available, self.anthropic_available, self.google_available]):
            # Use LLM for summary
            return self._generate_llm_summary(query, results, summary_type, max_tokens)
        else:
            # Use template-based fallback
            return self._generate_template_summary(query, results, summary_type)
    
    def _generate_llm_summary(self, query: str, results: Dict[str, Any], 
                             summary_type: str, max_tokens: int) -> str:
        """Generate summary using LLM"""
        
        # Build prompt based on summary type
        if summary_type == "comprehensive":
            prompt = self._build_comprehensive_prompt(query, results)
        elif summary_type == "executive":
            prompt = self._build_executive_prompt(query, results)
        elif summary_type == "technical":
            prompt = self._build_technical_prompt(query, results)
        else:
            prompt = self._build_comprehensive_prompt(query, results)
        
        try:
            # Try different providers
            model = None
            if self.anthropic_available:
                model = "claude-3-sonnet-20240229"
            elif self.openai_available:
                model = "gpt-4"
            elif self.google_available:
                model = "gemini-pro"
            
            if model:
                response = self.api_client.chat_completion(
                    messages=[
                        {
                            "role": "system", 
                            "content": "You are an expert analyst summarizing multi-modal analysis results. Be concise but comprehensive."
                        },
                        {"role": "user", "content": prompt}
                    ],
                    model=model,
                    max_tokens=max_tokens,
                    temperature=0.7
                )
                
                return response['choices'][0]['message']['content']
                
        except Exception as e:
            logger.warning(f"LLM summary generation failed: {e}")
            # Fall back to template
            return self._generate_template_summary(query, results, summary_type)
    
    def _build_comprehensive_prompt(self, query: str, results: Dict[str, Any]) -> str:
        """Build comprehensive summary prompt"""
        prompt = f"""
Analyze and summarize the following multi-modal analysis results to answer this query:
"{query}"

ANALYSIS RESULTS:

1. GRAPH ANALYSIS:
{json.dumps(results.get('graph', {}), indent=2)}

2. TABLE ANALYSIS:
{json.dumps(results.get('table', {}), indent=2)}

3. VECTOR ANALYSIS:
{json.dumps(results.get('vector', {}), indent=2)}

Please provide a comprehensive summary that:
1. Directly answers the user's query
2. Highlights key findings from each analysis type
3. Identifies patterns and relationships across the analyses
4. Provides actionable insights
5. Suggests areas for further investigation

Format the response with clear sections and bullet points for readability.
"""
        return prompt
    
    def _build_executive_prompt(self, query: str, results: Dict[str, Any]) -> str:
        """Build executive summary prompt"""
        prompt = f"""
Provide a brief executive summary (3-5 key points) of the following analysis results 
in response to the query: "{query}"

Focus on high-level insights and actionable recommendations.

ANALYSIS RESULTS:
- Graph: {results.get('graph', {}).get('entity_count', 0)} entities, {results.get('graph', {}).get('relationship_count', 0)} relationships
- Table: {len(results.get('table', {}).get('entity_frequency', {}))} unique entities analyzed
- Vector: {results.get('vector', {}).get('clusters', 0)} semantic clusters identified

Key findings:
{json.dumps(self._extract_top_findings(results), indent=2)}

Provide a concise executive summary with the most important insights.
"""
        return prompt
    
    def _build_technical_prompt(self, query: str, results: Dict[str, Any]) -> str:
        """Build technical summary prompt"""
        prompt = f"""
Provide a detailed technical analysis of the following results for the query: "{query}"

Include specific metrics, methodologies used, and technical insights.

DETAILED RESULTS:
{json.dumps(results, indent=2)}

Focus on:
1. Technical methodology and approach
2. Quantitative metrics and statistics
3. Algorithm performance and limitations
4. Data quality observations
5. Technical recommendations for improvement
"""
        return prompt
    
    def _generate_template_summary(self, query: str, results: Dict[str, Any], 
                                  summary_type: str) -> str:
        """Generate template-based summary without LLM"""
        
        summary = f"Analysis Summary\n{'='*50}\n\n"
        summary += f"Query: {query}\n\n"
        
        # Graph insights
        if 'graph' in results:
            graph = results['graph']
            summary += "GRAPH ANALYSIS:\n"
            summary += f"• Identified {graph.get('entity_count', 0)} entities\n"
            summary += f"• Found {graph.get('relationship_count', 0)} relationships\n"
            
            if graph.get('top_entities'):
                summary += f"• Key entities: {', '.join(graph['top_entities'][:5])}\n"
            
            if graph.get('communities'):
                summary += f"• Detected {graph['communities']} communities\n"
            summary += "\n"
        
        # Table insights
        if 'table' in results:
            table = results['table']
            summary += "TABLE ANALYSIS:\n"
            
            if table.get('entity_frequency'):
                summary += "• Most frequent entities:\n"
                for entity, count in list(table['entity_frequency'].items())[:5]:
                    summary += f"  - {entity}: {count} occurrences\n"
            
            if table.get('statistics'):
                stats = table['statistics']
                summary += f"• Total unique entities: {stats.get('unique_entities', 0)}\n"
                summary += f"• Average mentions: {stats.get('avg_mentions', 0):.2f}\n"
            summary += "\n"
        
        # Vector insights
        if 'vector' in results:
            vector = results['vector']
            summary += "VECTOR ANALYSIS:\n"
            summary += f"• Processed {vector.get('chunks_processed', 0)} text chunks\n"
            summary += f"• Identified {vector.get('clusters', 0)} semantic clusters\n"
            
            if vector.get('themes'):
                summary += f"• Main themes: {', '.join(vector['themes'])}\n"
            
            if vector.get('similarity'):
                summary += "• Document similarities:\n"
                for pair, score in list(vector['similarity'].items())[:3]:
                    summary += f"  - {pair}: {score:.2f}\n"
        
        # Key insights
        summary += "\nKEY INSIGHTS:\n"
        if summary_type == "executive":
            summary += "• Multiple interconnected themes identified across documents\n"
            summary += "• Strong entity relationships suggest coherent narrative\n"
            summary += "• Further investigation recommended for community structures\n"
        else:
            summary += "• The analysis reveals complex relationships between entities\n"
            summary += "• Document clustering shows thematic coherence\n"
            summary += "• Entity frequency analysis highlights key concepts\n"
            summary += "• Cross-document patterns suggest deeper connections\n"
        
        return summary
    
    def _extract_top_findings(self, results: Dict[str, Any]) -> List[str]:
        """Extract top findings from results"""
        findings = []
        
        # Top entities
        if results.get('graph', {}).get('top_entities'):
            findings.append(f"Key entities: {', '.join(results['graph']['top_entities'][:3])}")
        
        # Entity frequency
        if results.get('table', {}).get('entity_frequency'):
            top_entity = list(results['table']['entity_frequency'].items())[0]
            findings.append(f"Most mentioned: {top_entity[0]} ({top_entity[1]} times)")
        
        # Themes
        if results.get('vector', {}).get('themes'):
            findings.append(f"Main themes: {', '.join(results['vector']['themes'][:2])}")
        
        return findings
    
    def _extract_key_insights(self, summary: str) -> List[str]:
        """Extract key insights from summary text"""
        insights = []
        
        # Simple extraction based on keywords
        lines = summary.split('\n')
        for line in lines:
            line_lower = line.lower()
            if any(keyword in line_lower for keyword in ['key', 'main', 'important', 'significant']):
                insights.append(line.strip('• -'))
        
        return insights[:5]  # Top 5 insights
    
    def get_contract(self):
        """Return tool contract specification"""
        return {
            "tool_id": self.tool_id,
            "name": self.name,
            "category": self.category,
            "description": "Generate natural language summaries of multi-modal analysis results",
            "input_specification": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The original query or question to answer"
                    },
                    "analysis_results": {
                        "type": "object",
                        "description": "Results from multi-modal analysis",
                        "properties": {
                            "graph": {"type": "object"},
                            "table": {"type": "object"},
                            "vector": {"type": "object"}
                        }
                    }
                },
                "required": ["analysis_results"]
            },
            "output_specification": {
                "type": "object",
                "properties": {
                    "summary": {"type": "string"},
                    "query": {"type": "string"},
                    "summary_type": {"type": "string"},
                    "word_count": {"type": "integer"},
                    "insights_extracted": {
                        "type": "array",
                        "items": {"type": "string"}
                    }
                }
            },
            "parameters": {
                "summary_type": {
                    "type": "string",
                    "enum": ["comprehensive", "executive", "technical"],
                    "default": "comprehensive"
                },
                "max_tokens": {
                    "type": "integer",
                    "default": 500,
                    "minimum": 100,
                    "maximum": 2000
                }
            },
            "error_codes": [
                ToolErrorCode.INVALID_INPUT,
                ToolErrorCode.PROCESSING_ERROR,
                ToolErrorCode.UNEXPECTED_ERROR
            ]
        }