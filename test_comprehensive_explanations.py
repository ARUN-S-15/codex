"""
Test script to verify the comprehensive explanation system
Tests the detailed, educational explanations with step-by-step breakdowns
"""

import requests
import json

# Test with the user's triangle pattern example
test_code = """n = 5
for i in range(1, n+1):
    for j in range(n - i, -1, -1):
        print("* ", end="")
    print()"""

def test_comprehensive_explanation():
    """Test the new comprehensive explanation endpoint"""
    url = "http://127.0.0.1:5000/explain_html"
    
    payload = {
        "code": test_code,
        "language": "python"
    }
    
    print("🧪 Testing Comprehensive Explanation System...")
    print("=" * 60)
    print(f"\n📝 Test Code:\n{test_code}\n")
    print("=" * 60)
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            html = result.get("html", "")
            
            # Check for comprehensive explanation features
            checks = {
                "✅ Success Card": "success-card" in html,
                "✅ Step-by-Step Section": "STEP-BY-STEP EXPLANATION" in html,
                "✅ Numbered Steps (emojis)": "1️⃣" in html or "2️⃣" in html,
                "✅ Code Blocks": "<code>" in html,
                "✅ Detailed Descriptions": "What's happening" in html or "Think of" in html,
                "✅ Background Colors": "background:" in html,
                "✅ Key Concepts Section": "KEY CONCEPTS" in html or "key concepts" in html.lower(),
            }
            
            print("\n🔍 Feature Detection:")
            print("-" * 60)
            for feature, found in checks.items():
                print(f"{feature}: {'✅ FOUND' if found else '❌ MISSING'}")
            
            print("\n" + "=" * 60)
            
            # Count total features found
            total = len(checks)
            found = sum(1 for v in checks.values() if v)
            
            print(f"\n📊 Results: {found}/{total} features detected")
            
            if found == total:
                print("✅ ✅ ✅ ALL CHECKS PASSED! ✅ ✅ ✅")
            elif found >= total * 0.7:
                print("⚠️ Most features working, some missing")
            else:
                print("❌ System needs improvement")
            
            # Print a sample of the HTML (first 1000 chars)
            print("\n📄 Sample HTML Output:")
            print("-" * 60)
            print(html[:1000] + "..." if len(html) > 1000 else html)
            print("\n" + "=" * 60)
            
            return found == total
        else:
            print(f"❌ Error: HTTP {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to Flask server at http://127.0.0.1:5000")
        print("Make sure the server is running: python app.py")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = test_comprehensive_explanation()
    exit(0 if success else 1)
