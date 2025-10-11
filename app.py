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


def _expr_value(node, env):
    """Evaluate a restricted set of expression AST nodes safely.

    Supports: Constant, Name, BinOp (+-*/%), Compare (==, !=, <, >, <=, >=), UnaryOp.
    Raises ValueError for unsupported nodes or unknown names.
    """
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.Name):
        if node.id in env:
            return env[node.id]
        raise ValueError(f"Unknown name: {node.id}")
    if isinstance(node, ast.BinOp):
        left = _expr_value(node.left, env)
        right = _expr_value(node.right, env)
        if isinstance(node.op, ast.Add):
            return left + right
        if isinstance(node.op, ast.Sub):
            return left - right
        if isinstance(node.op, ast.Mult):
            return left * right
        if isinstance(node.op, ast.Div):
            return left / right
        if isinstance(node.op, ast.Mod):
            return left % right
        raise ValueError("Unsupported binary operator")
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
        return -_expr_value(node.operand, env)
    if isinstance(node, ast.Compare):
        left = _expr_value(node.left, env)
        # Only handle single comparator for simplicity
        if len(node.ops) != 1 or len(node.comparators) != 1:
            raise ValueError("Complex comparisons not supported")
        right = _expr_value(node.comparators[0], env)
        op = node.ops[0]
        if isinstance(op, ast.Eq):
            return left == right
        if isinstance(op, ast.NotEq):
            return left != right
        if isinstance(op, ast.Lt):
            return left < right
        if isinstance(op, ast.LtE):
            return left <= right
        if isinstance(op, ast.Gt):
            return left > right
        if isinstance(op, ast.GtE):
            return left >= right
        raise ValueError("Unsupported comparison")
    raise ValueError(f"Unsupported expression node: {type(node).__name__}")


def simulate_simple_python(code):
    """A conservative simulator for simple top-level Python code.

    Supports Assign, Expr(print(...)), and If with supported expressions. Returns
    (steps_list, outputs_list) or raises ValueError if code is too complex.
    """
    tree = ast.parse(code)
    env = {}
    steps = []
    outputs = []

    for node in tree.body:
        if isinstance(node, ast.Assign):
            # only single target Name supported
            if len(node.targets) != 1 or not isinstance(node.targets[0], ast.Name):
                raise ValueError("Unsupported assignment target")
            name = node.targets[0].id
            val = _expr_value(node.value, env)
            env[name] = val
            steps.append(f"{name} is assigned {repr(val)}.")

        elif isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
            # print calls
            func = node.value.func
            if isinstance(func, ast.Name) and func.id == 'print':
                evaluated_args = []
                for arg in node.value.args:
                    evaluated_args.append(_expr_value(arg, env))
                outputs.append(" ".join(str(a) for a in evaluated_args))
                steps.append(f"print({', '.join(ast.get_source_segment(code, a) or '' for a in node.value.args)}) -> prints {outputs[-1]!r}.")
            else:
                raise ValueError("Unsupported function call")

        elif isinstance(node, ast.If):
            test_val = _expr_value(node.test, env)
            steps.append(f"Evaluate condition {ast.get_source_segment(code, node.test) or ''} -> {test_val}.")
            if test_val:
                # execute body (simple supported statements)
                for b in node.body:
                    if isinstance(b, ast.Expr) and isinstance(b.value, ast.Call):
                        func = b.value.func
                        if isinstance(func, ast.Name) and func.id == 'print':
                            evaluated_args = [_expr_value(a, env) for a in b.value.args]
                            outputs.append(" ".join(str(a) for a in evaluated_args))
                            steps.append(f"{ast.get_source_segment(code, b).strip()} -> prints {outputs[-1]!r}.")
                        else:
                            raise ValueError("Unsupported call in if-body")
                    elif isinstance(b, ast.Assign):
                        if len(b.targets) != 1 or not isinstance(b.targets[0], ast.Name):
                            raise ValueError("Unsupported assignment in if-body")
                        nm = b.targets[0].id
                        val = _expr_value(b.value, env)
                        env[nm] = val
                        steps.append(f"{nm} is assigned {repr(val)}.")
                    else:
                        raise ValueError("Unsupported statement in if-body")
            else:
                # orelse
                for b in node.orelse:
                    if isinstance(b, ast.Expr) and isinstance(b.value, ast.Call):
                        func = b.value.func
                        if isinstance(func, ast.Name) and func.id == 'print':
                            evaluated_args = [_expr_value(a, env) for a in b.value.args]
                            outputs.append(" ".join(str(a) for a in evaluated_args))
                            steps.append(f"{ast.get_source_segment(code, b).strip()} -> prints {outputs[-1]!r}.")
                        else:
                            raise ValueError("Unsupported call in else-body")
                    elif isinstance(b, ast.Assign):
                        if len(b.targets) != 1 or not isinstance(b.targets[0], ast.Name):
                            raise ValueError("Unsupported assignment in else-body")
                        nm = b.targets[0].id
                        val = _expr_value(b.value, env)
                        env[nm] = val
                        steps.append(f"{nm} is assigned {repr(val)}.")
                    else:
                        raise ValueError("Unsupported statement in else-body")

        else:
            raise ValueError(f"Unsupported top-level statement: {type(node).__name__}")

    return steps, outputs


