"""
Quick test script to verify Gemini API connection and model availability.
Run this before deploying to check if your API key works.
"""
import os
import sys

def test_gemini_connection():
    """Test if Gemini API key is valid and list available models."""
    try:
        import google.generativeai as genai
    except ImportError:
        print("❌ google-generativeai not installed")
        print("Run: pip install -r requirements.txt")
        return False
    
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("❌ GEMINI_API_KEY environment variable not set")
        print("\nSet it with:")
        print('  PowerShell: $env:GEMINI_API_KEY = "your-key"')
        print('  CMD: set GEMINI_API_KEY=your-key')
        print('  Linux/Mac: export GEMINI_API_KEY="your-key"')
        return False
    
    print(f"✅ API key found: {api_key[:10]}...")
    
    try:
        genai.configure(api_key=api_key)
        print("✅ Successfully configured Gemini API")
        
        print("\n🔍 Fetching available models...")
        models = genai.list_models()
        
        content_models = [
            m.name for m in models 
            if "generateContent" in m.supported_generation_methods
        ]
        
        if not content_models:
            print("❌ No models available for generateContent")
            print("   Your API key may not have access to Gemini models")
            return False
        
        print(f"✅ Found {len(content_models)} available models:\n")
        for model in content_models[:10]:  # Show first 10
            model_name = model.replace("models/", "")
            print(f"   • {model_name}")
        
        if len(content_models) > 10:
            print(f"   ... and {len(content_models) - 10} more")
        
        # Test a simple generation
        print("\n🧪 Testing content generation...")
        test_model = genai.GenerativeModel(content_models[0].replace("models/", ""))
        response = test_model.generate_content("Say 'Hello'")
        
        if response and response.text:
            print(f"✅ Model works! Response: {response.text[:50]}")
            print("\n✨ Everything looks good! Ready to deploy.")
            return True
        else:
            print("⚠️  Model responded but no text generated")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    success = test_gemini_connection()
    sys.exit(0 if success else 1)
