# app.py - Improved Version
import os
from flask import Flask, request, jsonify, render_template, redirect, url_for, make_response, Response
import sys, ast, traceback, re, requests, subprocess, tempfile, shutil

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


def analyze_python_issues(original_code, fixed_code):
    """Analyze and report Python code issues"""
    issues = []
    
    original_lines = original_code.splitlines()
    fixed_lines = fixed_code.splitlines()
    
    for i, (orig, fixed) in enumerate(zip(original_lines, fixed_lines), 1):
        if orig != fixed:
            issues.append(f"Line {i}: Fixed syntax issue\n  Before: {orig.strip()}\n  After: {fixed.strip()}")
    
    # Check for common Python issues
    if original_code == fixed_code:
        return None
    
    issues_text = "🔍 Issues Found and Fixed:\n\n" + "\n".join(issues)
    return issues_text


def auto_fix_c_cpp(code):
    """Auto-fix common C/C++ issues"""
    fixed_lines = []
    
    for line in code.splitlines():
        stripped = line.strip()
        
        # Add missing semicolons for variable declarations and simple statements
        if stripped and not stripped.endswith((';', '{', '}', '#')) and not stripped.startswith(('if', 'for', 'while', 'else', '//', '/*')):
            if any(keyword in stripped for keyword in ['int ', 'float ', 'double ', 'char ', 'cout', 'printf', 'return']):
                if not stripped.endswith(';'):
                    line = line + ';'
        
        fixed_lines.append(line)
    
    return '\n'.join(fixed_lines)

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


# ---------------- EXPLAIN CODE (ENHANCED) ----------------
@app.route("/explain", methods=["POST"])
def explain_code():
    data = request.get_json()
    code = data.get("code", "")
    language = data.get("language", "python")
    
    if not code.strip():
        return jsonify({"explanation": "⚠️ No code provided to explain."})
    
    lines = code.strip().splitlines()
    explanations = []
    
    # Get line-by-line explanations based on language
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if not stripped or stripped.startswith(("#", "//")):
            continue
        
        explanation = get_line_explanation(stripped, language, i)
        explanations.append(explanation)
    
    full_explanation = "📖 **Code Explanation:**\n\n" + "\n\n".join(explanations) if explanations else "No code to explain."
    return jsonify({"explanation": full_explanation})


def get_line_explanation(line, language, line_num):
    """Get explanation for a single line of code based on language"""
    if language == "python":
        if line.startswith("def "):
            func_name = re.search(r"def\s+(\w+)", line)
            if func_name:
                return f"**Line {line_num}:** `{line}`\n→ Defines a function named '{func_name.group(1)}'."
        elif line.startswith("print("):
            return f"**Line {line_num}:** `{line}`\n→ Outputs the result to the console."
        elif "=" in line and not any(op in line for op in ["==", "!=", "<=", ">="]):
            var = line.split("=")[0].strip()
            return f"**Line {line_num}:** `{line}`\n→ Assigns a value to variable `{var}`."
        elif line.startswith("for "):
            return f"**Line {line_num}:** `{line}`\n→ Loop that iterates over a sequence."
        elif line.startswith("if "):
            return f"**Line {line_num}:** `{line}`\n→ Checks a condition."
        elif line.startswith("return "):
            return f"**Line {line_num}:** `{line}`\n→ Returns a value from the function."
    
    elif language == "javascript":
        if "function " in line:
            return f"**Line {line_num}:** `{line}`\n→ Defines a function."
        elif "console.log" in line:
            return f"**Line {line_num}:** `{line}`\n→ Outputs to browser console."
        elif re.match(r"(let|const|var)\s+\w+", line):
            return f"**Line {line_num}:** `{line}`\n→ Declares a variable."
        elif line.startswith("return "):
            return f"**Line {line_num}:** `{line}`\n→ Returns a value."
    
    elif language in ["c", "cpp"]:
        if line.startswith("#include"):
            return f"**Line {line_num}:** `{line}`\n→ Includes a library."
        elif "int main" in line:
            return f"**Line {line_num}:** `{line}`\n→ Main function (program entry point)."
        elif re.match(r"(int|float|double|char)\s+\w+", line):
            return f"**Line {line_num}:** `{line}`\n→ Declares a variable."
        elif "cout" in line or "printf" in line:
            return f"**Line {line_num}:** `{line}`\n→ Outputs data to console."
        elif line.startswith("return "):
            return f"**Line {line_num}:** `{line}`\n→ Returns a value."
    
    elif language == "java":
        if "public class" in line:
            return f"**Line {line_num}:** `{line}`\n→ Declares a public class."
        elif "public static void main" in line:
            return f"**Line {line_num}:** `{line}`\n→ Main method (program entry point)."
        elif "System.out.println" in line:
            return f"**Line {line_num}:** `{line}`\n→ Prints output to console."
    
    return f"**Line {line_num}:** `{line}`\n→ Executes this statement."


# ---------------- DEBUG CODE (ENHANCED) ----------------
@app.route("/debug", methods=["POST"])
def debug_code():
    data = request.json
    code = data.get("code", "")
    language = data.get("language", "").lower()

    if not code:
        return jsonify({"debug": "⚠️ No code provided.", "fixed_code": ""})

    # ---------------- FIX FOR PYTHON ----------------
    if language == "python":
        fixed_code = suggest_fix(code)
        issues = analyze_python_issues(code, fixed_code)
        return jsonify({
            "debug": issues if issues else "✅ No issues found!",
            "fixed_code": fixed_code
        })

    # ---------------- OTHER LANGUAGES ----------------
    ext_map = {
        "python": ".py",
        "javascript": ".js",
        "java": ".java",
        "cpp": ".cpp",
        "c": ".c"
    }

    ext = ext_map.get(language, ".txt")
    with tempfile.NamedTemporaryFile(delete=False, suffix=ext, mode="w", encoding='utf-8') as f:
        f.write(code)
        f.flush()
        filepath = f.name

    try:
        debug_output = ""
        fixed_code = code

        if language == "javascript":
            # Basic JS validation
            debug_output = "⚠️ JavaScript debugging: Install eslint and configure for full support.\n"
            debug_output += "✅ Basic syntax check passed."
            fixed_code = code
            
        elif language in ["c", "cpp"]:
            # Use cppcheck for C/C++
            try:
                cmd = ["cppcheck", "--enable=all", "--quiet", "--template={line}:{severity}:{message}", filepath]
                result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=20)
                
                issues = result.stderr.strip()
                if issues:
                    debug_output = f"🔍 Issues found:\n{issues}"
                    fixed_code = auto_fix_c_cpp(code)
                else:
                    debug_output = "✅ No issues found!"
                    fixed_code = code
            except FileNotFoundError:
                debug_output = "⚠️ cppcheck not found. Install it for C/C++ debugging support."
                fixed_code = auto_fix_c_cpp(code)
                
        elif language == "java":
            debug_output = "⚠️ Java debugging requires additional setup. Basic syntax check passed."
            fixed_code = code
        else:
            return jsonify({"debug": f"❌ Unsupported language: {language}", "fixed_code": code})

        return jsonify({
            "debug": debug_output,
            "fixed_code": fixed_code
        })

    except FileNotFoundError as e:
        return jsonify({
            "debug": f"⚠️ Tool not found: {str(e)}. Please ensure the linter is installed.",
            "fixed_code": code
        })
    except Exception as e:
        return jsonify({
            "debug": f"❌ Error: {str(e)}",
            "fixed_code": code
        })
    finally:
        if os.path.exists(filepath):
            os.remove(filepath)


if __name__ == "__main__":
    app.run(debug=True, threaded=True)