# ---------------- JUDGE0 FREE API ----------------
JUDGE0_URL = "https://ce.judge0.com/submissions/"


def run_judge0(code, language_id=71, stdin=""):
    payload = {
        "source_code": code,
        "language_id": language_id,
        "stdin": stdin
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
    stdin = data.get("stdin", "")  # Get user input
    try:
        output = run_judge0(code, language_id, stdin)
        return jsonify({"output": output})
    except Exception as e:
        return jsonify({"output": f"Error: {str(e)}"})


@app.route("/compile", methods=["POST"])
def compile_code():
    """Compile or run code via Judge0 and return structured result.

    Expects JSON: { code: str, language_id: int, stdin: str (optional) }
    Returns JSON with keys: stdout, stderr, compile_output, status
    """
    data = request.get_json() or {}
    code = data.get("code", "")
    language_id = data.get("language_id", 71)
    stdin = data.get("stdin", "")

    if not code:
        return jsonify({"error": "No code provided"}), 400

    payload = {
        "source_code": code,
        "language_id": language_id,
        "stdin": stdin
    }
    try:
        submit = requests.post(
            "https://ce.judge0.com/submissions/?base64_encoded=false&wait=false",
            json=payload,
            timeout=10
        )
        if submit.status_code not in (201, 200):
            return jsonify({"error": "Failed to submit to Judge0", "detail": submit.text}), 502
        token = submit.json().get("token")

        # Poll for a short period
        for _ in range(60):
            res = requests.get(f"https://ce.judge0.com/submissions/{token}?base64_encoded=false")
            if res.status_code != 200:
                break
            result = res.json()
            status = result.get("status", {}).get("description")
            if status not in ["In Queue", "Processing"]:
                return jsonify({
                    "status": status,
                    "stdout": result.get("stdout"),
                    "stderr": result.get("stderr"),
                    "compile_output": result.get("compile_output"),
                    "message": result.get("message")
                })
        return jsonify({"error": "Timeout waiting for Judge0 result"}), 504
    except requests.exceptions.RequestException as e:
        return jsonify({"error": "Judge0 request failed", "detail": str(e)}), 502


def simple_python_optimizer(code: str) -> str:
    """A tiny, safe optimizer for Python source.

    - Removes consecutive blank lines
    - Strips trailing whitespace
    - Inlines simple constant expressions (very conservative)
    This is intentionally small and heuristic-based.
    """
    lines = code.splitlines()
    out_lines = []
    prev_blank = False
    const_assign = {}
    assign_re = re.compile(r"^\s*(\w+)\s*=\s*([0-9]+)\s*$")

    for line in lines:
        stripped = line.rstrip()
        if stripped == "":
            if prev_blank:
                continue
            prev_blank = True
            out_lines.append("")
            continue
        prev_blank = False

        m = assign_re.match(stripped)
        if m:
            var, val = m.group(1), m.group(2)
            const_assign[var] = val
            out_lines.append(f"{var} = {val}")
            continue

        # Replace simple var references with constants where safe (very conservative)
        for var, val in const_assign.items():
            # word boundary replace
            stripped = re.sub(rf"\b{var}\b", val, stripped)

        out_lines.append(stripped)

    return "\n".join(out_lines)


@app.route("/optimize", methods=["POST"])
def optimize_code():
    data = request.get_json() or {}
    code = data.get("code", "")
    language = data.get("language", "python").lower()

    if not code:
        return jsonify({"error": "No code provided"}), 400

    if language != "python":
        # For non-python languages, return a no-op placeholder
        return jsonify({"optimized": code, "notes": "No optimizer implemented for this language."})

    try:
        optimized = simple_python_optimizer(code)
        # Provide a diff-like hint (very small)
        notes = []
        if optimized != code:
            notes.append("Applied simple whitespace and constant inlining optimizations.")
        else:
            notes.append("No optimizations applied.")
        return jsonify({"optimized": optimized, "notes": notes})
    except Exception as e:
        return jsonify({"error": "Optimization failed", "detail": str(e)}), 500


@app.route("/explain", methods=["POST"])
def explain_code():
    data = request.get_json() or {}
    code = data.get("code", "")
    language = data.get("language", "python").lower().strip()

    if not code:
        return jsonify({"explanation": "⚠️ No code provided."}), 400

    # Normalize language names
    lang_normalize = {
        "javascript (node.js 12.14.0)": "javascript",
        "java (openjdk 13.0.1)": "java",
        "c++": "cpp"
    }
    language = lang_normalize.get(language, language)

    # Run linter first
    ext_map = {
        "python": (".py", ["pylint", "--disable=R,C"]),
        "javascript": (".js", ["eslint", "--no-color"]),
        "c": (".c", ["cppcheck", "--enable=all", "--quiet"]),
        "cpp": (".cpp", ["cppcheck", "--enable=all", "--quiet"]),
        "java": (".java", ["checkstyle", "-c", "/google_checks.xml"])
    }

    linter_output = ""
    tmpfile = None
    try:
        suffix = ext_map.get(language, (".txt", None))[0]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix, mode="w", encoding="utf-8") as f:
            f.write(code)
            f.flush()
            tmpfile = f.name

        tool_info = ext_map.get(language)
        if tool_info and tool_info[1]:
            cmd = tool_info[1] + [tmpfile]
            try:
                result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=15)
                linter_output = (result.stdout or "").strip() + ("\n" + result.stderr.strip() if result.stderr else "")
                if not linter_output:
                    linter_output = "✅ No linter issues found."
            except FileNotFoundError:
                linter_output = f"⚠️ Linter tool not found for language '{language}'."
            except subprocess.TimeoutExpired:
                linter_output = "⚠️ Linter timed out."
            except Exception as e:
                linter_output = f"⚠️ Error running linter: {str(e)}"
        else:
            linter_output = "⚠️ No linter configured for this language."
    finally:
        if tmpfile and os.path.exists(tmpfile):
            try:
                os.remove(tmpfile)
            except Exception:
                pass

    # Build human-friendly explanation
    explanation_parts = []

    # Header
    explanation_parts.append("=" * 60)
    explanation_parts.append("📘 CODE EXPLANATION")
    explanation_parts.append("=" * 60)
    explanation_parts.append("")

    # Linter section
    explanation_parts.append("🔍 Linter Analysis:")
    explanation_parts.append("-" * 60)
    explanation_parts.append(linter_output)
    explanation_parts.append("")

    # Line-by-line explanation for Python (with optional simulation)
    if language == "python":
        explanation_parts.append("📝 Line-by-Line Explanation:")
        explanation_parts.append("-" * 60)
        lines = code.splitlines()
        for i, line in enumerate(lines, start=1):
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            explanation_parts.append(f"{line}\n")
            # Explain the line
            if "=" in stripped and not any(op in stripped for op in ["==", "!=", "<=", ">=", "+=", "-=", "*=", "/="]):
                parts = stripped.split("=", 1)
                var = parts[0].strip()
                expr = parts[1].strip() if len(parts) > 1 else ""
                explanation_parts.append(f"  → Creates variable '{var}' and assigns it the value {expr}.")
            elif stripped.startswith("if "):
                cond = stripped[3:].rstrip(":")
                explanation_parts.append(f"  → Checks the condition: {cond}")
                if "%" in cond:
                    explanation_parts.append(f"  → The '%' operator gives the remainder after division.")
                if "==" in cond:
                    explanation_parts.append(f"  → '==' checks if two values are equal.")
            elif stripped.startswith("else:"):
                explanation_parts.append(f"  → If the condition above is false, this block runs.")
            elif "print(" in stripped:
                explanation_parts.append(f"  → Prints the given value to the console.")
            elif stripped.startswith("for "):
                explanation_parts.append(f"  → Loop that iterates over a sequence.")
            elif stripped.startswith("while "):
                explanation_parts.append(f"  → Loop that runs while a condition is true.")
            elif stripped.startswith("def "):
                explanation_parts.append(f"  → Defines a function.")
            else:
                explanation_parts.append(f"  → Executes this statement.")
            explanation_parts.append("")

        # Try to simulate execution for simple code
        explanation_parts.append("🚀 Step-by-Step Execution:")
        explanation_parts.append("-" * 60)
        try:
            steps, outputs = simulate_simple_python(code)
            for i, step in enumerate(steps, start=1):
                explanation_parts.append(f"{i}. {step}")
            explanation_parts.append("")
            if outputs:
                explanation_parts.append("✅ Output:")
                explanation_parts.append("")
                for out in outputs:
                    explanation_parts.append(f"  {out}")
            else:
                explanation_parts.append("  (No output produced)")
        except ValueError as e:
            explanation_parts.append(f"⚠️ Code is too complex to simulate: {e}")
        except Exception as e:
            explanation_parts.append(f"⚠️ Simulation error: {e}")

    else:
        # For non-Python languages, provide a basic per-line summary
        explanation_parts.append("📝 Line-by-Line Summary:")
        explanation_parts.append("-" * 60)
        lines = [l for l in code.strip().splitlines() if l.strip()]
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("//") or stripped.startswith("#"):
                continue
            explanation_parts.append(f"{line}\n")
            if "console.log" in stripped or "printf(" in stripped or "cout <<" in stripped:
                explanation_parts.append(f"  → Prints or logs output.")
            elif "=" in stripped:
                explanation_parts.append(f"  → Assigns a value to a variable.")
            elif stripped.startswith("if ") or stripped.startswith("if("):
                explanation_parts.append(f"  → Conditional check.")
            elif stripped.startswith("for ") or stripped.startswith("for("):
                explanation_parts.append(f"  → Loop construct.")
            else:
                explanation_parts.append(f"  → Executes this statement.")
            explanation_parts.append("")

    explanation_parts.append("=" * 60)

    return jsonify({"explanation": "\n".join(explanation_parts)})


