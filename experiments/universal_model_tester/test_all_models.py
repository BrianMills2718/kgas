#!/usr/bin/env python3
"""
Test All Models with Structured Output
Comprehensive testing of all model variants with fallback sequences
"""

import json
import logging
from universal_model_client import UniversalModelClient

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Define test schemas
SCHEMAS = {
    "character": {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "age": {"type": "integer", "minimum": 0, "maximum": 200},
            "occupation": {"type": "string"},
            "personality_traits": {
                "type": "array",
                "items": {"type": "string"},
                "maxItems": 5
            },
            "backstory": {"type": "string", "maxLength": 500}
        },
        "required": ["name", "age", "occupation", "personality_traits", "backstory"],
        "additionalProperties": False
    },
    
    "product": {
        "type": "object",
        "properties": {
            "product_name": {"type": "string"},
            "price": {"type": "number", "minimum": 0},
            "category": {
                "type": "string",
                "enum": ["Electronics", "Clothing", "Books", "Home & Garden", "Sports", "Other"]
            },
            "in_stock": {"type": "boolean"},
            "features": {
                "type": "array",
                "items": {"type": "string"},
                "minItems": 1,
                "maxItems": 10
            },
            "rating": {"type": "number", "minimum": 0, "maximum": 5}
        },
        "required": ["product_name", "price", "category", "in_stock", "features", "rating"],
        "additionalProperties": False
    },
    
    "analysis": {
        "type": "object",
        "properties": {
            "summary": {"type": "string", "maxLength": 200},
            "key_points": {
                "type": "array",
                "items": {"type": "string"},
                "minItems": 3,
                "maxItems": 7
            },
            "confidence_score": {"type": "number", "minimum": 0, "maximum": 1},
            "recommendations": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "action": {"type": "string"},
                        "priority": {"type": "string", "enum": ["high", "medium", "low"]},
                        "rationale": {"type": "string"}
                    },
                    "required": ["action", "priority", "rationale"],
                    "additionalProperties": False
                }
            }
        },
        "required": ["summary", "key_points", "confidence_score", "recommendations"],
        "additionalProperties": False
    },
    
    "simple": {
        "type": "object",
        "properties": {
            "response": {"type": "string"},
            "sentiment": {"type": "string", "enum": ["positive", "negative", "neutral"]},
            "confidence": {"type": "number", "minimum": 0, "maximum": 1}
        },
        "required": ["response", "sentiment", "confidence"],
        "additionalProperties": False
    }
}

# Define test prompts
TEST_CASES = [
    {
        "name": "Character Generation",
        "messages": [{"role": "user", "content": "Create a compelling fantasy character for a medieval RPG game."}],
        "schema": SCHEMAS["character"]
    },
    {
        "name": "Product Creation", 
        "messages": [{"role": "user", "content": "Design an innovative tech product that would be popular in 2025."}],
        "schema": SCHEMAS["product"]
    },
    {
        "name": "Data Analysis",
        "messages": [{"role": "user", "content": "Analyze the potential impact of AI on the job market in the next 5 years."}],
        "schema": SCHEMAS["analysis"]
    },
    {
        "name": "Simple Response",
        "messages": [{"role": "user", "content": "What do you think about renewable energy adoption?"}],
        "schema": SCHEMAS["simple"]
    }
]

# Models to test (using env var names)
MODELS_TO_TEST = [
    "gemini_2_5_pro",
    "gemini_2_5_flash", 
    "gemini_2_5_flash_lite",
    "gpt_4_1",
    "o4_mini",
    "o3",
    "claude_opus_4",
    "claude_sonnet_4",
    "claude_sonnet_3_7",
    "claude_haiku_3_5"
]

def test_model_with_schema(client: UniversalModelClient, model: str, test_case: dict) -> dict:
    """Test a specific model with a specific schema"""
    try:
        logger.info(f"Testing {model} with {test_case['name']}")
        
        result = client.complete(
            messages=test_case["messages"],
            model=model,
            schema=test_case["schema"],
            fallback_models=[]  # Disable fallbacks for individual model testing
        )
        
        # Try to parse JSON response
        try:
            response_content = result["response"].choices[0].message.content
            parsed_json = json.loads(response_content)
            json_valid = True
        except json.JSONDecodeError as e:
            parsed_json = None
            json_valid = False
            logger.warning(f"Invalid JSON from {model}: {e}")
        
        return {
            "model": model,
            "test_case": test_case["name"],
            "success": True,
            "model_used": result["model_used"],
            "total_attempts": result["total_attempts"],
            "structured_output_native": result["structured_output_native"],
            "json_valid": json_valid,
            "response_content": response_content,
            "parsed_json": parsed_json,
            "error": None
        }
        
    except Exception as e:
        logger.error(f"Failed testing {model} with {test_case['name']}: {e}")
        return {
            "model": model,
            "test_case": test_case["name"],
            "success": False,
            "error": str(e),
            "json_valid": False,
            "response_content": None,
            "parsed_json": None
        }

