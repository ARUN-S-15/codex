"""Test C debugging with real cppcheck analysis"""
import sys
import json
sys.path.insert(0, 'e:\\codex_1\\codex')

from app import app

# Create test client
client = app.test_client()

# C code with actual issues that cppcheck can detect
test_c_code = """#include<stdio.h>
int main()
{
    int n;
    int *ptr;
    printf("%d", n);
    printf("%d", *ptr);
    return 0;
}"""

print("=" * 70)
print("Testing C Code with Real Issues (uninitialized variables)")
print("=" * 70)
print("\nOriginal Code:")
print(test_c_code)

# Send debug request
response = client.post('/debug',
                      data=json.dumps({
                          'code': test_c_code,
                          'language': 'C'
                      }),
                      content_type='application/json')

result = response.get_json()

print("\n" + "=" * 70)
print("Issues Found by cppcheck:")
print("=" * 70)
issues = result.get('issues', 'No issues')
print(issues)

print("\n" + "=" * 70)
print("Analysis:")
print("=" * 70)

# Check if cppcheck detected the issues
if "uninitialized" in issues.lower() or "uninitvar" in issues.lower():
    print("✅ cppcheck detected uninitialized variable 'n'")
else:
    print("⚠️ cppcheck warnings may not show uninitialized variable")

if "null" in issues.lower() or "uninitptr" in issues.lower():
    print("✅ cppcheck detected uninitialized pointer '*ptr'")
else:
    print("⚠️ cppcheck warnings may not show pointer issue")

if "cppcheck not found" not in issues.lower():
    print("✅ cppcheck IS working! (no 'not found' error)")
else:
    print("❌ cppcheck still not found")

print("\n" + "=" * 70)
print("Conclusion:")
print("=" * 70)
if "information:" in issues or "warning:" in issues or "error:" in issues:
    print("🎉 SUCCESS! cppcheck is installed and analyzing your C code!")
else:
    print("⚠️ cppcheck may be running but with limited output")
