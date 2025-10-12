"""Test Judge0 connection and timing"""
import requests
import time

print("=" * 60)
print("TESTING JUDGE0 CONNECTIONS")
print("=" * 60)

# Test 1: Localhost (should fail fast)
print("\n1. Testing localhost:2358...")
start = time.time()
try:
    response = requests.get("http://localhost:2358", timeout=3)
    print(f"   ✅ Localhost works - Status: {response.status_code}")
except requests.exceptions.ConnectionError:
    elapsed = time.time() - start
    print(f"   ❌ Connection refused (took {elapsed:.2f}s)")
except requests.exceptions.Timeout:
    print(f"   ❌ Timeout after 3 seconds")

# Test 2: Public API accessibility
print("\n2. Testing ce.judge0.com...")
start = time.time()
try:
    response = requests.get("https://ce.judge0.com", timeout=10)
    elapsed = time.time() - start
    print(f"   ✅ API accessible - Status: {response.status_code} (took {elapsed:.2f}s)")
except Exception as e:
    elapsed = time.time() - start
    print(f"   ❌ Failed: {e} (took {elapsed:.2f}s)")

# Test 3: Actual code submission
print("\n3. Testing code execution...")
start = time.time()
try:
    payload = {
        "source_code": "print('Hello from Judge0!')",
        "language_id": 71
    }
    
    # Submit
    response = requests.post(
        "https://ce.judge0.com/submissions?base64_encoded=false&wait=true",
        json=payload,
        timeout=30
    )
    
    elapsed = time.time() - start
    
    if response.status_code == 201:
        result = response.json()
        stdout = result.get("stdout", "").strip()
        status = result.get("status", {}).get("description", "Unknown")
        
        print(f"   ✅ Execution successful (took {elapsed:.2f}s)")
        print(f"   Status: {status}")
        print(f"   Output: {stdout}")
    else:
        print(f"   ❌ Unexpected status: {response.status_code}")
        
except Exception as e:
    elapsed = time.time() - start
    print(f"   ❌ Failed: {e} (took {elapsed:.2f}s)")

print("\n" + "=" * 60)
print("DIAGNOSIS:")
print("=" * 60)

# Provide diagnosis
print("\nIf Test 1 takes ~3 seconds: Localhost is delaying (normal if Docker not running)")
print("If Test 2 fails: Network/firewall blocking Judge0")
print("If Test 3 fails: API issue or timeout too short")
print("\nRecommendation:")
print("- If only Test 1 is slow: Disable localhost or increase timeout")
print("- If Test 2 works but Test 3 fails: Increase timeout in app.py")
print("- If all fail: Use RapidAPI or fix network/firewall")
