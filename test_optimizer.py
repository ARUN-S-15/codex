import requests
import json

# Test the optimize endpoint with your example code
test_code = """n = 5
for i in range(1, n+1):
    for j in range(n - i, -1, -1):
        print("* ", end="")
    print()
"""

url = "http://127.0.0.1:5000/optimize"
data = {
    "code": test_code,
    "language": "python"
}

print("🧪 Testing Optimizer...")
print("=" * 60)
print(f"📝 Original Code:\n{test_code}\n")
print("=" * 60)

try:
    response = requests.post(url, json=data, timeout=15)
    if response.status_code == 200:
        result = response.json()
        
        print("\n✅ Server Response Received!")
        print("\n" + "=" * 60)
        print("✨ OPTIMIZED CODE:")
        print("=" * 60)
        print(result.get("optimized", "No optimized code"))
        
        if "optimizations" in result and result["optimizations"]:
            print("\n" + "=" * 60)
            print("📊 OPTIMIZATIONS MADE:")
            print("=" * 60)
            for idx, opt in enumerate(result["optimizations"], 1):
                print(f"\n{idx}. ✅ {opt['change']}")
                print(f"   Description: {opt['description']}")
                print(f"   Benefit: {opt['benefit']}")
        
    else:
        print(f"❌ Server returned error: {response.status_code}")
        print(f"Response: {response.text}")
        
except requests.exceptions.ConnectionError:
    print("❌ Could not connect to Flask server at http://127.0.0.1:5000")
    print("Make sure the server is running: python app.py")
except Exception as e:
    print(f"❌ Error: {e}")