def auto_fix_python(code, issues):
    """Auto-fix common Python errors based on linter output."""
    fixed_lines = []
    lines = code.splitlines()
    
    for i, line in enumerate(lines):
        fixed_line = line
        stripped = line.strip()
        
        # Fix missing colons
        if re.match(r"^(if|for|while|def|elif|else|try|except|finally|class)\b", stripped):
            if not stripped.endswith(":") and not stripped.endswith(":\\"):
                fixed_line = line + ":"
        
        # Fix print statements (Python 2 to 3)
        if stripped.startswith("print ") and not "print(" in stripped:
            content = stripped[6:]
            fixed_line = line.replace("print " + content, f"print({content})")
        
        # Fix assignment in conditionals
        if_match = re.match(r"^(\s*)(if|while)\s+(.+)", line)
        if if_match and "=" in if_match.group(3) and "==" not in if_match.group(3):
            indent, keyword, condition = if_match.groups()
            condition = condition.replace("=", "==")
            fixed_line = f"{indent}{keyword} {condition}"
        
        # Fix indentation (basic - replace tabs with 4 spaces)
        if "\t" in fixed_line:
            fixed_line = fixed_line.replace("\t", "    ")
        
        # Fix missing parentheses in function calls
        if stripped.startswith("input ") and not "input(" in stripped:
            fixed_line = line.replace("input ", "input(") + ")"
        
        fixed_lines.append(fixed_line)
    
    return "\n".join(fixed_lines)


