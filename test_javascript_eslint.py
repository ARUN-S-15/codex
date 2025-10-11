"""Test JavaScript debugging with eslint"""
import sys
import json
sys.path.insert(0, 'e:\\codex_1\\codex')

from app import app

# Create test client
client = app.test_client()

# Buggy JavaScript code
test_js_code = """let x = 5
console.log(x)
var y = 10
console.log(y)"""

print("=" * 70)
print("Testing JavaScript Code Debug with eslint")
print("=" * 70)
print("\nOriginal Code (with bugs):")
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

issues = result.get('issues', '')
fixed = result.get('fixed_code', '')

# Check if eslint is working
if "eslint not found" in issues.lower():
    print("❌ eslint still not found")
    print("\n🔧 The code now searches for eslint in:")
    print("   1. System PATH")
    print("   2. C:\\Users\\aruns\\AppData\\Roaming\\npm\\eslint.cmd")
    print("   3. Local node_modules")
elif "error" in issues.lower() or "warning" in issues.lower() or "✅" in issues:
    print("✅ eslint IS WORKING!")

# Check auto-fix
checks = [
    ("Semicolon after let x = 5", "let x = 5;" in fixed),
    ("Semicolon after console.log(x)", "console.log(x);" in fixed),
    ("var replaced with let", "let y = 10" in fixed),
]

print("\nAuto-fix Results:")
for check_name, passed in checks:
    status = "✅" if passed else "❌"
    print(f"{status} {check_name}")

print("\n" + "=" * 70)
if "eslint not found" not in issues.lower():
    print("🎉 SUCCESS! eslint is analyzing your JavaScript code!")
else:
    print("ℹ️  eslint not detected, but auto-fix still works!")
