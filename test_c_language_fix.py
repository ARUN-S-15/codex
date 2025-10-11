"""Test that C language is properly detected and fixed"""
import sys
sys.path.insert(0, 'e:\\codex_1\\codex')

from app import auto_fix_c_cpp

# Your exact buggy C code
buggy_c_code = """#include<stdio.h>
int main
{
int n = 10
printf("%d",n);
}"""

print("=" * 60)
print("ORIGINAL C CODE (with bugs):")
print("=" * 60)
print(buggy_c_code)
print()

# Test the auto-fix function
fixed = auto_fix_c_cpp(buggy_c_code, [])

print("=" * 60)
print("FIXED C CODE:")
print("=" * 60)
print(fixed)
print()

# Verify fixes applied
checks = [
    ("main() added", "int main()" in fixed),
    ("Opening brace added", "int main()\n{" in fixed or "int main() {" in fixed),
    ("Semicolon after int n = 10", "int n = 10;" in fixed),
    ("Semicolon after printf", 'printf("%d",n);' in fixed or 'printf("%d", n);' in fixed)
]

print("=" * 60)
print("VERIFICATION:")
print("=" * 60)
for check_name, result in checks:
    status = "✅" if result else "❌"
    print(f"{status} {check_name}")
