# test_debugger.py - Quick Test Script for CODEX Features
import requests
import json

BASE_URL = "http://localhost:5000"

def test_explain():
    """Test the /explain endpoint"""
    print("\n🧪 Testing /explain endpoint...")
    
    test_cases = [
        {
            "name": "Python Code",
            "code": """def greet(name):
    print("Hello, " + name)
    return True""",
            "language": "python"
        },
        {
            "name": "JavaScript Code",
            "code": """function add(a, b) {
    console.log("Adding numbers");
    return a + b;
}""",
            "language": "javascript"
        },
        {
            "name": "C Code",
            "code": """#include <stdio.h>
int main() {
    int x = 5;
    printf("Hello");
    return 0;
}""",
            "language": "c"
        }
    ]
    
    for test in test_cases:
        print(f"\n📝 Testing {test['name']}:")
        response = requests.post(f"{BASE_URL}/explain", json={
            "code": test["code"],
            "language": test["language"]
        })
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success!")
            print(f"Explanation Preview: {result['explanation'][:200]}...")
        else:
            print(f"❌ Failed: {response.status_code}")

def test_debug():
    """Test the /debug endpoint"""
    print("\n🧪 Testing /debug endpoint...")
    
    test_cases = [
        {
            "name": "Python with errors",
            "code": """def hello()
    x = 5
    print x""",
            "language": "python"
        },
        {
            "name": "C with missing semicolon",
            "code": """#include <stdio.h>
int main() {
    int x = 5
    printf("Hello")
    return 0
}""",
            "language": "c"
        }
    ]
    
    for test in test_cases:
        print(f"\n🐛 Testing {test['name']}:")
        response = requests.post(f"{BASE_URL}/debug", json={
            "code": test["code"],
            "language": test["language"]
        })
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success!")
            print(f"Debug Output: {result['debug'][:200]}")
            print(f"Fixed Code Preview: {result['fixed_code'][:150]}...")
        else:
            print(f"❌ Failed: {response.status_code}")

def test_run():
    """Test the /run endpoint with Judge0"""
    print("\n🧪 Testing /run endpoint (Judge0)...")
    
    test_code = """print("Hello from CODEX!")
x = 5
y = 10
print(f"Sum: {x + y}")"""
    
    print("🐍 Testing Python execution...")
    response = requests.post(f"{BASE_URL}/run", json={
        "code": test_code,
        "language_id": 71  # Python
    })
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Success!")
        print(f"Output: {result['output']}")
    else:
        print(f"❌ Failed: {response.status_code}")

def main():
    print("=" * 60)
    print("🚀 CODEX Feature Testing Suite")
    print("=" * 60)
    print("\n⚠️ Make sure Flask server is running on http://localhost:5000")
    print("   Run: python app.py")
    
    input("\nPress Enter to start testing...")
    
    try:
        # Test all endpoints
        test_explain()
        test_debug()
        test_run()
        
        print("\n" + "=" * 60)
        print("✅ Testing completed!")
        print("=" * 60)
        
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Cannot connect to server.")
        print("Make sure Flask is running: python app.py")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")

if __name__ == "__main__":
    main()
