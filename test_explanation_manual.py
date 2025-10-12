import requests
import json

# Test the explanation endpoint
code = """n = 5
for i in range(1, n+1):
    for j in range(n - i, -1, -1):
        print("* ", end="")
    print()"""

url = "http://127.0.0.1:5000/explain_html"
data = {
    "code": code,
    "language": "python"
}

print("🧪 Testing Comprehensive Explanation System...")
print("=" * 60)
print(f"📝 Test Code:\n{code}\n")
print("=" * 60)

try:
    response = requests.post(url, json=data, timeout=10)
    if response.status_code == 200:
        result = response.json()
        html = result.get("html", "")
        
        print("✅ Server Response Received!")
        print(f"\n📊 HTML Length: {len(html)} characters")
        
        # Check for comprehensive explanation features
        checks = {
            "Step-by-step section": "🔍 STEP-BY-STEP EXPLANATION" in html,
            "Numbered steps (1️⃣)": "1️⃣" in html,
            "Detailed explanations": "What's happening:" in html or "Think of" in html,
            "Code blocks": "<code>" in html,
            "Issue cards": "issue-card" in html,
            "Success badges": "success-badge" in html,
        }
        
        print("\n🔍 Feature Checks:")
        all_passed = True
        for feature, found in checks.items():
            status = "✅" if found else "❌"
            print(f"  {status} {feature}: {found}")
            if not found:
                all_passed = False
        
        if all_passed:
            print("\n🎉 SUCCESS! All comprehensive explanation features are working!")
        else:
            print("\n⚠️ Some features are missing. Checking HTML content...")
        
        # Show first 500 chars of HTML
        print(f"\n📄 First 500 characters of HTML:\n{html[:500]}...")
        
    else:
        print(f"❌ Server returned error: {response.status_code}")
        print(f"Response: {response.text}")
        
except requests.exceptions.ConnectionError:
    print("❌ Could not connect to Flask server at http://127.0.0.1:5000")
    print("Make sure the server is running: python app.py")
except Exception as e:
    print(f"❌ Error: {e}")
