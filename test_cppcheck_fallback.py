"""Test C code debugging when cppcheck is not available"""
import sys
import json
sys.path.insert(0, 'e:\\codex_1\\codex')

from app import app

# Create test client
client = app.test_client()

# Your buggy C code
test_c_code = """#include<stdio.h>
int main
{
int n = 10
printf("%d",n);
}"""

print("=" * 70)
print("Testing C Code Debug WITHOUT cppcheck in PATH")
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
print("Issues Box Output:")
print("=" * 70)
print(result.get('issues', 'No issues'))

print("\n" + "=" * 70)
print("Fixed Code Output:")
print("=" * 70)
print(result.get('fixed_code', 'No fixed code'))

print("\n" + "=" * 70)
print("Verification:")
print("=" * 70)

# Check that helpful message is shown
if "cppcheck not found" in result.get('issues', '').lower():
    print("✅ Helpful error message about cppcheck shown")
else:
    print("❌ No cppcheck error message found")

# Check that installation instructions are provided
if "install" in result.get('issues', '').lower():
    print("✅ Installation instructions provided")
else:
    print("❌ No installation instructions")

# Check that code was still auto-fixed
fixed = result.get('fixed_code', '')
checks = [
    ("main() added", "int main()" in fixed),
    ("Opening brace present", "{" in fixed),
    ("Semicolon after int n = 10", "int n = 10;" in fixed),
]

print("\nAuto-fix Results (even without linter):")
for check_name, passed in checks:
    status = "✅" if passed else "❌"
    print(f"{status} {check_name}")
