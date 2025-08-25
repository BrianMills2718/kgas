# MCP Routing Research Insights

*Research conducted 2025-08-04 - Community insights on handling many tools in MCP agents*

## Executive Summary

The "too many tools" problem in MCP (Model Context Protocol) systems is a well-documented performance issue where agents struggle with tool selection and routing when presented with large numbers of available tools. Performance degradation starts surprisingly early (after just a handful of tools) due to decision paralysis, token bloat, and attention spreading.

## Core Problems Identified

### Performance Degradation Mechanisms

1. **Token Bloat**: Every tool description consumes valuable context window tokens needed for agent reasoning and task memory
2. **Decision Paralysis**: LLMs get confused with too many options and make incorrect tool selections  
3. **Attention Spreading**: Large toolsets spread the LLM's attention thinly between many options
4. **Early Onset**: Decline in tool calling accuracy happens after adding just a handful of tools, not dozens

### Platform-Specific Limits

- **Cursor**: Shows warnings when tools exceed 40 (performance issues noted)
- **VS Code**: 128 tool maximum per chat request ⚠️ *[UNVERIFIED CLAIM - needs validation]*
- **Claude Code**: Currently shows ALL tools to all agents, causing decision paralysis

### Technical Issues

- **Name Conflicts**: When two MCP servers have tools of the same name, routing goes to whichever MCP is first in the list
- **Context Window Crowding**: Detailed tool descriptions crowd context needed for reasoning
- **Agent Confusion**: Smaller/quantized models get tool names and definitions mixed up, hallucinate tools, or ignore tool instructions

## What LLMs Actually See in MCP (Technical Reality)

**Sources**: 
- https://modelcontextprotocol.io/docs/concepts/tools
- https://modelcontextprotocol.io/specification/2025-06-18

### Complete Information Exposure
When LLMs connect to MCP servers via `tools/list`, they receive **comprehensive, detailed information** for each tool:

```json
{
  "name": "get_weather",
  "title": "Weather Information Provider", 
  "description": "Get current weather information for a location",
  "inputSchema": {
    "type": "object",
    "properties": {
      "location": {
        "type": "string",
        "description": "City name or zip code"
      }
    },
    "required": ["location"]
  },
  "annotations": {
    "destructiveHint": false,
    "readOnlyHint": true
  }
}
```

### Information Available to LLMs
- **Tool names**: Unique identifiers
- **Rich descriptions**: Complete explanations of tool purposes
- **Full JSON Schema**: Parameter types, validation rules, constraints
- **Parameter descriptions**: Human-readable explanations for each field
- **Required vs optional fields**: Clear specification of mandatory parameters
- **Output schemas**: Expected response structures (when provided)
- **Behavioral annotations**: Hints about destructive/read-only operations

### Key Insight: Information Is Not the Problem
**LLMs already have excellent information for tool selection.** The issues arise from cognitive load, not lack of detail.

## Community Solutions & Best Practices

### Automated vs Interactive Routing

#### LLM Automation Approaches (No User Interaction)
- **Context-Based Auto-Routing**: Analyze project files, directory, commands, conversation history
- **Hierarchical Tool Selection**: Broad category first, then specific tool within category
- **Multi-Attempt Strategy**: Try most likely tool first, auto-retry with alternatives on failure
- **Tool Capability Matching**: Match request requirements against tool specifications automatically
- **Smart Tool Filtering**: Only expose relevant tools based on current context

#### Interactive Routing (Requires User Input)
- **Clarification Questions**: Ask user to specify when ambiguous (like Router Agent pattern)
- **Explicit Routing Overrides**: Allow "Using [tool], do [task]" manual specification
- **Preference Learning**: Remember user choices for future similar requests

#### Why "Learning" Approaches Are Questionable
- **Marginal gains**: 5-10% improvement for significant infrastructure overhead
- **Complexity mismatch**: Learning adds complexity without addressing core cognitive load issue
- **Information redundancy**: LLMs already have detailed tool descriptions and schemas
- **Pattern matching problems**: Natural language variation makes request matching technically complex
- **Post-MVP feature**: Better suited for systems with 50+ tools, not 8-tool systems

### Tool Selection Strategies

#### Tool Loadout Management
- **Selective Activation**: Only enable tools relevant to the current task
- **Per-conversation Selection**: Some clients support enabling specific MCP tools per conversation  
- **Deactivate Unused Tools**: Simple but effective - turn off what you don't need
- **Tool Budget**: Treat tool count like a budget - be selective about inclusions

#### Context-Aware Selection
- Use project context to determine which tools are relevant
- Dynamic tool activation based on task context
- Smart server selection based on tool chosen by LLM

### Architectural Patterns

#### Gateway Pattern
- **Tool Proxy**: Single service that exposes many tools under one roof
- **Intelligent Routing**: Gateway handles routing and high-level tool selection decisions
- **Policy Enforcement**: Rate limits, logging, audit trails, multi-tenancy support

#### Multi-Agent Architecture  
- **Agent Specialization**: Split agents into specialists with tool subsets
- **Role-Based Visibility**: Each agent type only sees tools relevant to their function
- **Limitation**: Eventually hits new context window limits when mini-agents need to route calls

#### Consolidation Patterns
- **Prompt Macros**: Single prompts that chain multiple tools behind the scenes
- **Meta-Servers**: Tool selector services that act as intelligent proxies
- **Service Abstraction**: Hide complexity of multiple tool calls behind single interfaces