def auto_fix_java(code, issues):
    """Auto-fix common Java errors."""
    fixed_lines = []
    lines = code.splitlines()
    
    for i, line in enumerate(lines):
        fixed_line = line
        stripped = line.strip()
        
        # Skip empty lines and comments
        if not stripped or stripped.startswith("//") or stripped.startswith("/*") or stripped.startswith("*"):
            fixed_lines.append(fixed_line)
            continue
        
        # Add missing semicolons to statements
        if stripped and not stripped.endswith((";", "{", "}", ",")):
            # Check if it's a statement that needs a semicolon
            if any(keyword in stripped for keyword in ["int ", "String ", "double ", "float ", "boolean ", 
                                                       "System.out", "return ", "break", "continue"]):
                if not stripped.endswith(";") and not stripped.endswith("{"):
                    fixed_line = line + ";"
        
        # Fix common System.out.println issues
        if "System.out.println" in stripped:
            if "(" not in stripped.split("System.out.println")[1][:2]:
                fixed_line = line.replace("System.out.println", "System.out.println(") + ")"
        
        # Add opening brace after class or method declaration if missing
        if any(keyword in stripped for keyword in ["class ", "public static void main", "public void ", "private void "]):
            if not stripped.endswith("{") and not stripped.endswith(";"):
                # Check if next line is a brace
                if i + 1 < len(lines) and lines[i + 1].strip() != "{":
                    fixed_line = line + " {"
        
        fixed_lines.append(fixed_line)
    
    # Check if closing braces are missing
    open_braces = code.count("{")
    close_braces = code.count("}")
    if open_braces > close_braces:
        for _ in range(open_braces - close_braces):
            fixed_lines.append("}")
    
    return "\n".join(fixed_lines)


