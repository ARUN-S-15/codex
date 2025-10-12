"""Test if Judge0 is actually working"""
import requests
import time

def test_judge0():
    print("\n" + "="*60)
    print("🔍 Testing Judge0 Docker Setup")
    print("="*60 + "\n")
    
    # Test 1: Can we reach Judge0?
    print("Test 1: Checking if Judge0 API is accessible...")
    try:
        response = requests.get("http://localhost:2358/about", timeout=5)
        if response.status_code == 200:
            print("✅ Judge0 API is accessible")
            data = response.json()
            print(f"   Version: {data.get('version')}")
        else:
            print(f"❌ Judge0 returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to Judge0: {e}")
        return False
    
    # Test 2: Can we submit code?
    print("\nTest 2: Attempting to execute Python code...")
    code = "print('Hello from Judge0!')"
    
    payload = {
        "source_code": code,
        "language_id": 71,  # Python 3
        "stdin": ""
    }
    
    try:
        # Submit without wait
        submit_response = requests.post(
            "http://localhost:2358/submissions?base64_encoded=false&wait=false",
            json=payload,
            timeout=10
        )
        
        if submit_response.status_code != 201:
            print(f"❌ Submission failed with status {submit_response.status_code}")
            print(f"   Response: {submit_response.text[:200]}")
            return False
        
        token = submit_response.json().get('token')
        print(f"✅ Code submitted (token: {token})")
        
        # Wait and check result
        print("   Waiting for execution...")
        time.sleep(3)
        
        result_response = requests.get(
            f"http://localhost:2358/submissions/{token}",
            timeout=5
        )
        
        if result_response.status_code != 200:
            print(f"❌ Failed to get result: {result_response.status_code}")
            return False
        
        result = result_response.json()
        status = result.get('status', {})
        status_id = status.get('id')
        status_desc = status.get('description')
        
        print(f"\n📊 Result:")
        print(f"   Status: {status_desc} (ID: {status_id})")
        
        if status_id == 3:  # Accepted
            print(f"   Output: {result.get('stdout', 'No output')}")
            print(f"   Time: {result.get('time')}s")
            print(f"   Memory: {result.get('memory')} KB")
            print("\n" + "="*60)
            print("🎉 SUCCESS! Judge0 Docker is fully working!")
            print("="*60 + "\n")
            return True
        else:
            print(f"   Error: {result.get('message', 'Unknown error')}")
            if result.get('stderr'):
                print(f"   Stderr: {result.get('stderr')[:200]}")
            
            print("\n" + "="*60)
            print("❌ Judge0 containers are running but code execution failed")
            print("="*60)
            print("\n💡 This is likely a cgroup/sandbox issue on Windows.")
            print("   Your options:")
            print("   1. Use RapidAPI (recommended - works immediately)")
            print("   2. Try running Docker Desktop as Administrator")
            print("   3. Switch Docker to Hyper-V mode (if using WSL 2)")
            print("\n")
            return False
            
    except Exception as e:
        print(f"❌ Error during execution: {e}")
        return False

if __name__ == "__main__":
    working = test_judge0()
    
    if not working:
        print("\n" + "🚀 Quick Fix: Use RapidAPI".center(60, "="))
        print("\n1. Visit: https://rapidapi.com/judge0-official/api/judge0-ce")
        print("2. Sign up and get your FREE API key")
        print("3. Add to .env file: JUDGE0_API_KEY=your-key-here")
        print("4. Restart Flask: python app.py")
        print("5. Start coding! ✨\n")
