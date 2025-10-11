"""Test Java debugging without javac installed"""
import sys
import json
sys.path.insert(0, 'e:\\codex_1\\codex')

from app import app

# Create test client
client = app.test_client()

# Buggy Java code
test_java_code = """public class Main
{
    public static void main(String[] args)
    {
        int n = 10
        System.out.println(n)
    }
}"""

print("=" * 70)
print("Testing Java Code Debug WITHOUT javac")
print("=" * 70)
print("\nOriginal Code (with bugs):")
print(test_java_code)

# Send debug request
response = client.post('/debug',
                      data=json.dumps({
                          'code': test_java_code,
                          'language': 'Java'
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
issues = result.get('issues', '')
if "javac" in issues.lower() or "java" in issues.lower():
    print("✅ Helpful message about Java shown")
else:
    print("❌ No Java message found")

# Check that installation instructions are provided
if "install" in issues.lower() or "download" in issues.lower():
    print("✅ Installation instructions provided")
else:
    print("❌ No installation instructions")

# Check that code was still auto-fixed
fixed = result.get('fixed_code', '')
checks = [
    ("Semicolon after int n = 10", "int n = 10;" in fixed),
    ("Semicolon after println", "println(n);" in fixed),
]

print("\nAuto-fix Results (even without javac):")
for check_name, passed in checks:
    status = "✅" if passed else "❌"
    print(f"{status} {check_name}")

print("\n" + "=" * 70)
print("To install Java:")
print("=" * 70)
print("1. Download JDK from: https://www.oracle.com/java/technologies/downloads/")
print("2. Or run: winget install Oracle.JDK.21")
print("3. Add JAVA_HOME\\bin to PATH")
print("4. Restart PowerShell and verify: javac -version")
