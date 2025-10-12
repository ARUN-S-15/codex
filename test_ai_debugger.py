"""
Test the AI-powered debugger with various logical errors
"""
import requests
import json

BASE_URL = "http://127.0.0.1:5000"

# Test cases with intentional bugs
test_cases = [
    {
        "name": "Infinite Loop (no break)",
        "code": """
count = 0
while True:
    print(count)
    count += 1
print("Done")
""",
        "expected_bugs": ["Infinite Loop"]
    },
    {
        "name": "Assignment in Conditional",
        "code": """
x = 5
if x = 10:
    print("x is 10")
else:
    print("x is not 10")
""",
        "expected_bugs": ["Assignment in Conditional"]
    },
    {
        "name": "Off-by-One Array Access",
        "code": """
numbers = [1, 2, 3, 4, 5]
for i in range(len(numbers)):
    if i < len(numbers):
        print(numbers[i] + numbers[i+1])
""",
        "expected_bugs": ["Potential Index Error"]
    },
    {
        "name": "Variable Typo",
        "code": """
user_name = "Alice"
age = 25
print(f"Hello {usernmae}, you are {age} years old")
""",
        "expected_bugs": ["Possible Typo"]
    },
    {
        "name": "Loop Variable Modification",
        "code": """
for i in range(10):
    print(i)
    i = i + 5  # This won't affect the loop
print("Loop done")
""",
        "expected_bugs": ["Loop Variable Modification"]
    },
    {
        "name": "Multiple Bugs",
        "code": """
total = 0
count = 0
while True:
    total = total + count
    count += 1
    if total = 100:
        break
print(f"Total is {totl}")
""",
        "expected_bugs": ["Infinite Loop", "Assignment in Conditional", "Possible Typo"]
    },
    {
        "name": "Clean Code (No Bugs)",
        "code": """
def calculate_sum(numbers):
    total = 0
    for num in numbers:
        total += num
    return total

result = calculate_sum([1, 2, 3, 4, 5])
print(f"Sum: {result}")
""",
        "expected_bugs": []
    }
]

def test_debugger():
    print("=" * 70)
    print("🤖 AI DEBUGGER TEST SUITE")
    print("=" * 70)
    
    for idx, test in enumerate(test_cases, 1):
        print(f"\n📝 Test {idx}: {test['name']}")
        print("-" * 70)
        
        try:
            response = requests.post(
                f"{BASE_URL}/debug",
                json={
                    "code": test["code"],
                    "language": "python"
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Check if AI analysis is present
                if "ai_analysis" in data and data["ai_analysis"]:
                    ai = data["ai_analysis"]
                    bugs_found = ai.get("bugs_found", [])
                    
                    print(f"✅ Response received")
                    print(f"🐛 Bugs detected: {len(bugs_found)}")
                    
                    if bugs_found:
                        for bug in bugs_found:
                            severity_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}
                            emoji = severity_emoji.get(bug["severity"], "🔵")
                            print(f"   {emoji} Line {bug['line']}: {bug['type']}")
                            print(f"      → {bug['message']}")
                    else:
                        print("   ✨ No logical errors found!")
                    
                    # Check if expected bugs were found
                    found_types = [bug["type"] for bug in bugs_found]
                    expected = test["expected_bugs"]
                    
                    if len(expected) == 0 and len(bugs_found) == 0:
                        print("   ✅ PASS: Correctly identified clean code")
                    elif any(exp in " ".join(found_types) for exp in expected):
                        print(f"   ✅ PASS: Found expected bugs")
                    else:
                        print(f"   ⚠️  Expected: {expected}")
                        print(f"   ⚠️  Found: {found_types}")
                    
                    # Show fixed code snippet
                    fixed = data.get("fixed_code", "")
                    if fixed and fixed != test["code"]:
                        print(f"\n   💡 Code was auto-fixed (syntax improvements applied)")
                else:
                    print("⚠️  No AI analysis in response")
                    print(f"Issues: {data.get('issues', 'None')[:200]}")
            else:
                print(f"❌ Request failed: {response.status_code}")
                print(f"Response: {response.text[:200]}")
                
        except requests.exceptions.ConnectionError:
            print("❌ Cannot connect to Flask server")
            print("   Make sure Flask is running: python app.py")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n" + "=" * 70)
    print("✅ Test suite completed!")
    print("=" * 70)

if __name__ == "__main__":
    test_debugger()
