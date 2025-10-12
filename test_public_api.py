"""
Quick Test - Public Judge0 API
Tests if the public API works for your app
"""

import requests
import time

def test_public_api():
    print("=" * 60)
    print("Testing Public Judge0 API")
    print("=" * 60)
    print()
    
    # Test 1: Connection
    print("Test 1: Checking API availability...")
    try:
        response = requests.get("https://ce.judge0.com/about", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Public API is available!")
            print(f"   Version: {data.get('version')}")
        else:
            print(f"⚠️ API returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect: {e}")
        return False
    
    # Test 2: Python execution
    print("\nTest 2: Running Python code...")
    code = """
x = 10
y = 20
print(f"Sum: {x + y}")
print(f"Product: {x * y}")
"""
    
    payload = {
        "source_code": code,
        "language_id": 71,
        "stdin": ""
    }
    
    try:
        # Submit
        submit = requests.post(
            "https://ce.judge0.com/submissions?base64_encoded=false&wait=false",
            json=payload,
            timeout=10
        )
        
        if submit.status_code not in [200, 201]:
            print(f"❌ Submission failed: {submit.status_code}")
            return False
        
        token = submit.json().get("token")
        print(f"   Submitted! Token: {token}")
        
        # Poll for result
        print("   Waiting for execution...", end="", flush=True)
        for _ in range(30):
            time.sleep(1)
            print(".", end="", flush=True)
            
            result = requests.get(
                f"https://ce.judge0.com/submissions/{token}?base64_encoded=false",
                timeout=10
            )
            
            if result.status_code == 200:
                data = result.json()
                status = data.get("status", {}).get("description")
                
                if status not in ["In Queue", "Processing"]:
                    print(f"\n   Status: {status}")
                    
                    if data.get("stdout"):
                        print(f"\n✅ OUTPUT:")
                        print(data.get("stdout"))
                        return True
                    elif data.get("stderr"):
                        print(f"\n⚠️ ERROR:")
                        print(data.get("stderr"))
                        return False
                    else:
                        print(f"   No output")
                        return False
        
        print("\n⚠️ Timeout waiting for result")
        return False
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("\n🔍 TESTING PUBLIC JUDGE0 API\n")
    
    success = test_public_api()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 PUBLIC API WORKS PERFECTLY!")
        print("=" * 60)
        print("\nYour CODEX app will use this API automatically.")
        print("\nJust run: python app.py")
        print("Then open: http://127.0.0.1:5000")
        print("\nNo RapidAPI key needed!")
        print("No Docker issues!")
        print("Just works! ✅")
    else:
        print("⚠️ PUBLIC API TEST FAILED")
        print("=" * 60)
        print("\nPossible issues:")
        print("• Internet connection problem")
        print("• Public API temporarily down")
        print("• Firewall blocking connection")
        print("\nTry RapidAPI instead: python quick_setup.py")
    print()