def auto_fix_javascript(code, issues):
    """Auto-fix common JavaScript errors."""
    fixed_lines = []
    lines = code.splitlines()
    
    for line in lines:
        fixed_line = line
        stripped = line.strip()
        
        # Add missing semicolons
        if stripped and not stripped.endswith((";", "{", "}", ",")):
            if any(keyword in stripped for keyword in ["let", "const", "var", "return", "break", "continue"]):
                if not stripped.endswith(";"):
                    fixed_line = line + ";"
        
        # Fix console.log
        if "console.log" in stripped and not "(" in stripped.split("console.log")[1][:2]:
            fixed_line = line.replace("console.log", "console.log(") + ")"
        
        # Fix var to let/const
        if stripped.startswith("var "):
            fixed_line = line.replace("var ", "let ")
        
        fixed_lines.append(fixed_line)
    
    return "\n".join(fixed_lines)


def auto_fix_c_cpp(code, issues):
    """Auto-fix common C/C++ errors with comprehensive fixes."""
    fixed_lines = []
    lines = code.splitlines()
    
    for i, line in enumerate(lines):
        fixed_line = line
        stripped = line.strip()
        
        # Skip empty lines and preprocessor directives
        if not stripped or stripped.startswith("#"):
            fixed_lines.append(fixed_line)
            continue
        
        # Fix function declarations - add parentheses (do this FIRST before other checks)
        if ("int main" in stripped or "void main" in stripped) and "main" in stripped and "(" not in stripped:
            fixed_line = line.replace("main", "main()")
            stripped = fixed_line.strip()  # Update stripped for next checks
        
        # Add missing opening brace for main function
        if (stripped == "int main()" or stripped == "void main()") and i + 1 < len(lines):
            next_line = lines[i + 1].strip()
            if next_line and not next_line.startswith("{"):
                fixed_line = fixed_line + " {"
                stripped = fixed_line.strip()  # Update stripped
        
        # Add missing semicolons for variable declarations and statements
        if stripped and not stripped.endswith((";", "{", "}", ":", "//", "/*", "*/", "()")):
            # Skip if it's a function declaration (has main in it)
            if "main" in stripped and "(" in stripped:
                fixed_lines.append(fixed_line)
                continue
            # Variable declarations
            if re.match(r"^(int|float|char|double|long|short|unsigned)\s+\w+", stripped):
                if "=" in stripped:  # assignment
                    fixed_line = line if line.endswith(";") else line + ";"
                elif not "(" in stripped:  # simple declaration
                    fixed_line = line if line.endswith(";") else line + ";"
            # Function calls (printf, scanf, etc.)
            elif re.search(r"\w+\s*\([^)]*\)", stripped):
                fixed_line = line + ";"
            # return statements
            elif stripped.startswith("return"):
                fixed_line = line + ";"
        
        # Fix printf/scanf - add missing closing parenthesis
        if ("printf" in stripped or "scanf" in stripped) and "(" in stripped:
            open_count = stripped.count("(")
            close_count = stripped.count(")")
            if open_count > close_count:
                fixed_line = line + ")" * (open_count - close_count)
                if not fixed_line.rstrip().endswith(";"):
                    fixed_line = fixed_line + ";"
        
        # Add closing brace if missing
        if i == len(lines) - 1 and "}" not in stripped:
            fixed_lines.append(fixed_line)
            fixed_lines.append("}")
            continue
        
        fixed_lines.append(fixed_line)
    
    return "\n".join(fixed_lines)


