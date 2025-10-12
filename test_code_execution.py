"""
Test CODEX App Code Execution
Tests if your Flask app's code execution endpoints work properly
"""

import requests
import time

BASE_URL = "http://127.0.0.1:5000"

def test_code_execution():
    """Test the /run endpoint"""
    print("=" * 60)
    print("🧪 TESTING CODEX CODE EXECUTION")
    print("=" * 60)
    print()
    
    # Test 1: Python Code
    print("Test 1: Python Code Execution")
    print("-" * 60)
    
    python_code = """
x = 15
y = 25
print(f"Addition: {x} + {y} = {x + y}")
print(f"Multiplication: {x} * {y} = {x * y}")
print("Hello from CODEX!")
"""
    
    payload = {
        "code": python_code,
        "language_id": 71,  # Python
        "stdin": ""
    }
    
    try:
        print("Sending Python code to CODEX...")
        response = requests.post(f"{BASE_URL}/run", json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            output = result.get("output", "")
            
            print("✅ Python Execution SUCCESS!")
            print("\nOutput:")
            print("-" * 40)
            print(output)
            print("-" * 40)
            
            # Check if output contains expected results
            if "Addition" in output and "Multiplication" in output and "Hello from CODEX" in output:
                print("✅ Output verification PASSED!")
                test1_pass = True
            else:
                print("⚠️ Output verification FAILED - unexpected output")
                test1_pass = False
        else:
            print(f"❌ Request failed with status {response.status_code}")
            print(response.text)
            test1_pass = False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        test1_pass = False
    
    print("\n")
    
    # Test 2: C Code
    print("Test 2: C Code Execution")
    print("-" * 60)
    
    c_code = """
#include <stdio.h>

int main() {
    printf("Hello from C!\\n");
    printf("5 + 3 = %d\\n", 5 + 3);
    return 0;
}
"""
    
    payload = {
        "code": c_code,
        "language_id": 50,  # C
        "stdin": ""
    }
    
    try:
        print("Sending C code to CODEX...")
        response = requests.post(f"{BASE_URL}/run", json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            output = result.get("output", "")
            
            print("✅ C Execution SUCCESS!")
            print("\nOutput:")
            print("-" * 40)
            print(output)
            print("-" * 40)
            
            if "Hello from C" in output and "5 + 3 = 8" in output:
                print("✅ Output verification PASSED!")
                test2_pass = True
            else:
                print("⚠️ Output verification FAILED")
                test2_pass = False
        else:
            print(f"❌ Request failed with status {response.status_code}")
            test2_pass = False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        test2_pass = False
    
    print("\n")
    
    # Test 3: Java Code
    print("Test 3: Java Code Execution")
    print("-" * 60)
    
    java_code = """
public class Main {
    public static void main(String[] args) {
        System.out.println("Hello from Java!");
        System.out.println("10 * 2 = " + (10 * 2));
    }
}
"""
    
    payload = {
        "code": java_code,
        "language_id": 62,  # Java
        "stdin": ""
    }
    
    try:
        print("Sending Java code to CODEX...")
        response = requests.post(f"{BASE_URL}/run", json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            output = result.get("output", "")
            
            print("✅ Java Execution SUCCESS!")
            print("\nOutput:")
            print("-" * 40)
            print(output)
            print("-" * 40)
            
            if "Hello from Java" in output and "10 * 2 = 20" in output:
                print("✅ Output verification PASSED!")
                test3_pass = True
            else:
                print("⚠️ Output verification FAILED")
                test3_pass = False
        else:
            print(f"❌ Request failed with status {response.status_code}")
            test3_pass = False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        test3_pass = False
    
    print("\n")
    
    # Test 4: JavaScript Code
    print("Test 4: JavaScript Code Execution")
    print("-" * 60)
    
    js_code = """
const x = 7;
const y = 8;
console.log("Hello from JavaScript!");
console.log(`${x} + ${y} = ${x + y}`);
"""
    
    payload = {
        "code": js_code,
        "language_id": 63,  # JavaScript
        "stdin": ""
    }
    
    try:
        print("Sending JavaScript code to CODEX...")
        response = requests.post(f"{BASE_URL}/run", json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            output = result.get("output", "")
            
            print("✅ JavaScript Execution SUCCESS!")
            print("\nOutput:")
            print("-" * 40)
            print(output)
            print("-" * 40)
            
            if "Hello from JavaScript" in output and "7 + 8 = 15" in output:
                print("✅ Output verification PASSED!")
                test4_pass = True
            else:
                print("⚠️ Output verification FAILED")
                test4_pass = False
        else:
            print(f"❌ Request failed with status {response.status_code}")
            test4_pass = False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        test4_pass = False
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    print()
    
    tests = [
        ("Python", test1_pass),
        ("C", test2_pass),
        ("Java", test3_pass),
        ("JavaScript", test4_pass)
    ]
    
    for lang, passed in tests:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{lang:15s} {status}")
    
    all_passed = all(result[1] for result in tests)
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 ALL TESTS PASSED!")
        print("=" * 60)
        print("\n✅ Your CODEX code execution is WORKING PERFECTLY!")
        print("\nYou can now:")
        print("  • Open http://127.0.0.1:5000 in browser")
        print("  • Login/Register")
        print("  • Go to Compiler")
        print("  • Write and run code in any language!")
        print("\n🚀 Your app is production-ready!")
    else:
        print("⚠️ SOME TESTS FAILED")
        print("=" * 60)
        print("\nPossible issues:")
        print("  • Internet connection problem")
        print("  • Judge0 API temporarily unavailable")
        print("  • Try again in a moment")
    print()

if __name__ == "__main__":
    print("\n🔍 TESTING CODEX CODE EXECUTION\n")
    
    # Wait a moment for Flask to fully start
    print("Waiting for Flask to be ready...")
    time.sleep(2)
    
    # Check if Flask is running
    try:
        response = requests.get(BASE_URL, timeout=5)
        print("✅ Flask app is running!\n")
    except:
        print("❌ Flask app not running!")
        print("Please start it first: python app.py\n")
        exit(1)
    
    test_code_execution()
