"""
Quick smoke test to verify imports and basic initialization.
Run: python test_simple.py
"""

import sys

print("=" * 60)
print("SMOKE TEST: Checking imports and initialization")
print("=" * 60)

# Test 1: Config
print("\n1️⃣  Testing config...")
try:
    from config_simple import GROQ_API_KEY, PRIMARY_MODEL
    if GROQ_API_KEY:
        print("   ✅ GROQ_API_KEY loaded")
    else:
        print("   ⚠️  GROQ_API_KEY is empty")
    print(f"   ✅ Primary model: {PRIMARY_MODEL}")
except Exception as e:
    print(f"   ❌ Config import failed: {e}")
    sys.exit(1)

# Test 2: LLM Handler
print("\n2️⃣  Testing LLM handler...")
try:
    from llm_handler_simple import LLMHandler
    llm = LLMHandler()
    print(f"   ✅ LLM initialized with model: {llm.current_model}")
except Exception as e:
    print(f"   ❌ LLM initialization failed: {e}")
    sys.exit(1)

# Test 3: Image Handler
print("\n3️⃣  Testing Image handler...")
try:
    from image_handler_simple import ImageHandler
    img = ImageHandler()
    if img.available:
        print("   ✅ Image handler ready (HF_API_KEY available)")
    else:
        print("   ⚠️  Image handler stubbed (HF_API_KEY missing)")
except Exception as e:
    print(f"   ❌ Image handler failed: {e}")
    sys.exit(1)

# Test 4: Simple LLM call
print("\n4️⃣  Testing LLM content generation...")
try:
    result = llm.generate_post(
        product_name="Test Product",
        product_description="A test product for demo",
        platform="instagram",
        tone="casual",
        content_type="product_highlight",
    ) 
    print(f"   ✅ Generated caption: {result['caption'][:50]}...")
    print(f"   ✅ Generated hashtags: {result['hashtags'][:3]}")
except Exception as e:
    print(f"   ❌ LLM generation failed: {e}")
    sys.exit(1)

print("\n" + "=" * 60)
print("✅ ALL TESTS PASSED!")
print("=" * 60)
print("\n▶️  To run the Streamlit app:")
print("   streamlit run app_simple.py")
