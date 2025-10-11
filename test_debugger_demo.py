"""
Demo test for the enhanced debugger functionality.
Shows how the debugger detects and auto-fixes common errors.
"""

# Example buggy Python code
buggy_python_code = """
n = 10
if n%2 == 0
   print "even"
else
   print "odd"
"""

# Example buggy JavaScript code
buggy_js_code = """
var x = 10
if (x > 5) {
    console.log "x is greater than 5"
}
"""

# Example buggy C code
buggy_c_code = """
#include <stdio.h>
int main() {
    int x = 10
    printf("x = %d", x)
    return 0
}
"""

print("=" * 60)
print("CODEX DEBUGGER - TEST CASES")
print("=" * 60)

print("\n1. PYTHON CODE WITH ISSUES:")
print("-" * 60)
print("Original (buggy):")
print(buggy_python_code)
print("\nExpected fixes:")
print("  ✓ Add missing colons after if/else")
print("  ✓ Convert print statements to print() functions")
print("  ✓ Fix indentation")

print("\n2. JAVASCRIPT CODE WITH ISSUES:")
print("-" * 60)
print("Original (buggy):")
print(buggy_js_code)
print("\nExpected fixes:")
print("  ✓ Add missing semicolons")
print("  ✓ Fix console.log syntax")
print("  ✓ Convert var to let/const")

print("\n3. C CODE WITH ISSUES:")
print("-" * 60)
print("Original (buggy):")
print(buggy_c_code)
print("\nExpected fixes:")
print("  ✓ Add missing semicolons")
print("  ✓ Fix printf syntax")

print("\n" + "=" * 60)
print("HOW TO TEST:")
print("=" * 60)
print("1. Start the Flask server: python app.py")
print("2. Go to http://127.0.0.1:5000/compiler")
print("3. Paste one of the buggy code examples")
print("4. Click the '🪲 Debug' button")
print("5. View:")
print("   - Left box: Issues found by linter")
print("   - Right box: Auto-fixed code")
print("\n✨ The debugger will automatically fix common errors!")
print("=" * 60)
