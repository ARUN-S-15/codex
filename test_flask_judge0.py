"""Quick test to verify Judge0 fix"""
import requests
import json

print("🧪 Testing Flask /run endpoint with fixes...")
print("=" * 60)

url = "http://127.0.0.1:5000/run"

# Test 1: Simple Python code
print("\n1️⃣ Testing Python code execution...")
payload = {
    "code": "print('Hello from CODEX!')\nprint('5 + 3 =', 5 + 3)",
    "language_id": 71
}

try:
    response = requests.post(url, json=payload, timeout=30)
    data = response.json()
    
    if response.status_code == 200:
        output = data.get("output", "")
        if "cannot connect" in output.lower() or "error" in output.lower():
            print(f"   ❌ Still failing: {output[:100]}")
        else:
            print(f"   ✅ SUCCESS!")
            print(f"   Output: {output}")
    else:
        print(f"   ❌ HTTP {response.status_code}: {data}")
except Exception as e:
    print(f"   ❌ Request failed: {e}")

# Test 2: C code
print("\n2️⃣ Testing C code execution...")
payload = {
    "code": '#include <stdio.h>\nint main() { printf("C works!"); return 0; }',
    "language_id": 50
}

try:
    response = requests.post(url, json=payload, timeout=30)
    data = response.json()
    
    if response.status_code == 200:
        output = data.get("output", "")
        if "cannot connect" in output.lower() or "error" in output.lower():
            print(f"   ❌ Still failing")
        else:
            print(f"   ✅ SUCCESS!")
            print(f"   Output: {output}")
    else:
        print(f"   ❌ HTTP {response.status_code}")
except Exception as e:
    print(f"   ❌ Request failed: {e}")

print("\n" + "=" * 60)
print("✅ If both tests show SUCCESS, your Judge0 is fixed!")
print("❌ If tests still fail, Flask needs to restart or check logs")
