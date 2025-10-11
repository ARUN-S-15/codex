"""Test script to demo the new /explain endpoint output."""
import sys
sys.path.insert(0, r"e:\codex_1\codex")
from app import explain_code
from flask import Flask

# Create a mock request context
test_app = Flask(__name__)

sample_code = """n = 10
if n%2 == 0:
   print("even")
else:
   print("odd")"""

with test_app.test_request_context(
    json={"code": sample_code, "language": "python"}
):
    from flask import request as flask_request
    # Directly call the endpoint
    result = explain_code()
    print(result.get_json()["explanation"])
