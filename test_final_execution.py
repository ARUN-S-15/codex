"""
Final comprehensive test of CODEX code execution
"""
import requests
import json

BASE_URL = "http://127.0.0.1:5000"

def test_language(name, code, language_id, expected_in_output):
    """Test a specific language"""
    print(f"\n{'='*60}")
    print(f"Testing {name}")
    print('='*60)
    
    payload = {
        "code": code,
        "language_id": language_id,
        "stdin": ""
    }
    
    try:
        response = requests.post(f"{BASE_URL}/run", json=payload, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            output = result.get("output", "")
            
            print(f"✅ Execution successful!")
            print(f"\nOutput:")
            print("-" * 40)
            print(output)
            print("-" * 40)
            
            if expected_in_output in output:
                print(f"✅ Verification PASSED")
                return True
            else:
                print(f"⚠️ Verification FAILED - expected '{expected_in_output}' in output")
                return False
        else:
            print(f"❌ Request failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    print("\n" + "="*60)
    print("🧪 CODEX COMPREHENSIVE CODE EXECUTION TEST")
    print("="*60)
    
    results = []
    
    # Test 1: Python
    python_code = """x = 15
y = 25
print(f"Sum: {x + y}")
print("Python works!")"""
    results.append(("Python", test_language("Python 3", python_code, 71, "Python works!")))
    
    # Test 2: C
    c_code = """#include <stdio.h>
int main() {
    printf("C works!\\n");
    printf("5 + 3 = %d\\n", 5 + 3);
    return 0;
}"""
    results.append(("C", test_language("C (GCC)", c_code, 50, "C works!")))
    
    # Test 3: C++
    cpp_code = """#include <iostream>
using namespace std;
int main() {
    cout << "C++ works!" << endl;
    cout << "10 * 2 = " << (10 * 2) << endl;
    return 0;
}"""
    results.append(("C++", test_language("C++ (G++)", cpp_code, 54, "C++ works!")))
    
    # Test 4: Java
    java_code = """public class Main {
    public static void main(String[] args) {
        System.out.println("Java works!");
        System.out.println("7 * 7 = " + (7 * 7));
    }
}"""
    results.append(("Java", test_language("Java", java_code, 62, "Java works!")))
    
    # Test 5: JavaScript
    js_code = """console.log("JavaScript works!");
const x = 12;
const y = 8;
console.log(`${x} + ${y} = ${x + y}`);"""
    results.append(("JavaScript", test_language("JavaScript (Node.js)", js_code, 63, "JavaScript works!")))
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    
    for lang, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{lang:15s} {status}")
    
    all_passed = all(r[1] for r in results)
    passed_count = sum(1 for r in results if r[1])
    
    print("\n" + "="*60)
    if all_passed:
        print("🎉 ALL TESTS PASSED!")
        print("="*60)
        print("\n✅ Your CODEX platform is FULLY OPERATIONAL!")
        print("\nAll language support is working:")
        print("  • Python ✅")
        print("  • C ✅")
        print("  • C++ ✅")
        print("  • Java ✅")
        print("  • JavaScript ✅")
        print("\n🚀 Ready for production use!")
        print("\nOpen: http://127.0.0.1:5000")
        print("Login and start coding! 💻✨")
    else:
        print(f"⚠️ {passed_count}/{len(results)} TESTS PASSED")
        print("="*60)
        print("\nSome languages may need more time or have temporary issues.")
        print("The working languages are ready to use!")
    print()

if __name__ == "__main__":
    import time
    print("\nWaiting for Flask to be ready...")
    time.sleep(1)
    
    try:
        requests.get(BASE_URL, timeout=5)
        print("✅ Flask is running!\n")
    except:
        print("❌ Flask not running! Start it with: python app.py\n")
        exit(1)
    
    main()
