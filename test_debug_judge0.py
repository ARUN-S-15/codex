"""
Debug version of run_judge0 to see what's happening
"""
import requests
import time

JUDGE0_URLS = [
    "http://localhost:2358",
    "https://judge0-ce.p.rapidapi.com",
    "https://ce.judge0.com"
]

RAPIDAPI_KEY = None

def run_judge0_debug(code, language_id=71, stdin=""):
    payload = {
        "source_code": code,
        "language_id": language_id,
        "stdin": stdin
    }
    
    last_error = None
    
    # Try each Judge0 endpoint
    for base_url in JUDGE0_URLS:
        print(f"\n🔍 Trying: {base_url}")
        
        # Skip RapidAPI if no key configured
        if "rapidapi.com" in base_url and not RAPIDAPI_KEY:
            print("   ⏭️  Skipping (no API key)")
            continue
            
        try:
            headers = {"Content-Type": "application/json"}
            
            # Submit code
            timeout_seconds = 3 if "localhost" in base_url else 8
            print(f"   📤 Submitting code...")
            
            submit = requests.post(
                f"{base_url}/submissions/?base64_encoded=false&wait=false",
                json=payload,
                headers=headers,
                timeout=timeout_seconds
            )
            
            print(f"   📥 Submit response: {submit.status_code}")
            
            if submit.status_code not in [200, 201]:
                last_error = f"Server returned status {submit.status_code}"
                print(f"   ❌ {last_error}")
                continue
                
            token = submit.json().get("token")
            if not token:
                last_error = "No token received from server"
                print(f"   ❌ {last_error}")
                continue
            
            print(f"   ✅ Got token: {token}")
            print(f"   ⏳ Polling for result...")

            # Poll for result
            for attempt in range(60):
                time.sleep(1)
                res = requests.get(
                    f"{base_url}/submissions/{token}?base64_encoded=false",
                    headers=headers,
                    timeout=timeout_seconds
                )
                
                if res.status_code != 200:
                    print(f"   ❌ Poll failed: {res.status_code}")
                    break
                    
                result = res.json()
                status = result.get("status", {}).get("description")
                
                print(f"   Status: {status}", end="\r")
                
                if status not in ["In Queue", "Processing"]:
                    print(f"\n   ✅ Final status: {status}")
                    
                    output = ""
                    if result.get("stdout"):
                        output += result.get("stdout")
                        print(f"   📝 stdout: {result.get('stdout')}")
                    if result.get("stderr"):
                        output += "\n[stderr]:\n" + result.get("stderr")
                        print(f"   ⚠️  stderr: {result.get('stderr')}")
                    if result.get("compile_output"):
                        output += "\n[compile_output]:\n" + result.get("compile_output")
                        print(f"   📋 compile_output: {result.get('compile_output')}")
                    
                    final_output = output or "⚠️ No output"
                    print(f"\n   🎯 Returning: {final_output}")
                    return final_output
            
            last_error = "Timeout waiting for execution"
            print(f"   ❌ {last_error}")
            
        except requests.exceptions.ConnectionError as e:
            last_error = f"Cannot connect to {base_url}"
            print(f"   ❌ {last_error}")
            continue
        except requests.exceptions.Timeout as e:
            last_error = f"Request timeout for {base_url}"
            print(f"   ❌ {last_error}")
            continue
        except Exception as e:
            last_error = f"Unexpected error: {str(e)}"
            print(f"   ❌ {last_error}")
            continue
    
    print(f"\n❌ All endpoints failed!")
    print(f"Last error: {last_error}")
    return f"❌ Cannot connect to Judge0 API. Last error: {last_error}"


if __name__ == "__main__":
    print("=" * 60)
    print("DEBUG: Testing run_judge0 function")
    print("=" * 60)
    
    code = "print('Hello from CODEX!')"
    
    result = run_judge0_debug(code, 71, "")
    
    print("\n" + "=" * 60)
    print("FINAL RESULT:")
    print("=" * 60)
    print(result)
