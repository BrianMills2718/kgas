# Universal Model Tester

A comprehensive testing framework for all major LLM providers with automatic fallback handling and structured output support.

## Features

- **Universal Model Support**: Gemini, OpenAI (GPT-4.1, o4-mini, o3), and Anthropic (Claude Opus 4, Sonnet 4, Sonnet 3.7, Haiku 3.5)
- **Automatic Fallbacks**: Intelligent fallback sequences based on configurable trigger conditions
- **Structured Output**: Native JSON schema support where available, prompt injection fallback for others
- **Environment Configuration**: All models, API keys, and fallback conditions configured via `.env`
- **Comprehensive Testing**: Full test suite with detailed reporting

## Quick Start

1. **Configure Environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and model preferences
   ```

2. **Basic Usage**:
   ```python
   from universal_model_client import UniversalModelClient
   
   client = UniversalModelClient()
   
   # Simple completion with fallbacks
   result = client.complete(
       messages=[{"role": "user", "content": "Hello!"}]
   )
   
   # Structured output with schema
   schema = {
       "type": "object",
       "properties": {
           "name": {"type": "string"},
           "age": {"type": "integer"}
       },
       "required": ["name", "age"],
       "additionalProperties": False
   }
   
   result = client.complete(
       messages=[{"role": "user", "content": "Create a character"}],
       schema=schema
   )
   ```

3. **Run Comprehensive Tests**:
   ```bash
   python test_all_models.py
   ```

## Configuration

### Environment Variables

```bash
# API Keys
OPENAI_API_KEY=your_key_here
GEMINI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here

# Primary Model and Fallbacks
PRIMARY_MODEL=gemini-2.5-flash
FALLBACK_MODEL_1=o4-mini
FALLBACK_MODEL_2=claude-sonnet-4-20250514

# Fallback Triggers
FALLBACK_ON_RATE_LIMIT=true
FALLBACK_ON_TIMEOUT=true
FALLBACK_ON_ERROR=true
TIMEOUT_SECONDS=30
```

### Model Configurations

Each model is configured with:
- **LiteLLM Model Name**: Exact name for LiteLLM calls
- **Structured Output Support**: Whether native JSON schema is supported
- **Max Tokens**: Maximum token limit for the model

```bash
# Format: MODEL_NAME=litellm_name,supports_structured_output,max_tokens
GEMINI_2_5_FLASH=gemini/gemini-2.5-flash,true,8192
O4_MINI=o4-mini,false,16384
CLAUDE_SONNET_4=claude-sonnet-4-20250514,true,4096
```

## Supported Models

### Gemini Models
- **gemini-2.5-pro**: Enhanced reasoning, multimodal
- **gemini-2.5-flash**: Adaptive thinking, cost efficient  
- **gemini-2.5-flash-lite**: Most cost-efficient, high throughput

### OpenAI Models
- **gpt-4.1**: Flagship GPT model for complex tasks
- **o4-mini**: Faster, affordable reasoning model
- **o3**: Most powerful reasoning model

### Anthropic Models  
- **claude-opus-4**: Latest Opus model
- **claude-sonnet-4**: Latest Sonnet model
- **claude-3-7-sonnet**: Sonnet 3.7 variant
- **claude-3-5-haiku**: Latest Haiku model

## Structured Output Support

### Native Support (JSON Schema)
Models with native structured output support use OpenAI's JSON Schema format:

```python
response_format = {
    "type": "json_schema",
    "json_schema": {
        "name": "schema_name",
        "schema": your_schema,
        "strict": True
    }
}
```

**Supported Models**: Gemini 2.5 series, GPT-4.1, o3, All Claude models

### Fallback Support (Prompt Injection)
Models without native support get the schema injected into the prompt:

```python
# Schema automatically added to prompt
"Please format your response as JSON matching this schema: {...}"
response_format = {"type": "json_object"}
```

**Fallback Models**: o4-mini

## Fallback System

### Trigger Conditions
- **Rate Limit**: HTTP 429 errors
- **Timeout**: Request timeouts
- **Token Limit**: Context length exceeded
- **General Error**: Any other error

### Fallback Sequence
1. **Primary Model**: Configured via `PRIMARY_MODEL`
2. **Fallback 1**: Configured via `FALLBACK_MODEL_1` 
3. **Fallback 2**: Configured via `FALLBACK_MODEL_2`

### Example Flow
```
gemini-2.5-flash → o4-mini → claude-sonnet-4-20250514
     (timeout)      (success)
```

## Testing

### Individual Model Testing
Test specific models with all schema types:

```python
python test_all_models.py
```

### Custom Testing
```python
from universal_model_client import UniversalModelClient, TriggerCondition

client = UniversalModelClient()

result = client.complete(
    messages=[{"role": "user", "content": "Test message"}],
    model="gemini-2.5-pro",
    fallback_models=["o4-mini", "claude-sonnet-4-20250514"],
    trigger_conditions=[TriggerCondition.RATE_LIMIT, TriggerCondition.TIMEOUT]
)
```

### Test Report
The comprehensive test generates:
- **Success rate by model**
- **Success rate by test case**  
- **Structured output support matrix**
- **Fallback sequence validation**
- **Failed test details**

## Advanced Usage

### Custom Schemas
Define complex nested schemas:

```python
complex_schema = {
    "type": "object",
    "properties": {
        "analysis": {
            "type": "object", 
            "properties": {
                "summary": {"type": "string"},
                "confidence": {"type": "number", "minimum": 0, "maximum": 1}
            }
        },
        "recommendations": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "action": {"type": "string"},
                    "priority": {"type": "string", "enum": ["high", "medium", "low"]}
                }
            }
        }
    },
    "required": ["analysis", "recommendations"],
    "additionalProperties": False
}
```

### Response Analysis
```python
result = client.complete(messages=messages, schema=schema)

print(f"Model used: {result['model_used']}")
print(f"Total attempts: {result['total_attempts']}")  
print(f"Native structured output: {result['structured_output_native']}")
print(f"Response: {result['response'].choices[0].message.content}")
```

## Error Handling

The client handles:
- **API key errors**
- **Rate limiting** 
- **Timeouts**
- **Model availability**
- **Invalid schemas**
- **JSON parsing errors**

All errors are logged and detailed in the response metadata.

## Files

- **`universal_model_client.py`**: Main client with fallback logic
- **`test_all_models.py`**: Comprehensive test suite
- **`.env`**: Configuration file with API keys and settings
- **`.env.example`**: Template configuration file
- **`README.md`**: This documentation