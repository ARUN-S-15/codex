"""
Test the explanation box styling in compiler page
"""
import requests

BASE_URL = "http://127.0.0.1:5000"

test_code = """
def calculate_sum(numbers):
    total = 0
    for num in numbers:
        total += num
    return total

result = calculate_sum([1, 2, 3, 4, 5])
print(f"Sum: {result}")
"""

print("=" * 70)
print("🎨 TESTING COMPILER EXPLANATION BOX STYLING")
print("=" * 70)
print("\n📝 Test Code:")
print(test_code)
print("=" * 70)

try:
    # Test the /explain_html endpoint (colorful explanations)
    response = requests.post(
        f"{BASE_URL}/explain_html",
        json={"code": test_code, "language": "Python"},
        timeout=30
    )
    
    if response.status_code == 200:
        html = response.text
        
        print("\n✅ Explanation HTML received successfully!")
        print(f"📊 Response length: {len(html)} characters")
        
        # Check if issue card styles are being used
        style_checks = {
            "Issue Card": "issue-card" in html,
            "Issue Badge": "issue-badge" in html,
            "Issue Title": "issue-title" in html,
            "Issue Description": "issue-description" in html,
            "Gradient Background": "linear-gradient" in html,
            "Border Left": "border-left:" in html,
            "Hover Animation": "transform:" in html or "translateX" in html,
        }
        
        print("\n🎨 Style Elements Found:")
        for element, found in style_checks.items():
            status = "✅" if found else "❌"
            print(f"   {status} {element}")
        
        # Check for color classes
        color_classes = {
            "Success Card": "success-card" in html,
            "Warning Card": "warning-card" in html,
            "Info Card": "info-card" in html or "issue-card" in html,
        }
        
        print("\n🌈 Color Classes:")
        for cls, found in color_classes.items():
            status = "✅" if found else "❌"
            print(f"   {status} {cls}")
        
        # Save to file for inspection
        with open("test_explanation_output.html", "w", encoding="utf-8") as f:
            f.write(f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Explanation Test Output</title>
    <style>
        body {{
            background: #1e1e1e;
            color: #ececf1;
            font-family: 'Segoe UI', sans-serif;
            padding: 2rem;
        }}
        .container {{
            max-width: 900px;
            margin: 0 auto;
            background: #202123;
            padding: 2rem;
            border-radius: 10px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1 style="color: #10a37f; text-align: center;">📝 Explanation Output Test</h1>
        {html}
    </div>
</body>
</html>""")
        
        print("\n💾 Full HTML saved to: test_explanation_output.html")
        print("\n✅ Test completed successfully!")
        
    else:
        print(f"\n❌ Request failed: {response.status_code}")
        print(f"Response: {response.text[:300]}")

except requests.exceptions.ConnectionError:
    print("\n❌ Cannot connect to Flask server")
    print("   Make sure Flask is running: python app.py")
except Exception as e:
    print(f"\n❌ Error: {e}")

print("\n" + "=" * 70)
