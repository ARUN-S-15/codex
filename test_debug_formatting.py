import requests
import json

# Test the debug endpoint with code that has errors
test_code = """n = 5
for i in range(1, n+1)
    for j in range(n-i, -1, -1)
        print("* ", end="")
    print
"""

url = "http://127.0.0.1:5000/debug"
data = {
    "code": test_code,
    "language": "python"
}

print("🧪 Testing Debug Formatting...")
print("=" * 60)
print(f"📝 Test Code (with errors):\n{test_code}\n")
print("=" * 60)

try:
    response = requests.post(url, json=data, timeout=15)
    if response.status_code == 200:
        result = response.json()
        
        print("\n✅ Server Response Received!")
        print("\n" + "=" * 60)
        print("🚨 ISSUES FOUND:")
        print("=" * 60)
        print(result.get("issues", "No issues"))
        
        print("\n" + "=" * 60)
        print("✅ CORRECTED CODE:")
        print("=" * 60)
        print(result.get("fixed_code", "No fixed code"))
        
    else:
        print(f"❌ Server returned error: {response.status_code}")
        print(f"Response: {response.text}")
        
except requests.exceptions.ConnectionError:
    print("❌ Could not connect to Flask server at http://127.0.0.1:5000")
    print("Make sure the server is running: python app.py")
except Exception as e:
    print(f"❌ Error: {e}")