def test_fallback_sequence(client: UniversalModelClient) -> dict:
    """Test the fallback sequence with a failing primary model"""
    logger.info("Testing fallback sequence...")
    
    try:
        # Use a non-existent model to trigger fallback
        result = client.complete(
            messages=[{"role": "user", "content": "Hello, test the fallback system!"}],
            model="non-existent-model",
            schema=SCHEMAS["simple"]
        )
        
        return {
            "success": True,
            "model_used": result["model_used"],
            "total_attempts": result["total_attempts"],
            "attempts": result["attempts"]
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def run_comprehensive_test():
    """Run comprehensive tests on all models"""
    logger.info("Starting comprehensive model testing...")
    
    client = UniversalModelClient()
    results = []
    
    # Test each model with each schema
    for model in MODELS_TO_TEST:
        for test_case in TEST_CASES:
            result = test_model_with_schema(client, model, test_case)
            results.append(result)
    
    # Test fallback sequence
    fallback_result = test_fallback_sequence(client)
    
    # Generate summary report
    generate_report(results, fallback_result)
    
    return results, fallback_result

def generate_report(results: list, fallback_result: dict):
    """Generate a comprehensive test report"""
    print("\n" + "="*80)
    print("UNIVERSAL MODEL TESTER - COMPREHENSIVE REPORT")
    print("="*80)
    
    # Success rate by model
    print("\n📊 SUCCESS RATE BY MODEL:")
    print("-" * 40)
    
    model_stats = {}
    for result in results:
        model = result["model"]
        if model not in model_stats:
            model_stats[model] = {"total": 0, "success": 0, "json_valid": 0}
        
        model_stats[model]["total"] += 1
        if result["success"]:
            model_stats[model]["success"] += 1
        if result.get("json_valid", False):
            model_stats[model]["json_valid"] += 1
    
    for model, stats in model_stats.items():
        success_rate = (stats["success"] / stats["total"]) * 100
        json_rate = (stats["json_valid"] / stats["total"]) * 100
        print(f"{model:30} | Success: {success_rate:5.1f}% | Valid JSON: {json_rate:5.1f}%")
    
    # Success rate by test case
    print("\n📋 SUCCESS RATE BY TEST CASE:")
    print("-" * 40)
    
    case_stats = {}
    for result in results:
        case = result["test_case"]
        if case not in case_stats:
            case_stats[case] = {"total": 0, "success": 0, "json_valid": 0}
        
        case_stats[case]["total"] += 1
        if result["success"]:
            case_stats[case]["success"] += 1
        if result.get("json_valid", False):
            case_stats[case]["json_valid"] += 1
    
    for case, stats in case_stats.items():
        success_rate = (stats["success"] / stats["total"]) * 100
        json_rate = (stats["json_valid"] / stats["total"]) * 100
        print(f"{case:25} | Success: {success_rate:5.1f}% | Valid JSON: {json_rate:5.1f}%")
    
    # Structured output support
    print("\n🏗️  STRUCTURED OUTPUT SUPPORT:")
    print("-" * 40)
    
    native_support = {}
    for result in results:
        if result["success"] and "structured_output_native" in result:
            model = result["model"]
            native = result["structured_output_native"]
            if model not in native_support:
                native_support[model] = native
    
    for model, native in native_support.items():
        support_type = "Native JSON Schema" if native else "Prompt Injection"
        print(f"{model:30} | {support_type}")
    
    # Fallback test result
    print("\n🔄 FALLBACK SEQUENCE TEST:")
    print("-" * 40)
    if fallback_result["success"]:
        print(f"✅ Success! Final model: {fallback_result['model_used']}")
        print(f"   Total attempts: {fallback_result['total_attempts']}")
    else:
        print(f"❌ Failed: {fallback_result['error']}")
    
    # Failed tests
    failed_tests = [r for r in results if not r["success"]]
    if failed_tests:
        print(f"\n❌ FAILED TESTS ({len(failed_tests)}):")
        print("-" * 40)
        for fail in failed_tests:
            print(f"{fail['model']:20} | {fail['test_case']:20} | {fail['error']}")
    
    print("\n" + "="*80)

def main():
    """Main function"""
    try:
        results, fallback_result = run_comprehensive_test()
        
        # Save detailed results
        with open("test_results.json", "w") as f:
            json.dump({
                "individual_tests": results,
                "fallback_test": fallback_result
            }, f, indent=2)
        
        logger.info("Test complete! Results saved to test_results.json")
        
    except Exception as e:
        logger.error(f"Test suite failed: {e}")

if __name__ == "__main__":
    main()