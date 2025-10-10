# app.py
import os
from flask import Flask, request, jsonify, render_template, redirect, url_for, make_response, Response
import sys, ast, traceback, re, requests, subprocess, tempfile

app = Flask(__name__)

# ---------------- LOGIN ----------------
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if username == "admin" and password == "123":
            resp = make_response(redirect(url_for("main")))
            resp.set_cookie("user", username)
            return resp
        else:
            return render_template("login.html", error="Invalid credentials")
    return render_template("login.html")

def check_user():
    return request.cookies.get("user")

@app.route("/main")
def main():
    if not check_user():
        return redirect(url_for("login"))
    return render_template("main.html")

@app.route("/compiler")
def compiler():
    if not check_user():
        return redirect(url_for("login"))
    return render_template("compiler.html")

@app.route("/debugger")
def debugger_page():
    if not check_user():
        return redirect(url_for("login"))
    return render_template("debug.html")


def suggest_fix(code):
    fixed_lines = []
    defined_vars = set()
    for line in code.splitlines():
        stripped = line.strip()
        if stripped.startswith("print ") and not stripped.startswith("print("):
            line = "print(" + line[len("print "):] + ")"
        if re.match(r"^(if|for|while|def|elif|else)\b", stripped) and not stripped.endswith(":"):
            line += ":"
        if re.match(r"^(if|while)\s+.*=.*", stripped) and "==" not in stripped:
            line = line.replace("=", "==")
        if "=" in line and not line.strip().startswith(("if", "while", "for", "==")):
            var = line.split("=")[0].strip()
            defined_vars.add(var)
        fixed_lines.append(line)
    fixed_code = "\n".join(fixed_lines)
    if "NameError" in code or "name '" in code:
        for var in re.findall(r"name '(\w+)' is not defined", code):
            if var not in defined_vars:
                fixed_code = f"{var} = 0\n" + fixed_code
    return fixed_code

@app.route("/optimizer")
def optimizer():
    if not check_user():
        return redirect(url_for("login"))
    return render_template("optimizer.html")

@app.route("/practice")
def practice():
    if not check_user():
        return redirect(url_for("login"))
    return render_template("practice.html")

@app.route("/problem")
def problem():
    if not check_user():
        return redirect(url_for("login"))
    return render_template("problem.html")

class Analyzer(ast.NodeVisitor):
    def __init__(self):
        self.details = []
    def visit_FunctionDef(self, node):
        self.details.append(f"Defines function '{node.name}' with {len(node.args.args)} parameter(s).")
        self.generic_visit(node)
    def visit_For(self, node):
        self.details.append("Contains a for-loop.")
        self.generic_visit(node)
    def visit_While(self, node):
        self.details.append("Contains a while-loop.")
        self.generic_visit(node)
    def visit_If(self, node):
        self.details.append("Contains an if-statement.")
        self.generic_visit(node)
    def visit_Call(self, node):
        if isinstance(node.func, ast.Name) and node.func.id:
            self.details.append(f"Calls function '{node.func.id}()'.")
        self.generic_visit(node)

def explain_python(code):
    explanation = []
    try:
        tree = ast.parse(code)
        analyzer = Analyzer()
        analyzer.visit(tree)
        explanation.extend(analyzer.details)
    except Exception as e:
        explanation.append("⚠️ Could not analyze structure: " + str(e))
    return "\n".join(explanation)


# ---------------- JUDGE0 FREE API ----------------
JUDGE0_URL = "https://ce.judge0.com/submissions/"


def run_judge0(code, language_id=71):
    payload = {
        "source_code": code,
        "language_id": language_id,
        "stdin": ""
    }
    try:
        submit = requests.post(
            "https://ce.judge0.com/submissions/?base64_encoded=false&wait=false",
            json=payload
        )
        if submit.status_code != 201:
            return f"❌ Error submitting code: {submit.text}"
        token = submit.json().get("token")

        # Poll for result
        while True:
            res = requests.get(f"https://ce.judge0.com/submissions/{token}?base64_encoded=false")
            result = res.json()
            status = result.get("status", {}).get("description")
            if status not in ["In Queue", "Processing"]:
                output = ""
                if result.get("stdout"):
                    output += result.get("stdout")
                if result.get("stderr"):
                    output += "\n[stderr]:\n" + result.get("stderr")
                if result.get("compile_output"):
                    output += "\n[compile_output]:\n" + result.get("compile_output")
                return output or "⚠️ No output"
    except Exception as e:
        return f"⚠️ Error communicating with Judge0: {str(e)}"


# ---------------- RUN CODE ----------------
@app.route("/run", methods=["POST"])
def run_code():
    data = request.json
    code = data.get("code", "")
    language_id = data.get("language_id", 71)
    try:
        output = run_judge0(code, language_id)
        return jsonify({"output": output})
    except Exception as e:
        return jsonify({"output": f"Error: {str(e)}"})


@app.route("/explain", methods=["POST"])
def explain_code():
    data = request.get_json()
    code = data.get("code", "")
    lines = code.strip().splitlines()
    explanations = []
    for line in lines:
        line = line.strip()
        if line.startswith("print("):
            explanations.append(f"`{line}` → Prints the value of the given expression.")
        elif "=" in line:
            var, expr = line.split("=", 1)
            explanations.append(f"`{line}` → Assigns the result of `{expr.strip()}` to the variable `{var.strip()}`.")
        elif line.startswith("for "):
            explanations.append(f"`{line}` → A loop that iterates over a sequence.")
        elif line.startswith("if "):
            explanations.append(f"`{line}` → Checks a condition and executes the following block if true.")
        else:
            explanations.append(f"`{line}` → Executes this statement.")
    full_explanation = "Here’s a step-by-step explanation:\n\n" + "\n".join(explanations)
    return jsonify({"explanation": full_explanation})


@app.route("/debug", methods=["POST"])
def debug_code():
    data = request.json
    code = data.get("code", "")
    language = data.get("language", "").lower()
    
    if not code:
        return jsonify({"debug": "⚠️ No code provided."})
    
    # Create a temporary file for analysis
    ext_map = {
        "python": ".py",
        "javascript": ".js",
        "java": ".java",
        "cpp": ".cpp",
        "c": ".c"
    }

    ext = ext_map.get(language, ".txt")
    with tempfile.NamedTemporaryFile(delete=False, suffix=ext, mode="w") as f:
        f.write(code)
        f.flush()
        filepath = f.name

    try:
        if language == "python":
            cmd = ["pylint", "--disable=R,C", filepath]
        elif language == "javascript":
            cmd = ["eslint", filepath, "--no-color"]
        elif language in ["c", "cpp"]:
            cmd = ["cppcheck", "--enable=all", "--quiet", filepath]
        elif language == "java":
            cmd = ["checkstyle", "-c", "/google_checks.xml", filepath]
        else:
            return jsonify({"debug": f"❌ Unsupported language: {language}"})

        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=20)
        output = result.stdout.strip() or result.stderr.strip() or "✅ No issues found!"

        return jsonify({"debug": output})

    except Exception as e:
        return jsonify({"debug": f"❌ Error: {str(e)}"})
    finally:
        os.remove(filepath)

if __name__ == "__main__":
    app.run(debug=True, threaded=True)
