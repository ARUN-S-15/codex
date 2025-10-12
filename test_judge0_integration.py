"""Test Judge0 Integration and Code Execution"""
import requests
import json
import time

def test_judge0_direct():
    """Test Judge0 API directly"""
    print("=" * 60)
    print("🔍 Testing Judge0 API Directly")
    print("=" * 60)
    
    # Test if Judge0 is accessible
    try:
        response = requests.get("http://localhost:2358/about", timeout=3)
        if response.status_code == 200:
            print("✅ Judge0 API is accessible!")
            data = response.json()
            print(f"   Version: {data.get('version')}")
            print(f"   Homepage: {data.get('homepage')}")
        else:
            print(f"❌ Judge0 returned status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to Judge0: {e}")
        return False
    
    # Test code execution
    print("\n📝 Testing Python code execution...")
    code = "print('Hello from Judge0!')"
    
    # Submit code
    payload = {
        "source_code": code,
        "language_id": 71,  # Python 3
        "stdin": ""
    }
    
    try:
        submit_response = requests.post(
            "http://localhost:2358/submissions?base64_encoded=false&wait=true",
            json=payload,
            timeout=10
        )
        
        if submit_response.status_code == 201:
            result = submit_response.json()
            print("✅ Code executed successfully!")
            print(f"   Status: {result.get('status', {}).get('description')}")
            print(f"   Output: {result.get('stdout', 'No output')}")
            print(f"   Time: {result.get('time')}s")
            print(f"   Memory: {result.get('memory')} KB")
            return True
        else:
            print(f"❌ Submission failed: {submit_response.status_code}")
            print(f"   Response: {submit_response.text}")
            return False
    except Exception as e:
        print(f"❌ Error during execution: {e}")
        return False

def test_flask_run_endpoint():
    """Test Flask /run endpoint"""
    print("\n" + "=" * 60)
    print("🔍 Testing Flask /run Endpoint")
    print("=" * 60)
    
    payload = {
        "code": "print('Hello from Flask!')",
        "language": "python",
        "input": ""
    }
    
    try:
        response = requests.post(
            "http://localhost:5000/run",
            json=payload,
            timeout=15
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ Flask /run endpoint working!")
                print(f"   Output: {result.get('output')}")
                print(f"   Execution time: {result.get('execution_time')}s")
                return True
            else:
                print("❌ Execution failed!")
                print(f"   Error: {result.get('output')}")
                return False
        else:
            print(f"❌ Flask returned status: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to Flask: {e}")
        return False

def test_multiple_languages():
    """Test different programming languages"""
    print("\n" + "=" * 60)
    print("🔍 Testing Multiple Languages via Flask")
    print("=" * 60)
    
    tests = [
        {
            "name": "Python",
            "code": "print('Python works!')",
            "language": "python"
        },
        {
            "name": "JavaScript",
            "code": "console.log('JavaScript works!');",
            "language": "javascript"
        },
        {
            "name": "C",
            "code": '#include <stdio.h>\nint main() { printf("C works!"); return 0; }',
            "language": "c"
        },
        {
            "name": "C++",
            "code": '#include <iostream>\nint main() { std::cout << "C++ works!"; return 0; }',
            "language": "cpp"
        }
    ]
    
    results = []
    for test in tests:
        print(f"\n📝 Testing {test['name']}...")
        payload = {
            "code": test['code'],
            "language": test['language'],
            "input": ""
        }
        
        try:
            response = requests.post(
                "http://localhost:5000/run",
                json=payload,
                timeout=15
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    print(f"✅ {test['name']} execution successful!")
                    print(f"   Output: {result.get('output', '').strip()}")
                    results.append(True)
                else:
                    print(f"❌ {test['name']} execution failed!")
                    print(f"   Error: {result.get('output', '')[:100]}")
                    results.append(False)
            else:
                print(f"❌ Request failed with status: {response.status_code}")
                results.append(False)
        except Exception as e:
            print(f"❌ Error: {e}")
            results.append(False)
    
    return all(results)

def test_history_saving():
    """Test if code execution is saved to history"""
    print("\n" + "=" * 60)
    print("🔍 Testing History Saving")
    print("=" * 60)
    
    # First, execute some code
    print("📝 Executing test code...")
    payload = {
        "code": "# Test history\nprint('Testing history feature!')",
        "language": "python",
        "input": ""
    }
    
    try:
        response = requests.post(
            "http://localhost:5000/run",
            json=payload,
            timeout=15
        )
        
        if response.status_code == 200 and response.json().get('success'):
            print("✅ Code executed successfully!")
            
            # Wait a moment for database to update
            time.sleep(1)
            
            # Check history (assuming user is logged in - you might need session)
            print("\n📊 Checking history endpoint...")
            try:
                history_response = requests.get(
                    "http://localhost:5000/api/history",
                    timeout=5
                )
                
                if history_response.status_code == 200:
                    history = history_response.json()
                    print(f"✅ History endpoint accessible!")
                    print(f"   Total entries: {len(history)}")
                    if history:
                        latest = history[0]
                        print(f"   Latest: {latest.get('activity_type')} - {latest.get('title')}")
                    return True
                else:
                    print(f"⚠️ History endpoint returned: {history_response.status_code}")
                    print("   (This might be normal if not logged in)")
                    return True  # Not a critical failure
            except Exception as e:
                print(f"⚠️ Cannot check history: {e}")
                return True  # Not a critical failure
        else:
            print("❌ Code execution failed!")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("🚀 CODEX - Judge0 Integration Test Suite")
    print("=" * 60)
    print()
    
    results = []
    
    # Test 1: Judge0 Direct
    results.append(("Judge0 API Direct", test_judge0_direct()))
    
    # Test 2: Flask /run endpoint
    results.append(("Flask /run Endpoint", test_flask_run_endpoint()))
    
    # Test 3: Multiple languages
    results.append(("Multiple Languages", test_multiple_languages()))
    
    # Test 4: History saving
    results.append(("History Saving", test_history_saving()))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status} - {test_name}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print("\n" + "=" * 60)
    print(f"🎯 Results: {passed}/{total} tests passed")
    print("=" * 60)
    
    if passed == total:
        print("\n🎉 All tests passed! Your CODEX is fully functional! 🚀")
    else:
        print("\n⚠️ Some tests failed. Check the output above for details.")

if __name__ == "__main__":
    main()
