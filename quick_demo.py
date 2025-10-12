"""
Quick demo: Test ONE buggy code example to see AI debugger in action
"""
import requests
import json

BASE_URL = "http://127.0.0.1:5000"

# Buggy code with MULTIPLE logical errors
buggy_code = """
total = 0
count = 0
while True:
    total = total + count
    count += 1
    if total = 100:
        break
print(f"Total is {totl}")
"""

print("=" * 70)
print("🐛 TESTING AI DEBUGGER WITH BUGGY CODE")
print("=" * 70)
print("\n📝 Input Code:")
print(buggy_code)
print("=" * 70)

try:
    response = requests.post(
        f"{BASE_URL}/debug",
        json={"code": buggy_code, "language": "python"},
        timeout=30
    )
    
    if response.status_code == 200:
        data = response.json()
        
        print("\n🤖 AI ANALYSIS RESULTS:\n")
        print(data.get("issues", "No issues data"))
        
        print("\n" + "=" * 70)
        print("✨ AUTO-FIXED CODE:")
        print("=" * 70)
        print(data.get("fixed_code", "No fixed code"))
        print("=" * 70)
        
        if "ai_analysis" in data and data["ai_analysis"]:
            bugs = data["ai_analysis"].get("bugs_found", [])
            print(f"\n📊 SUMMARY: Found {len(bugs)} logical error(s)")
            print("✅ AI Debugger is working perfectly!")
        else:
            print("\n⚠️  No AI analysis in response")
    else:
        print(f"\n❌ Error: {response.status_code}")
        print(response.text)

except requests.exceptions.ConnectionError:
    print("\n❌ Cannot connect to Flask server")
    print("Make sure Flask is running: python app.py")
except Exception as e:
    print(f"\n❌ Error: {e}")
