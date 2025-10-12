"""
Direct test of run_judge0 function
"""
import sys
sys.path.insert(0, '.')

from app import run_judge0

print("Testing run_judge0 function directly...\n")

code = """
x = 10
y = 20
print(f"Sum: {x + y}")
"""

print("Running Python code...")
result = run_judge0(code, 71, "")

print("\nResult:")
print("=" * 60)
print(result)
print("=" * 60)
