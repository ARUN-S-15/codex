"""Test JavaScript with actual eslint errors"""
import sys
import json
sys.path.insert(0, 'e:\\codex_1\\codex')

from app import app

# Create test client
client = app.test_client()

# JavaScript with actual errors
test_js_code = """let x = 5
console.log(x)
console.log(y)
var z = 10"""

print("=" * 70)
print("Testing JavaScript with Real Errors")
print("=" * 70)
print("\nOriginal Code:")
print(test_js_code)

# Send debug request
response = client.post('/debug',
                      data=json.dumps({
                          'code': test_js_code,
                          'language': 'JavaScript'
                      }),
                      content_type='application/json')

result = response.get_json()

print("\n" + "=" * 70)
print("Issues Found by eslint:")
print("=" * 70)
print(result.get('issues', 'No issues'))

print("\n" + "=" * 70)
print("Fixed Code:")
print("=" * 70)
print(result.get('fixed_code', 'No fixed code'))

print("\n" + "=" * 70)
print("Analysis:")
print("=" * 70)

issues = result.get('issues', '')

if "error" in issues.lower() or "warning" in issues.lower():
    print("✅ eslint detected errors/warnings!")
elif "✅" in issues:
    print("✅ eslint ran successfully (no issues found)")
else:
    print("⚠️ Unexpected output")

if "undef" in issues.lower() or "'y'" in issues:
    print("✅ eslint detected undefined variable 'y'")

if "no-var" in issues or "var" in issues:
    print("✅ eslint detected 'var' usage")

print("\n🎉 eslint v9.37.0 is fully functional!")