@app.route("/debug", methods=["POST"])
def debug_code():
    data = request.json
    code = data.get("code", "")
    language = data.get("language", "python").lower().strip()
    
    if not code:
        return jsonify({
            "issues": "⚠️ No code provided.",
            "fixed_code": "",
            "original_code": ""
        })
    
    # Map language names
    lang_map = {
        "python": "python",
        "javascript": "javascript",
        "javascript (node.js 12.14.0)": "javascript",
        "java": "java",
        "java (openjdk 13.0.1)": "java",
        "c++": "cpp",
        "cpp": "cpp",
        "c": "c"
    }
    language = lang_map.get(language, "python")
    
    # Create a temporary file for linter analysis
    ext_map = {
        "python": ".py",
        "javascript": ".js",
        "java": ".java",
        "cpp": ".cpp",
        "c": ".c"
    }

    ext = ext_map.get(language, ".txt")
    tmpfile = None
    linter_output = ""
    
    try:
        # For JavaScript with ESLint v9, create temp file in current directory to avoid ignore issues
        if language == "javascript":
            tmpfile = os.path.join(os.path.dirname(__file__), f"_temp_eslint{ext}")
            with open(tmpfile, "w", encoding="utf-8") as f:
                f.write(code)
        else:
            with tempfile.NamedTemporaryFile(delete=False, suffix=ext, mode="w", encoding="utf-8") as f:
                f.write(code)
                f.flush()
                tmpfile = f.name

        # Run appropriate linter
        if language == "python":
            cmd = ["pylint", "--disable=R,C", tmpfile]
        elif language == "javascript":
            # Try to find eslint - check PATH and common npm installation paths
            eslint_cmd = None
            eslint_paths = [
                "eslint",  # In PATH
                r"C:\Users\aruns\AppData\Roaming\npm\eslint.cmd",
                "node_modules\\.bin\\eslint.cmd",  # Local installation
            ]
            
            for path in eslint_paths:
                try:
                    # Quick test if this path works
                    test_result = subprocess.run([path, "--version"], 
                                                capture_output=True, timeout=5)
                    if test_result.returncode == 0:
                        eslint_cmd = path
                        break
                except (FileNotFoundError, subprocess.TimeoutExpired):
                    continue
            
            if eslint_cmd:
                # For ESLint v9, suppress ignore warnings for temp files
                config_path = os.path.join(os.path.dirname(__file__), "eslint.config.js")
                if os.path.exists(config_path):
                    cmd = [eslint_cmd, tmpfile, "--no-color", "--config", config_path, "--no-warn-ignored"]
                else:
                    cmd = [eslint_cmd, tmpfile, "--no-color", "--no-warn-ignored"]
            else:
                linter_output = ("⚠️ eslint not found.\n\n"
                               "To install eslint:\n"
                               "1. Install Node.js from: https://nodejs.org/\n"
                               "2. Run: npm install -g eslint\n"
                               "3. Create config: npm init @eslint/config\n\n"
                               "Your code will still be auto-fixed below.")
                cmd = None
        elif language in ["c", "cpp"]:
            # Try to find cppcheck - check common Windows installation paths
            cppcheck_paths = [
                "cppcheck",  # In PATH
                r"C:\Program Files\Cppcheck\cppcheck.exe",
                r"C:\Program Files (x86)\Cppcheck\cppcheck.exe",
            ]
            cppcheck_cmd = None
            for path in cppcheck_paths:
                try:
                    # Quick test if this path works
                    test_result = subprocess.run([path, "--version"], 
                                                capture_output=True, timeout=5)
                    if test_result.returncode == 0:
                        cppcheck_cmd = path
                        break
                except (FileNotFoundError, subprocess.TimeoutExpired):
                    continue
            
            if cppcheck_cmd:
                cmd = [cppcheck_cmd, "--enable=all", "--quiet", tmpfile]
            else:
                linter_output = ("⚠️ cppcheck not found.\n\n"
                               "To install cppcheck on Windows:\n"
                               "1. Download from: https://github.com/danmar/cppcheck/releases\n"
                               "2. Install and add to PATH\n"
                               "3. Or install via: winget install cppcheck\n\n"
                               "Code will still be auto-fixed below.")
                cmd = None
        elif language == "java":
            # For Java, we'll use javac for basic syntax checking instead of checkstyle
            # javac is included with JDK and doesn't require separate installation
            java_compiler = None
            javac_paths = [
                "javac",  # In PATH
                r"C:\Program Files\Java\jdk-21\bin\javac.exe",
                r"C:\Program Files\Java\jdk-17\bin\javac.exe",
                r"C:\Program Files\Java\jdk-11\bin\javac.exe",
            ]
            
            for path in javac_paths:
                try:
                    test_result = subprocess.run([path, "-version"], 
                                                capture_output=True, timeout=5)
                    if test_result.returncode == 0:
                        java_compiler = path
                        break
                except (FileNotFoundError, subprocess.TimeoutExpired):
                    continue
            
            if java_compiler:
                # Use javac to check syntax
                cmd = [java_compiler, "-Xlint", tmpfile]
            else:
                linter_output = ("⚠️ Java compiler (javac) not found.\n\n"
                               "To enable Java analysis:\n"
                               "1. Install JDK (Java Development Kit)\n"
                               "2. Download from: https://www.oracle.com/java/technologies/downloads/\n"
                               "3. Or use: winget install Oracle.JDK.21\n"
                               "4. Add JAVA_HOME/bin to PATH\n\n"
                               "Your code will still be auto-fixed below.")
                cmd = None
        else:
            linter_output = f"⚠️ Unsupported language: {language}"
            cmd = None

        if cmd:
            try:
                result = subprocess.run(
                    cmd, 
                    stdout=subprocess.PIPE, 
                    stderr=subprocess.PIPE, 
                    text=True, 
                    timeout=20
                )
                linter_output = result.stdout.strip() or result.stderr.strip()
                
                if not linter_output:
                    linter_output = "✅ No issues found! Your code looks good."
                else:
                    # Clean up linter output - remove file paths and module references
                    linter_output = linter_output.replace(tmpfile, "")
                    # Remove "Module tmpXXX" lines
                    lines = linter_output.split("\n")
                    cleaned_lines = []
                    for line in lines:
                        if "Module tmp" in line and line.strip().startswith("*"):
                            continue  # Skip module header lines
                        if "your_code" in line:
                            line = line.replace("your_code" + ext, "Line")
                        cleaned_lines.append(line)
                    linter_output = "\n".join(cleaned_lines).strip()
                    
            except FileNotFoundError as e:
                if language in ["c", "cpp"]:
                    linter_output = ("⚠️ cppcheck not found in PATH.\n\n"
                                   "To install:\n"
                                   "• Download: https://github.com/danmar/cppcheck/releases\n"
                                   "• Or use: winget install cppcheck\n"
                                   "• Add installation folder to system PATH\n\n"
                                   "Your code will still be auto-fixed below.")
                elif language == "java":
                    linter_output = ("⚠️ Java compiler (javac) not found.\n\n"
                                   "To enable Java analysis:\n"
                                   "1. Install JDK (Java Development Kit)\n"
                                   "2. Download: https://www.oracle.com/java/technologies/downloads/\n"
                                   "3. Or install: winget install Oracle.JDK.21\n"
                                   "4. Add JAVA_HOME\\bin to PATH\n\n"
                                   "Your code will still be auto-fixed below.")
                elif language == "javascript":
                    linter_output = ("⚠️ eslint not found.\n\n"
                                   "To install eslint:\n"
                                   "1. Install Node.js from: https://nodejs.org/\n"
                                   "2. Run: npm install -g eslint\n"
                                   "3. Restart terminal\n\n"
                                   "Your code will still be auto-fixed below.")
                else:
                    linter_output = f"⚠️ Linter not installed for {language}. Please install the required tool.\n\n" \
                                  f"Your code will still be auto-fixed below."
            except subprocess.TimeoutExpired:
                linter_output = "⚠️ Linter analysis timed out."
            except Exception as e:
                linter_output = f"⚠️ Linter error: {str(e)}"

    except Exception as e:
        linter_output = f"❌ Error creating temp file: {str(e)}"
    finally:
        if tmpfile and os.path.exists(tmpfile):
            try:
                os.remove(tmpfile)
            except Exception:
                pass

    # Auto-fix code based on language - ALWAYS attempt fixes
    fixed_code = code
    try:
        if language == "python":
            fixed_code = auto_fix_python(code, linter_output)
        elif language == "javascript":
            fixed_code = auto_fix_javascript(code, linter_output)
        elif language == "java":
            fixed_code = auto_fix_java(code, linter_output)
        elif language in ["c", "cpp"]:
            fixed_code = auto_fix_c_cpp(code, linter_output)
        else:
            # For unsupported languages, still return the code without comments
            fixed_code = code
            
        # NEVER add comments - just return the fixed code as-is
        # Even if no changes were made, return clean code
            
    except Exception as e:
        # On error, still return original code without error comments
        fixed_code = code

    return jsonify({
        "issues": linter_output,
        "fixed_code": fixed_code,
        "original_code": code
    })

if __name__ == "__main__":
    app.run(debug=True, threaded=True)
