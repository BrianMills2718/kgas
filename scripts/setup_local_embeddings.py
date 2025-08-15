#!/usr/bin/env python3
"""
Setup script for local embeddings using all-MiniLM-L6-v2
This is an alternative to OpenAI embeddings for fully local operation
"""

import subprocess
import sys
import os

def setup_local_embeddings():
    """Setup all-MiniLM-L6-v2 for local embeddings"""
    
    print("🚀 Setting up local embeddings with all-MiniLM-L6-v2")
    print("="*60)
    
    # Check if sentence-transformers is installed
    try:
        import sentence_transformers
        print("✅ sentence-transformers is already installed")
        print(f"   Version: {sentence_transformers.__version__}")
    except ImportError:
        print("📦 Installing sentence-transformers...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "sentence-transformers"])
        print("✅ sentence-transformers installed successfully")
    
    # Download and cache the model
    print("\n📥 Downloading all-MiniLM-L6-v2 model...")
    from sentence_transformers import SentenceTransformer
    
    try:
        model = SentenceTransformer('all-MiniLM-L6-v2')
        print("✅ Model downloaded and cached successfully")
        
        # Test the model
        print("\n🧪 Testing the model...")
        test_texts = ["Apple Inc. is a technology company", "Tim Cook is the CEO"]
        embeddings = model.encode(test_texts)
        
        print(f"✅ Model test successful!")
        print(f"   Input texts: {len(test_texts)}")
        print(f"   Embedding dimension: {embeddings.shape[1]}")
        print(f"   First text embedding (first 5 dims): {embeddings[0][:5]}")
        
        # Model info
        print("\n📊 Model Information:")
        print(f"   Model name: all-MiniLM-L6-v2")
        print(f"   Embedding dimension: 384")
        print(f"   Max sequence length: 256 tokens")
        print(f"   Model size: ~80MB")
        print(f"   Speed: ~14,200 sentences/sec on CPU")
        
        # Usage instructions
        print("\n📝 Usage Instructions:")
        print("   To use local embeddings in your code:")
        print("   ```python")
        print("   from sentence_transformers import SentenceTransformer")
        print("   model = SentenceTransformer('all-MiniLM-L6-v2')")
        print("   embeddings = model.encode(['your text here'])")
        print("   ```")
        
        print("\n✅ Local embeddings setup complete!")
        
    except Exception as e:
        print(f"❌ Failed to setup model: {e}")
        return False
    
    return True

def compare_with_openai():
    """Compare local embeddings with OpenAI"""
    
    print("\n🔍 Comparing with OpenAI embeddings:")
    print("-"*40)
    
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key:
        print("✅ OpenAI API key found in environment")
        print("\nComparison:")
        print("┌─────────────────────┬────────────────────┬───────────────────┐")
        print("│ Feature             │ all-MiniLM-L6-v2   │ OpenAI text-3-sm  │")
        print("├─────────────────────┼────────────────────┼───────────────────┤")
        print("│ Dimension           │ 384                │ 1536              │")
        print("│ Speed               │ Very Fast (local)  │ Fast (API)        │")
        print("│ Cost                │ Free               │ $0.02/1M tokens   │")
        print("│ Privacy             │ 100% local         │ API calls         │")
        print("│ Quality             │ Good               │ Excellent         │")
        print("│ Max tokens          │ 256                │ 8191              │")
        print("│ Internet required   │ No                 │ Yes               │")
        print("└─────────────────────┴────────────────────┴───────────────────┘")
    else:
        print("⚠️  No OpenAI API key found")
        print("   Local embeddings will be your only option")

if __name__ == "__main__":
    success = setup_local_embeddings()
    if success:
        compare_with_openai()
        
        print("\n🎯 Next Steps:")
        print("1. Run the demo with OpenAI: python scripts/complete_multimodal_demo_real_vectors.py")
        print("2. Or modify the script to use model_type='local' for all-MiniLM-L6-v2")