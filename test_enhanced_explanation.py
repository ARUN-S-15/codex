"""
Test the enhanced explanation feature with visual boxes and emojis
"""
import requests
import json

# Test URL
url = "http://127.0.0.1:5000/explain"

# Test 1: Python code
print("=" * 70)
print("🔍 TEST 1: PYTHON CODE EXPLANATION")
print("=" * 70)

python_code = """
# Calculate sum and product
a = 10
b = 20
sum_result = a + b
product = a * b

if sum_result > 25:
    print(f"Sum is large: {sum_result}")
else:
    print(f"Sum is small: {sum_result}")

print(f"Product: {product}")
"""

response = requests.post(url, json={
    "code": python_code,
    "language": "python"
})

if response.status_code == 200:
    result = response.json()
    print("\n" + result["explanation"])
else:
    print(f"❌ Error: {response.status_code}")

print("\n\n")

# Test 2: C code
print("=" * 70)
print("🔍 TEST 2: C CODE EXPLANATION")
print("=" * 70)

c_code = """
#include <stdio.h>

int main() {
    int a = 5;
    int b = 3;
    int sum = a + b;
    
    if (sum > 7) {
        printf("Sum is large: %d\\n", sum);
    } else {
        printf("Sum is small: %d\\n", sum);
    }
    
    return 0;
}
"""

response = requests.post(url, json={
    "code": c_code,
    "language": "c"
})

if response.status_code == 200:
    result = response.json()
    print("\n" + result["explanation"])
else:
    print(f"❌ Error: {response.status_code}")

print("\n\n")

# Test 3: Java code
print("=" * 70)
print("🔍 TEST 3: JAVA CODE EXPLANATION")
print("=" * 70)

java_code = """
public class Main {
    public static void main(String[] args) {
        int x = 10;
        int y = 20;
        int result = x + y;
        
        System.out.println("Result: " + result);
        
        for (int i = 0; i < 3; i++) {
            System.out.println("Count: " + i);
        }
    }
}
"""

response = requests.post(url, json={
    "code": java_code,
    "language": "java"
})

if response.status_code == 200:
    result = response.json()
    print("\n" + result["explanation"])
else:
    print(f"❌ Error: {response.status_code}")

print("\n" + "=" * 70)
print("✅ ALL EXPLANATION TESTS COMPLETE!")
print("=" * 70)
