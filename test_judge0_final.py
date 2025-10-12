"""
Test Judge0 Integration - Final Verification
Tests that Judge0 is working properly with code execution
"""

import requests
import time
import json

def test_judge0_connection():
    """Test if Judge0 API is accessible"""
    print("=" * 60)
    print("TEST 1: Judge0 API Connection")
    print("=" * 60)
    try:
        response = requests.get("http://localhost:2358/about", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Judge0 is running!")
            print(f"   Version: {data.get('version')}")
            print(f"   Homepage: {data.get('homepage')}")
            return True
        else:
            print(f"❌ Judge0 returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Judge0 on http://localhost:2358")
        print("   Make sure Docker containers are running: docker ps")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_python_execution():
    """Test Python code execution"""
    print("\n" + "=" * 60)
    print("TEST 2: Python Code Execution")
    print("=" * 60)
    
    code = """
x = 5
y = 10
print(f"Sum: {x + y}")
print(f"Product: {x * y}")
"""
    
    payload = {
        "source_code": code,
        "language_id": 71,  # Python 3
        "stdin": ""
    }
    
    try:
        # Submit code
        print("Submitting Python code...")
        response = requests.post(
            "http://localhost:2358/submissions?base64_encoded=false&wait=false",
            json=payload,
            timeout=10
        )
        
        if response.status_code not in [200, 201]:
            print(f"❌ Submission failed with status {response.status_code}")
            print(response.text)
            return False
        
        token = response.json().get("token")
        print(f"   Token: {token}")
        
        # Poll for result
        print("Waiting for execution...")
        for attempt in range(30):
            time.sleep(1)
            result_response = requests.get(
                f"http://localhost:2358/submissions/{token}?base64_encoded=false",
                timeout=10
            )
            
            if result_response.status_code != 200:
                continue
            
            result = result_response.json()
            status = result.get("status", {}).get("description")
            
            print(f"   Status: {status}")
            
            if status not in ["In Queue", "Processing"]:
                print("\n✅ Execution completed!")
                print(f"   Status: {status}")
                if result.get("stdout"):
                    print(f"   Output:\n{result.get('stdout')}")
                if result.get("stderr"):
                    print(f"   Errors:\n{result.get('stderr')}")
                if result.get("compile_output"):
                    print(f"   Compile Output:\n{result.get('compile_output')}")
                return status == "Accepted"
        
        print("❌ Timeout waiting for execution")
        return False
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_c_execution():
    """Test C code execution"""
    print("\n" + "=" * 60)
    print("TEST 3: C Code Execution")
    print("=" * 60)
    
    code = """
#include <stdio.h>

int main() {
    printf("Hello from C!\\n");
    printf("2 + 2 = %d\\n", 2 + 2);
    return 0;
}
"""
    
    payload = {
        "source_code": code,
        "language_id": 50,  # C
        "stdin": ""
    }
    
    try:
        print("Submitting C code...")
        response = requests.post(
            "http://localhost:2358/submissions?base64_encoded=false&wait=true",
            json=payload,
            timeout=30
        )
        
        if response.status_code not in [200, 201]:
            print(f"❌ Submission failed with status {response.status_code}")
            return False
        
        result = response.json()
        status = result.get("status", {}).get("description")
        
        print(f"✅ Execution completed!")
        print(f"   Status: {status}")
        if result.get("stdout"):
            print(f"   Output:\n{result.get('stdout')}")
        if result.get("stderr"):
            print(f"   Errors:\n{result.get('stderr')}")
        
        return status == "Accepted"
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_java_execution():
    """Test Java code execution"""
    print("\n" + "=" * 60)
    print("TEST 4: Java Code Execution")
    print("=" * 60)
    
    code = """
public class Main {
    public static void main(String[] args) {
        System.out.println("Hello from Java!");
        System.out.println("5 * 5 = " + (5 * 5));
    }
}
"""
    
    payload = {
        "source_code": code,
        "language_id": 62,  # Java
        "stdin": ""
    }
    
    try:
        print("Submitting Java code...")
        response = requests.post(
            "http://localhost:2358/submissions?base64_encoded=false&wait=true",
            json=payload,
            timeout=30
        )
        
        if response.status_code not in [200, 201]:
            print(f"❌ Submission failed with status {response.status_code}")
            return False
        
        result = response.json()
        status = result.get("status", {}).get("description")
        
        print(f"✅ Execution completed!")
        print(f"   Status: {status}")
        if result.get("stdout"):
            print(f"   Output:\n{result.get('stdout')}")
        if result.get("stderr"):
            print(f"   Errors:\n{result.get('stderr')}")
        
        return status == "Accepted"
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("\n🔍 JUDGE0 INTEGRATION TEST\n")
    
    results = []
    
    # Test 1: Connection
    results.append(("Connection", test_judge0_connection()))
    
    if results[0][1]:  # If connection works, test code execution
        results.append(("Python", test_python_execution()))
        results.append(("C", test_c_execution()))
        results.append(("Java", test_java_execution()))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name:20s} {status}")
    
    all_passed = all(result[1] for result in results)
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 ALL TESTS PASSED! Judge0 is working perfectly!")
        print("=" * 60)
        print("\n✅ Your CODEX app is ready to use!")
        print("   • Start Flask: python app.py")
        print("   • Open browser: http://127.0.0.1:5000")
        print("   • Login and start coding!")
    else:
        print("⚠️ SOME TESTS FAILED")
        print("=" * 60)
        print("\n📝 Troubleshooting:")
        print("   • Check Docker: docker ps")
        print("   • Check logs: docker logs judge0-server-1")
        print("   • Restart: docker-compose restart")
    print()