### Error Handling Best Practices

#### Agent-Friendly Design
- Design tools with agent-friendly error messages that help with routing decisions
- Error handling should help the agent decide what to do next, not just flag problems
- Agents often retry with different approaches when something fails

#### Naming Conventions
- Use clear, specific tool names to avoid conflicts
- Descriptive tool descriptions that clearly differentiate purposes
- Consistent naming patterns across related tools

## Current State & Future Directions

### Existing Solutions
- **Manual Curation**: Currently the most effective approach - human tool selection remains superior
- **Tool Filtering**: Basic enable/disable functionality in most platforms
- **Project Templates**: Pre-configured tool sets for common use cases

### Emerging Technologies
- **Meta Servers**: Tool selector proxies claiming to improve performance
- **Intelligent Routing Systems**: AI-powered tool selection based on task analysis
- **Dynamic Tool Activation**: Context-aware tool enabling/disabling
- **Per-Agent Filtering**: Role-based tool visibility (requested feature for Claude Code)
- **Smart Defaults with Learning**: Systems that track tool success rates (questionable ROI for small tool sets)

### Community Consensus
The Reddit and broader development community agrees that:
1. **Manual curation remains most effective** for now
2. **Automated solutions are rapidly developing** but not yet mature
3. **Architectural solutions** (gateways, specialization) show promise
4. **Tool budget management** is critical for performance
5. **Early intervention** is better than trying to fix overcrowded contexts

## Practical Recommendations (Revised Based on Technical Reality)

### Immediate Actions (High ROI)
1. **Improve Tool Descriptions**: LLMs get full descriptions - make them clearer and more distinctive
2. **Context-Based Filtering**: Only expose tools relevant to current conversation/project
3. **Tool Naming Strategy**: Use action-oriented, unambiguous names ("extractPdfEntities" vs "extract")
4. **Reduce Tool Count**: Combine similar functions, eliminate redundant tools

### Medium-Term Strategies (Proven Approaches)
1. **Hierarchical Organization**: Category-based tool grouping instead of flat lists
2. **Agent Specialization**: Role-specific agents with curated tool subsets
3. **Smart Defaults**: Simple rules-based routing ("pdf" → PDF tools) rather than learning
4. **Multi-Attempt Fallbacks**: Auto-retry with alternative tools on failure

### What NOT to Build (Low ROI)
1. **Complex Learning Systems**: Marginal gains for significant overhead
2. **Request Pattern Matching**: Natural language variation makes this technically complex
3. **Usage Analytics**: Better to focus on better tool design
4. **Elaborate Routing Logic**: LLMs already have good information for decisions

### Long-Term Vision
1. **Intelligent Meta-Servers**: AI-powered tool selection and routing systems
2. **Dynamic Context Management**: Automatic tool activation based on conversation flow
3. **Performance Optimization**: Research into how different models handle tool selection
4. **Standards Development**: Community standards for tool naming and organization
5. **Better Tool Design**: Focus on fewer, better-described tools rather than complex routing

## Research Sources

- Reddit communities: /r/MachineLearning, /r/LocalLLaMA, /r/ClaudeAI
- Industry blogs: Speakeasy, Jentic, Docker, Microsoft Learn
- GitHub issues: Anthropic Claude Code, Cursor Community Forum
- **MCP Official Documentation**: https://modelcontextprotocol.io/docs/concepts/tools
- **MCP Technical Specification**: https://modelcontextprotocol.io/specification/2025-06-18

## Next Steps for KGAS Implementation

Given our current system has 8 tools and plans for expansion:

### MVP Phase (Focus on Simplicity)
1. **Immediate**: Improve existing tool descriptions for clarity and distinctiveness
2. **Phase 1**: Implement context-based tool filtering (only show relevant tools)
3. **Phase 2**: Create hierarchical tool organization (processing → analysis → output)
4. **Phase 3**: Add simple fallback strategies for tool failures

### Post-MVP Phase (If Tool Count Exceeds 20+)
1. **Meta-Server Patterns**: Gateway-style tool routing for complex workflows
2. **Advanced Context Analysis**: File type, project structure, conversation history
3. **Dynamic Tool Loading**: Load/unload tools based on active context
4. **Performance Monitoring**: Track tool selection accuracy (not usage patterns)

### Experimental Validation Needed
- [ ] **VS Code 128-tool limit**: Test actual VS Code MCP integration tool limits (may be specific to VS Code's direct MCP chat features, not IDE usage)
- [ ] **Cursor 40-tool warning threshold**: Verify when warnings actually appear
- [ ] **"Handful of tools" degradation**: Test with GPT-3.5, GPT-4 base models to validate community claims
- [ ] **Token bloat impact**: Measure actual context window usage with tool descriptions

## Key Insight: Focus on Tool Quality, Not Routing Complexity

The research reveals that **LLMs already receive comprehensive tool information** through MCP. The problem isn't information quality - it's information overload. Rather than building complex routing systems, focus on:

1. **Fewer, better tools** with clear, distinctive purposes
2. **Context-based filtering** to reduce cognitive load
3. **Hierarchical organization** rather than flat tool lists
4. **Simple fallback strategies** instead of predictive routing

This approach avoids the technical complexity of learning systems while addressing the actual root cause: too many simultaneous choices for the LLM to process effectively.