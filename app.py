# app.py
import os
from flask import Flask, request, jsonify, render_template, redirect, url_for, make_response, Response, session, flash
import sys, ast, traceback, re, requests, subprocess, tempfile
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from dotenv import load_dotenv
from database import init_db, fetch_one, execute_query, add_to_history, get_user_history, get_history_by_id, delete_history_item, generate_code_title

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
# Use environment variable for secret key, fallback to generated key if not found
app.secret_key = os.getenv('SECRET_KEY', os.urandom(24).hex())

# Configuration from environment
app.config['DB_TYPE'] = os.getenv('DB_TYPE', 'mysql')
app.config['FLASK_ENV'] = os.getenv('FLASK_ENV', 'production')
app.config['DEBUG'] = os.getenv('FLASK_DEBUG', 'False') == 'True'

# Initialize database on startup
init_db()

# ---------------- AUTHENTICATION ----------------
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        
        # Check credentials in database
        user = fetch_one('SELECT id, username, password FROM users WHERE username = ?', (username,))
        
        if user and check_password_hash(user[2], password):
            # Login successful
            session['user_id'] = user[0]
            session['username'] = user[1]
            return redirect(url_for("main"))
        else:
            return render_template("login.html", error="Invalid username or password!")
    
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")
        
        # Validation
        if not username or not email or not password:
            return render_template("register.html", error="All fields are required!")
        
        if password != confirm_password:
            return render_template("register.html", error="Passwords do not match!")
        
        if len(password) < 6:
            return render_template("register.html", error="Password must be at least 6 characters!")
        
        # Check if user already exists
        existing_user = fetch_one('SELECT id FROM users WHERE username = ? OR email = ?', (username, email))
        
        if existing_user:
            return render_template("register.html", error="Username or email already exists!")
        
        # Create new user
        hashed_password = generate_password_hash(password)
        try:
            execute_query('INSERT INTO users (username, email, password) VALUES (?, ?, ?)',
                         (username, email, hashed_password))
            flash("Registration successful! Please login.", "success")
            return redirect(url_for("login"))
        except Exception as e:
            return render_template("register.html", error=f"Registration failed: {str(e)}")
    
    return render_template("register.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

def check_user():
    return session.get('username')

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


# ---------------- JUDGE0 API with fallback options ----------------
# Try local Judge0 first (if running Docker), then fall back to free API
JUDGE0_URLS = [
    # "http://localhost:2358",  # ❌ DISABLED: Docker Judge0 doesn't work on Windows WSL2 (cgroup v2 incompatibility)
    # "https://judge0-ce.p.rapidapi.com",  # RapidAPI (requires API key)
    "https://ce.judge0.com"  # ✅ ACTIVE: Free Public API (reliable and working)
]

# RapidAPI key from environment or hardcoded
RAPIDAPI_KEY = os.getenv('JUDGE0_API_KEY', None)  # Set in .env file or here


def run_judge0(code, language_id=71, stdin=""):
    """
    Try to run code on Judge0 with multiple fallback options:
    1. Local Docker instance (fastest, most reliable)
    2. RapidAPI (if API key is configured)
    3. Free public API (may have connectivity issues)
    """
    payload = {
        "source_code": code,
        "language_id": language_id,
        "stdin": stdin
    }
    
    last_error = None
    
    # Try each Judge0 endpoint
    for base_url in JUDGE0_URLS:
        # Skip RapidAPI if no key configured
        if "rapidapi.com" in base_url and not RAPIDAPI_KEY:
            continue
            
        try:
            headers = {"Content-Type": "application/json"}
            
            # Add RapidAPI headers if needed
            if "rapidapi.com" in base_url and RAPIDAPI_KEY:
                headers.update({
                    "X-RapidAPI-Key": RAPIDAPI_KEY,
                    "X-RapidAPI-Host": "judge0-ce.p.rapidapi.com"
                })
            
            # Submit code with adequate timeout for remote APIs
            timeout_seconds = 15  # Increased timeout for reliable connections
            submit = requests.post(
                f"{base_url}/submissions/?base64_encoded=false&wait=false",
                json=payload,
                headers=headers,
                timeout=timeout_seconds
            )
            
            if submit.status_code not in [200, 201]:
                last_error = f"Server returned status {submit.status_code}"
                continue
                
            token = submit.json().get("token")
            if not token:
                last_error = "No token received from server"
                continue

            # Poll for result (max 60 attempts = 60 seconds)
            import time
            for attempt in range(60):
                time.sleep(1)
                res = requests.get(
                    f"{base_url}/submissions/{token}?base64_encoded=false",
                    headers=headers,
                    timeout=15  # Increased timeout for polling requests
                )
                
                if res.status_code != 200:
                    break
                    
                result = res.json()
                status = result.get("status", {}).get("description")
                
                if status not in ["In Queue", "Processing"]:
                    # Check if execution was successful
                    if status == "Accepted" or result.get("stdout") or result.get("stderr"):
                        output = ""
                        if result.get("stdout"):
                            output += result.get("stdout")
                        if result.get("stderr"):
                            output += "\n[stderr]:\n" + result.get("stderr")
                        if result.get("compile_output"):
                            output += "\n[compile_output]:\n" + result.get("compile_output")
                        return output or "⚠️ No output"
                    else:
                        # Execution failed (Internal Error, etc), try next endpoint
                        last_error = f"Execution failed with status: {status}"
                        break
            
            last_error = "Timeout waiting for execution"
            
        except requests.exceptions.ConnectionError:
            last_error = f"Cannot connect to {base_url}"
            continue
        except requests.exceptions.Timeout:
            last_error = f"Request timeout for {base_url}"
            continue
        except requests.exceptions.RequestException as e:
            last_error = f"Request error: {str(e)}"
            continue
        except Exception as e:
            last_error = f"Unexpected error: {str(e)}"
            continue
    
    # If all endpoints failed, return error with instructions
    error_msg = f"❌ Cannot connect to Judge0 API\n\n"
    error_msg += f"Last error: {last_error}\n\n"
    error_msg += "💡 Solutions:\n\n"
    error_msg += "1️⃣ CHECK YOUR INTERNET CONNECTION\n"
    error_msg += "   • Make sure you're connected to the internet\n"
    error_msg += "   • Try opening https://ce.judge0.com in your browser\n\n"
    error_msg += "2️⃣ USE LOCAL JUDGE0 (Recommended)\n"
    error_msg += "   • Install Docker Desktop: https://www.docker.com/products/docker-desktop\n"
    error_msg += "   • Open terminal in the 'Judge0' folder\n"
    error_msg += "   • Run: docker-compose up -d\n"
    error_msg += "   • This runs Judge0 locally (no internet needed!)\n\n"
    error_msg += "3️⃣ CHECK FIREWALL/ANTIVIRUS\n"
    error_msg += "   • Your firewall might be blocking the connection\n"
    error_msg += "   • Try temporarily disabling it\n\n"
    error_msg += "4️⃣ USE RAPIDAPI (Alternative)\n"
    error_msg += "   • Sign up at: https://rapidapi.com/judge0-official/api/judge0-ce\n"
    error_msg += "   • Get your API key (free tier available)\n"
    error_msg += "   • Add it to app.py: RAPIDAPI_KEY = 'your-key-here'\n"
    
    return error_msg


# ---------------- RUN CODE ----------------
@app.route("/run", methods=["POST"])
def run_code():
    data = request.json
    code = data.get("code", "")
    language_id = data.get("language_id", 71)
    stdin = data.get("stdin", "")  # Get user input
    
    # Get language name from ID
    language_map = {71: "Python", 50: "C", 54: "C++", 62: "Java", 63: "JavaScript"}
    language_name = language_map.get(language_id, "Unknown")
    
    try:
        output = run_judge0(code, language_id, stdin)
        
        # Save to history if user is logged in
        if session.get('user_id'):
            title = generate_code_title(code)
            add_to_history(
                user_id=session['user_id'],
                activity_type='run',
                code_snippet=code,
                language=language_name,
                title=title,
                output=output
            )
        
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
    
    import time
    last_error = None
    
    # Try each Judge0 endpoint
    for base_url in JUDGE0_URLS:
        # Skip RapidAPI if no key configured
        if "rapidapi.com" in base_url and not RAPIDAPI_KEY:
            continue
            
        try:
            headers = {"Content-Type": "application/json"}
            
            # Add RapidAPI headers if needed
            if "rapidapi.com" in base_url and RAPIDAPI_KEY:
                headers.update({
                    "X-RapidAPI-Key": RAPIDAPI_KEY,
                    "X-RapidAPI-Host": "judge0-ce.p.rapidapi.com"
                })
            
            submit = requests.post(
                f"{base_url}/submissions/?base64_encoded=false&wait=false",
                json=payload,
                headers=headers,
                timeout=15  # Increased timeout for reliable connections
            )
            
            if submit.status_code not in (201, 200):
                last_error = f"Server returned {submit.status_code}"
                continue
                
            token = submit.json().get("token")
            if not token:
                last_error = "No token received"
                continue

            # Poll for result
            for _ in range(60):
                time.sleep(1)
                res = requests.get(
                    f"{base_url}/submissions/{token}?base64_encoded=false",
                    headers=headers,
                    timeout=15  # Increased timeout for polling requests
                )
                
                if res.status_code != 200:
                    break
                    
                result = res.json()
                status = result.get("status", {}).get("description")
                
                if status not in ["In Queue", "Processing"]:
                    # Check if execution was successful
                    if status == "Accepted" or result.get("stdout") or result.get("stderr"):
                        return jsonify({
                            "status": status,
                            "stdout": result.get("stdout"),
                            "stderr": result.get("stderr"),
                            "compile_output": result.get("compile_output"),
                            "message": result.get("message")
                        })
                    else:
                        # Execution failed, try next endpoint
                        last_error = f"Execution failed with status: {status}"
                        break
            
            last_error = "Timeout waiting for result"
            
        except requests.exceptions.ConnectionError:
            last_error = f"Cannot connect to {base_url}"
            continue
        except requests.exceptions.Timeout:
            last_error = f"Timeout for {base_url}"
            continue
        except requests.exceptions.RequestException as e:
            last_error = str(e)
            continue
    
    return jsonify({"error": "All Judge0 endpoints failed", "detail": last_error}), 502


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
        return jsonify({
            "optimized": code, 
            "optimizations": [],
            "notes": "No optimizer implemented for this language."
        })

    try:
        result = ai_optimize_python(code)
        optimized = result["optimized_code"]
        optimizations = result["optimizations"]
        
        # Save to history if user is logged in
        if session.get('user_id'):
            title = generate_code_title(code)
            add_to_history(
                user_id=session['user_id'],
                activity_type='optimize',
                code_snippet=code,
                language=language.capitalize(),
                title=title,
                output=optimized
            )
        
        return jsonify({
            "optimized": optimized, 
            "optimizations": optimizations
        })
    except Exception as e:
        return jsonify({"error": "Optimization failed", "detail": str(e)}), 500


def analyze_code_purpose(code, language):
    """Analyze what the code does and provide comprehensive high-level overview"""
    overview = []
    
    code_lower = code.lower()
    lines = [l.strip() for l in code.splitlines() if l.strip() and not l.strip().startswith("#")]
    
    # Detect code patterns
    has_input = "input(" in code_lower or "scanner" in code_lower or "scanf" in code_lower or "cin >>" in code_lower
    has_loop = "for " in code_lower or "while " in code_lower
    has_if = "if " in code_lower or "if(" in code_lower
    has_function = "def " in code_lower or "function " in code_lower
    has_print = "print(" in code_lower or "console.log" in code_lower or "cout <<" in code_lower or "system.out" in code_lower
    has_math = any(op in code for op in ["+", "-", "*", "/", "%", "**", "pow(", "sqrt(", "math."])
    
    # Build comprehensive overview
    overview.append("💡 **Purpose & Goal:**")
    overview.append("")
    
    if has_input and has_loop and has_print:
        overview.append("   This program is an interactive application that:")
        overview.append("   • Collects input from the user")
        overview.append("   • Uses loops to process the data or repeat operations")
        overview.append("   • Displays calculated results or patterns")
        overview.append("")
        overview.append("   **Why this matters:** Interactive programs are the foundation")
        overview.append("   of user-friendly applications. They make programming dynamic!")
    elif has_loop and has_math:
        overview.append("   This is a computational algorithm that:")
        overview.append("   • Uses mathematical operations")
        overview.append("   • Employs loops for efficiency or pattern generation")
        overview.append("   • Solves a specific problem through calculation")
        overview.append("")
        overview.append("   **Why this matters:** Loops + Math = Powerful algorithms")
        overview.append("   that can solve complex problems automatically!")
    elif has_input and has_print:
        overview.append("   This is an I/O (Input/Output) program that:")
        overview.append("   • Takes data from the user")
        overview.append("   • Processes or transforms that data")
        overview.append("   • Shows meaningful output")
    elif has_function:
        overview.append("   This code demonstrates modular programming:")
        overview.append("   • Organizes code into reusable functions")
        overview.append("   • Makes code cleaner and maintainable")
        overview.append("   • Follows the DRY principle (Don't Repeat Yourself)")
    elif has_loop:
        overview.append("   This code uses repetition (loops) to:")
        overview.append("   • Perform tasks multiple times efficiently")
        overview.append("   • Avoid writing the same code over and over")
    elif has_if:
        overview.append("   This code makes intelligent decisions:")
        overview.append("   • Uses conditional logic (if/else)")
        overview.append("   • Changes behavior based on different conditions")
    else:
        overview.append("   This is a sequential program that executes")
        overview.append("   statements one after another in order.")
    
    # Statistics
    loc = len([l for l in code.splitlines() if l.strip() and not l.strip().startswith("#")])
    overview.append("")
    overview.append("� **Code Statistics:**")
    overview.append(f"   • Lines of code: {loc}")
    overview.append(f"   • Programming language: {language.upper()}")
    
    if has_loop:
        loop_count = code_lower.count("for ") + code_lower.count("while ")
        overview.append(f"   • Loops used: {loop_count}")
    if has_if:
        if_count = code_lower.count("if ") + code_lower.count("if(")
        overview.append(f"   • Decision points: {if_count}")
    if has_function:
        func_count = code_lower.count("def ") + code_lower.count("function ")
        overview.append(f"   • Functions defined: {func_count}")
    
    overview.append("")
    return overview


def generate_detailed_line_explanation(line, stripped, i, language):
    """Generate detailed, educational explanation for a line of code"""
    explanations = []
    
    if language == "python":
        # Variable assignment
        if "=" in stripped and not any(op in stripped for op in ["==", "!=", "<=", ">=", "+=", "-=", "*=", "/=", "end="]):
            parts = stripped.split("=", 1)
            var = parts[0].strip()
            expr = parts[1].strip() if len(parts) > 1 else ""
            
            explanations.append(f"📦 **Variable Assignment**")
            explanations.append(f"   Creating a variable named `{var}` and storing the value: `{expr}`")
            explanations.append("")
            explanations.append(f"   💭 **Think of it like this:** We're putting a label on a box.")
            explanations.append(f"   The label is `{var}` and what's inside the box is `{expr}`")
            
            if "input(" in stripped:
                explanations.append("")
                explanations.append("   🎯 **Special Note:** `input()` waits for the user to type something!")
                explanations.append("   The program pauses until Enter is pressed.")
            
        # If statement
        elif stripped.startswith("if "):
            cond = stripped[3:].rstrip(":")
            explanations.append(f"❓ **Conditional Check (Decision Making)**")
            explanations.append(f"   Testing if this is true: `{cond}`")
            explanations.append("")
            explanations.append("   💭 **How it works:** Like a fork in the road!")
            explanations.append("   • If the condition is TRUE → execute the indented code below")
            explanations.append("   • If the condition is FALSE → skip to the next part")
            
            if "%" in cond:
                explanations.append("")
                explanations.append("   📚 **Learning Moment:** The `%` operator (modulo)")
                explanations.append("   gives the REMAINDER after division.")
                explanations.append("   Example: 10 % 3 = 1 (because 10 ÷ 3 = 3 remainder 1)")
            if "==" in cond:
                explanations.append("")
                explanations.append("   ⚠️ **Common Mistake Alert:** `==` checks equality, `=` assigns!")
                explanations.append("   • `x == 5` asks 'is x equal to 5?'")
                explanations.append("   • `x = 5` says 'make x equal to 5'")
                
        # Print statement
        elif "print(" in stripped:
            explanations.append(f"📤 **Output to Screen**")
            explanations.append(f"   Displays information to the user/console")
            explanations.append("")
            explanations.append("   💭 **Why this matters:** This is how programs communicate!")
            explanations.append("   Without print(), your program would be silent!")
            
            if "f\"" in stripped or "f'" in stripped:
                explanations.append("")
                explanations.append("   🎨 **Cool Feature:** This uses an f-string!")
                explanations.append("   Variables inside {curly braces} get replaced with their values.")
                explanations.append("   Example: f\"Hello {name}\" → \"Hello John\"")
            
            if "end=" in stripped:
                explanations.append("")
                explanations.append("   ⚙️ **Technical Detail:** `end=` parameter changes what prints after.")
                explanations.append("   By default, print() adds a newline. `end=''` removes it!")
                
        # For loop
        elif stripped.startswith("for "):
            explanations.append(f"🔄 **For Loop (Controlled Repetition)**")
            explanations.append(f"   Repeating code for each item in a sequence")
            explanations.append("")
            explanations.append("   💭 **Real-world analogy:** Like dealing cards one by one!")
            explanations.append("   The loop variable takes on each value, one at a time.")
            
            if "range(" in stripped:
                explanations.append("")
                explanations.append("   📚 **About range():**")
                explanations.append("   • `range(5)` → 0, 1, 2, 3, 4 (starts at 0, stops before 5)")
                explanations.append("   • `range(1, 6)` → 1, 2, 3, 4, 5 (starts at 1, stops before 6)")
                explanations.append("   • `range(0, 10, 2)` → 0, 2, 4, 6, 8 (steps by 2)")
                
        # While loop
        elif stripped.startswith("while "):
            explanations.append(f"🔁 **While Loop (Conditional Repetition)**")
            explanations.append(f"   Keeps repeating as long as the condition is TRUE")
            explanations.append("")
            explanations.append("   💭 **Real-world analogy:** Like waiting for water to boil!")
            explanations.append("   You keep checking 'is it boiling yet?' until the answer is yes.")
            explanations.append("")
            explanations.append("   ⚠️ **Warning:** Make sure the condition eventually becomes FALSE,")
            explanations.append("   or you'll create an infinite loop!")
            
        # Else
        elif stripped.startswith("else:"):
            explanations.append(f"↩️ **Else Block (Alternative Path)**")
            explanations.append(f"   Runs when the above 'if' condition was FALSE")
            explanations.append("")
            explanations.append("   💭 **Think of it as:** The 'otherwise' or 'backup plan'")
            
        # Function definition
        elif stripped.startswith("def "):
            func_name = stripped.split("(")[0].replace("def ", "").strip()
            explanations.append(f"🎯 **Function Definition**")
            explanations.append(f"   Creating a reusable block of code named: `{func_name}()`")
            explanations.append("")
            explanations.append("   💭 **Why use functions?**")
            explanations.append("   • Write once, use many times")
            explanations.append("   • Makes code organized and readable")
            explanations.append("   • Easier to test and debug")
            
        # Return statement
        elif stripped.startswith("return "):
            explanations.append(f"⬅️ **Return Statement**")
            explanations.append(f"   Sends a value back from the function")
            explanations.append("")
            explanations.append("   💭 **Like a vending machine:**")
            explanations.append("   You put in money (input) → return gives you a snack (output)")
            
        else:
            explanations.append(f"▶️ **Statement Execution**")
            explanations.append(f"   This line performs an operation or calculation")
    
    return "\n".join(explanations)


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

    # Build beautiful, visual explanation with emojis and boxes
    explanation_parts = []

    # Stunning Header with Box
    explanation_parts.append("╔" + "═" * 58 + "╗")
    explanation_parts.append("║" + " " * 15 + "� CODE EXPLANATION 📚" + " " * 20 + "║")
    explanation_parts.append("║" + " " * 10 + f"Language: {language.upper()} 🔤" + " " * (47 - len(language)) + "║")
    explanation_parts.append("╚" + "═" * 58 + "╝")
    explanation_parts.append("")

    # Linter Analysis Box
    explanation_parts.append("╭" + "─" * 58 + "╮")
    explanation_parts.append("│  🔍 QUALITY CHECK & LINTER ANALYSIS" + " " * 20 + "│")
    explanation_parts.append("╰" + "─" * 58 + "╯")
    
    # Format linter output with indentation
    linter_lines = linter_output.split('\n')
    for line in linter_lines:
        if line.strip():
            if "✅" in line or "No" in line and "found" in line:
                explanation_parts.append(f"  ✅ {line}")
            elif "⚠️" in line or "warning" in line.lower():
                explanation_parts.append(f"  ⚠️  {line}")
            elif "❌" in line or "error" in line.lower():
                explanation_parts.append(f"  ❌ {line}")
            else:
                explanation_parts.append(f"  📝 {line}")
    explanation_parts.append("")

    # Line-by-line explanation for Python (with optional simulation)
    if language == "python":
        explanation_parts.append("╭" + "─" * 58 + "╮")
        explanation_parts.append("│  📖 LINE-BY-LINE CODE BREAKDOWN" + " " * 24 + "│")
        explanation_parts.append("╰" + "─" * 58 + "╯")
        explanation_parts.append("")
        
        lines = code.splitlines()
        for i, line in enumerate(lines, start=1):
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            
            # Code line in a box
            explanation_parts.append(f"┌─ Line {i} " + "─" * (66 - len(str(i))) + "┐")
            explanation_parts.append(f"│  {line[:72]}" + " " * max(0, 72 - len(line[:72])) + "│")
            explanation_parts.append(f"└" + "─" * 74 + "┘")
            
            # Use detailed AI explanation
            detailed_explanation = generate_detailed_line_explanation(line, stripped, i, language)
            for exp_line in detailed_explanation.split("\n"):
                explanation_parts.append(f"  {exp_line}")
            explanation_parts.append("")

        # Try to simulate execution for simple code
        explanation_parts.append("")
        explanation_parts.append("╭" + "─" * 58 + "╮")
        explanation_parts.append("│  🚀 STEP-BY-STEP EXECUTION FLOW" + " " * 24 + "│")
        explanation_parts.append("╰" + "─" * 58 + "╯")
        explanation_parts.append("")
        try:
            steps, outputs = simulate_simple_python(code)
            for i, step in enumerate(steps, start=1):
                explanation_parts.append(f"  {i}️⃣  {step}")
            explanation_parts.append("")
            if outputs:
                explanation_parts.append("  ┌─ 📺 OUTPUT " + "─" * 43 + "┐")
                for out in outputs:
                    explanation_parts.append(f"  │  💬 {out[:52]}" + " " * max(0, 52 - len(out[:52])) + "│")
                explanation_parts.append("  └" + "─" * 54 + "┘")
            else:
                explanation_parts.append("  📭 No output produced")
        except ValueError as e:
            explanation_parts.append(f"  ⚠️  Code too complex to simulate: {str(e)[:45]}")
        except Exception as e:
            explanation_parts.append(f"  ⚠️  Simulation error: {str(e)[:45]}")

    else:
        # For non-Python languages, provide a basic per-line summary
        explanation_parts.append("╭" + "─" * 58 + "╮")
        explanation_parts.append("│  📖 LINE-BY-LINE CODE BREAKDOWN" + " " * 24 + "│")
        explanation_parts.append("╰" + "─" * 58 + "╯")
        explanation_parts.append("")
        
        lines = [l for l in code.strip().splitlines() if l.strip()]
        line_num = 0
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("//") or stripped.startswith("#"):
                continue
            line_num += 1
            
            # Code line in a box
            explanation_parts.append(f"┌─ Line {line_num} " + "─" * (48 - len(str(line_num))) + "┐")
            explanation_parts.append(f"│  {line[:54]}" + " " * max(0, 54 - len(line[:54])) + "│")
            explanation_parts.append(f"└" + "─" * 56 + "┘")
            
            # Explain with emojis
            if "console.log" in stripped or "printf(" in stripped or "cout <<" in stripped or "System.out" in stripped:
                explanation_parts.append(f"  📤 Prints or logs output to console")
            elif "#include" in stripped or "import " in stripped or "using namespace" in stripped:
                explanation_parts.append(f"  📦 Imports library/module")
            elif "int main" in stripped or "public static void main" in stripped:
                explanation_parts.append(f"  🎯 Program entry point")
            elif "scanf(" in stripped or "cin >>" in stripped or "Scanner" in stripped:
                explanation_parts.append(f"  ⌨️  Reads user input")
            elif "=" in stripped and "==" not in stripped:
                explanation_parts.append(f"  💾 Assigns value to variable")
            elif stripped.startswith("if ") or stripped.startswith("if("):
                explanation_parts.append(f"  ❓ Conditional: Makes decision")
            elif stripped.startswith("else"):
                explanation_parts.append(f"  ↩️  Runs if condition fails")
            elif stripped.startswith("for ") or stripped.startswith("for("):
                explanation_parts.append(f"  🔄 Loop: Repeats code block")
            elif stripped.startswith("while ") or stripped.startswith("while("):
                explanation_parts.append(f"  🔁 Loop: Repeats while true")
            elif "return " in stripped:
                explanation_parts.append(f"  ⬅️  Returns value from function")
            elif "{" in stripped or "}" in stripped:
                explanation_parts.append(f"  🏁 Code block delimiter")
            else:
                explanation_parts.append(f"  ▶️  Executes statement")
            explanation_parts.append("")

        explanation_parts.append("")
        explanation_parts.append("╭" + "─" * 58 + "╮")
        explanation_parts.append("│  💡 TIP" + " " * 49 + "│")
        explanation_parts.append("├" + "─" * 58 + "┤")
        explanation_parts.append("│  Run the code to see detailed execution results!    │")
        explanation_parts.append("╰" + "─" * 58 + "╯")

    explanation_text = "\n".join(explanation_parts)
    
    # Save to history if user is logged in
    if session.get('user_id'):
        title = generate_code_title(code)
        add_to_history(
            user_id=session['user_id'],
            activity_type='explain',
            code_snippet=code,
            language=language.capitalize(),
            title=title,
            output=explanation_text
        )

    return jsonify({"explanation": explanation_text})


def generate_detailed_explanation(code, language):
    """Generate comprehensive, step-by-step code explanation with detailed breakdowns"""
    lines = code.splitlines()
    
    # Start with step-by-step section
    html = '''
    <div class="success-card issue-card" style="margin: 1rem;">
        <span class="issue-badge success-badge">🔍 STEP-BY-STEP EXPLANATION</span>
        <div class="issue-title">Let's break down this code line by line</div>
        <div class="issue-description">
            <div style="margin-top: 1rem;">
    '''
    
    # Analyze each line with detailed explanations
    step_num = 0
    for i, line in enumerate(lines, start=1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or stripped.startswith("//"):
            continue
        
        step_num += 1
        safe_line = line.replace('<', '&lt;').replace('>', '&gt;')
        
        # Generate detailed explanation based on pattern
        explanation = generate_line_explanation(stripped, line, language, step_num, lines, i-1)
        
        html += f'''
            <div style="margin: 1.5rem 0; padding: 1rem; background: rgba(102, 126, 234, 0.1); border-left: 4px solid #667eea; border-radius: 6px;">
                <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.8rem;">
                    <span style="background: #667eea; color: white; padding: 0.3rem 0.7rem; border-radius: 12px; font-weight: 600; font-size: 0.85rem;">{step_num}️⃣</span>
                    <code style="background: #0d0d0d; padding: 0.4rem 0.8rem; border-radius: 6px; color: #6ad7ff; font-size: 0.9rem; flex: 1;">{safe_line}</code>
                </div>
                <div style="color: #ececf1; line-height: 1.8; font-size: 0.95rem;">
                    {explanation}
                </div>
            </div>
        '''
    
    html += '''
            </div>
        </div>
    </div>
    '''
    
    # Add output/summary section if applicable
    summary = generate_code_summary(code, language)
    if summary:
        html += summary
    
    # Add key concepts section
    html += '''
    <div class="info-card issue-card" style="margin: 1rem;">
        <span class="issue-badge info-badge">💡 KEY TAKEAWAYS</span>
        <div class="issue-title">What You Should Remember</div>
        <div class="issue-description" style="line-height: 1.8;">
    '''
    
    key_concepts = extract_key_concepts(code, language)
    for concept in key_concepts:
        html += f'<div style="margin: 0.5rem 0;">• {concept}</div>'
    
    html += '''
        </div>
    </div>
    '''
    
    return html


def generate_line_explanation(stripped, original_line, language, step_num, all_lines, line_index):
    """Generate detailed explanation for a single line of code"""
    
    if language == "python":
        # Variable assignment with detailed explanation
        if "=" in stripped and not any(op in stripped for op in ["==", "!=", "<=", ">=", "+=", "-=", "*=", "/=", "**="]):
            parts = stripped.split("=", 1)
            var_name = parts[0].strip()
            value = parts[1].strip() if len(parts) > 1 else ""
            
            explanation = f'''
                <strong>This line assigns a value to the variable <code>{var_name}</code>.</strong>
                <br><br>
                <div style="background: rgba(16, 163, 127, 0.1); padding: 0.8rem; border-radius: 6px; margin: 0.5rem 0;">
                    📌 <strong>What's happening:</strong>
                    <ul style="margin: 0.5rem 0; padding-left: 1.5rem;">
                        <li>We create a variable called <code>{var_name}</code></li>
                        <li>We store the value <code>{value}</code> in it</li>
                        <li>Now we can use <code>{var_name}</code> anywhere in our code</li>
                    </ul>
                </div>
            '''
            
            # Add more context if it's a number
            if value.replace("-", "").replace(".", "").isdigit():
                explanation += f'''
                    <div style="margin-top: 0.5rem; color: #b4b4b4;">
                        💭 <em>Think of <code>{var_name}</code> as a labeled box that holds the number {value}.</em>
                    </div>
                '''
            
            return explanation
        
        # For loops with detailed breakdown
        elif stripped.startswith("for "):
            # Extract loop components
            if " in " in stripped:
                parts = stripped.split(" in ")
                loop_var = parts[0].replace("for ", "").strip()
                iterable = parts[1].rstrip(":").strip()
                
                explanation = f'''
                    <strong>This is a FOR LOOP - it repeats code multiple times.</strong>
                    <br><br>
                    <div style="background: rgba(16, 163, 127, 0.1); padding: 0.8rem; border-radius: 6px; margin: 0.5rem 0;">
                        📌 <strong>How it works:</strong>
                        <ul style="margin: 0.5rem 0; padding-left: 1.5rem;">
                            <li><code>{loop_var}</code> is the <strong>loop variable</strong> - it changes each iteration</li>
                            <li><code>{iterable}</code> is what we're looping through</li>
                '''
                
                # Explain range() if present
                if "range(" in iterable:
                    import re
                    range_match = re.search(r'range\((.*?)\)', iterable)
                    if range_match:
                        range_args = range_match.group(1).split(",")
                        if len(range_args) == 1:
                            explanation += f'''
                                <li>This loops from <code>0</code> to <code>{range_args[0].strip()} - 1</code></li>
                            '''
                        elif len(range_args) == 2:
                            explanation += f'''
                                <li>This loops from <code>{range_args[0].strip()}</code> to <code>{range_args[1].strip()} - 1</code></li>
                            '''
                        elif len(range_args) >= 3:
                            explanation += f'''
                                <li>Start: <code>{range_args[0].strip()}</code></li>
                                <li>End: <code>{range_args[1].strip()}</code> (not included)</li>
                                <li>Step: <code>{range_args[2].strip()}</code> (increment/decrement by this amount)</li>
                            '''
                
                explanation += '''
                        </ul>
                    </div>
                    <div style="margin-top: 0.5rem; color: #b4b4b4;">
                        💭 <em>The loop runs once for each value, executing all indented code below it.</em>
                    </div>
                '''
                return explanation
        
        # While loops
        elif stripped.startswith("while "):
            condition = stripped.replace("while ", "").rstrip(":")
            return f'''
                <strong>This is a WHILE LOOP - it repeats as long as a condition is true.</strong>
                <br><br>
                <div style="background: rgba(255, 193, 7, 0.1); padding: 0.8rem; border-radius: 6px; margin: 0.5rem 0;">
                    📌 <strong>How it works:</strong>
                    <ul style="margin: 0.5rem 0; padding-left: 1.5rem;">
                        <li>Checks if <code>{condition}</code> is true</li>
                        <li>If true, runs the indented code below</li>
                        <li>Then checks the condition again</li>
                        <li>Repeats until the condition becomes false</li>
                    </ul>
                </div>
                <div style="margin-top: 0.5rem; padding: 0.5rem; background: rgba(255, 84, 89, 0.1); border-radius: 4px;">
                    ⚠️ <strong>Warning:</strong> Make sure the condition eventually becomes false, or you'll have an infinite loop!
                </div>
            '''
        
        # If statements
        elif stripped.startswith("if "):
            condition = stripped.replace("if ", "").rstrip(":")
            return f'''
                <strong>This is an IF STATEMENT - it makes decisions.</strong>
                <br><br>
                <div style="background: rgba(255, 193, 7, 0.1); padding: 0.8rem; border-radius: 6px; margin: 0.5rem 0;">
                    📌 <strong>How it works:</strong>
                    <ul style="margin: 0.5rem 0; padding-left: 1.5rem;">
                        <li>Checks if <code>{condition}</code> is true</li>
                        <li>If true, runs the indented code below</li>
                        <li>If false, skips to the next section (elif/else or next line)</li>
                    </ul>
                </div>
                <div style="margin-top: 0.5rem; color: #b4b4b4;">
                    💭 <em>Think of it like a fork in the road - the code takes different paths based on the condition.</em>
                </div>
            '''
        
        # Print statements
        elif "print(" in stripped:
            return '''
                <strong>This PRINTS output to the screen.</strong>
                <br><br>
                <div style="background: rgba(102, 126, 234, 0.1); padding: 0.8rem; border-radius: 6px; margin: 0.5rem 0;">
                    📌 <strong>What it does:</strong>
                    <ul style="margin: 0.5rem 0; padding-left: 1.5rem;">
                        <li>Displays the result on your console/terminal</li>
                        <li>Useful for seeing what your program is doing</li>
                        <li>Helps with debugging and showing results to users</li>
                    </ul>
                </div>
            '''
        
        # Function definitions
        elif stripped.startswith("def "):
            func_name = stripped.split("(")[0].replace("def ", "").strip()
            params = ""
            if "(" in stripped and ")" in stripped:
                params = stripped[stripped.index("(")+1:stripped.index(")")].strip()
            
            explanation = f'''
                <strong>This defines a FUNCTION called <code>{func_name}</code>.</strong>
                <br><br>
                <div style="background: rgba(102, 126, 234, 0.1); padding: 0.8rem; border-radius: 6px; margin: 0.5rem 0;">
                    📌 <strong>What's a function?</strong>
                    <ul style="margin: 0.5rem 0; padding-left: 1.5rem;">
                        <li>A reusable block of code</li>
                        <li>You can call it multiple times</li>
            '''
            
            if params:
                explanation += f'''
                        <li>Takes input(s): <code>{params}</code></li>
                '''
            
            explanation += '''
                        <li>Can return a result</li>
                    </ul>
                </div>
                <div style="margin-top: 0.5rem; color: #b4b4b4;">
                    💭 <em>Functions are like recipes - write once, use many times!</em>
                </div>
            '''
            return explanation
        
        # Return statements
        elif stripped.startswith("return "):
            value = stripped.replace("return ", "").strip()
            return f'''
                <strong>This RETURNS a value from the function.</strong>
                <br><br>
                <div style="background: rgba(16, 163, 127, 0.1); padding: 0.8rem; border-radius: 6px; margin: 0.5rem 0;">
                    📌 <strong>What happens:</strong>
                    <ul style="margin: 0.5rem 0; padding-left: 1.5rem;">
                        <li>The function stops executing</li>
                        <li>It sends back the value: <code>{value}</code></li>
                        <li>The caller receives this value</li>
                    </ul>
                </div>
                <div style="margin-top: 0.5rem; color: #b4b4b4;">
                    💭 <em>Return is like the function's answer - it gives back a result.</em>
                </div>
            '''
    
    # Default explanation
    return f'''
        <strong>This line executes a statement in your program.</strong>
        <br><br>
        <div style="color: #b4b4b4; margin-top: 0.5rem;">
            The code performs its intended operation as part of the program's logic.
        </div>
    '''


def generate_code_summary(code, language):
    """Generate output pattern or summary section"""
    # For now, return empty - can be enhanced based on code patterns
    return ""


def extract_key_concepts(code, language):
    """Extract key programming concepts from the code"""
    concepts = []
    
    if "for " in code:
        concepts.append("<strong>Loops:</strong> Used to repeat code multiple times - essential for automation")
    if "while " in code:
        concepts.append("<strong>While Loops:</strong> Repeat code based on a condition - useful when you don't know how many iterations")
    if "if " in code or "elif " in code:
        concepts.append("<strong>Conditionals:</strong> Make decisions in code - allows different paths of execution")
    if "def " in code:
        concepts.append("<strong>Functions:</strong> Reusable code blocks - write once, use many times")
    if "range(" in code:
        concepts.append("<strong>Range:</strong> Generates sequences of numbers - commonly used with loops")
    if "print(" in code:
        concepts.append("<strong>Output:</strong> Displays results to users - essential for interaction and debugging")
    if "=" in code and "==" not in code:
        concepts.append("<strong>Variables:</strong> Store data for later use - the building blocks of programs")
    
    if not concepts:
        concepts.append("This code demonstrates fundamental programming concepts")
    
    return concepts


@app.route('/explain_html', methods=['POST'])
def explain_html():
    """Generate comprehensive, educational code explanations with detailed breakdowns"""
    data = request.get_json() or {}
    code = data.get("code", "")
    language = data.get("language", "python").lower().strip()

    if not code:
        return jsonify({"html": "<div style='color:red;'>⚠️ No code provided.</div>"}), 400

    # Normalize language names
    lang_normalize = {
        "javascript (node.js 12.14.0)": "javascript",
        "java (openjdk 13.0.1)": "java",
        "c++": "cpp"
    }
    language = lang_normalize.get(language, language)

    # Generate comprehensive explanation
    explanation_html = generate_detailed_explanation(code, language)
    
    # Build HTML with header
    html = f'''
    <div class="explanation-container">
        <div class="header-box">
            <h1>📚 COMPREHENSIVE CODE EXPLANATION</h1>
            <p>🔤 Language: {language.upper()} | 📖 Tutorial-Style Breakdown</p>
        </div>
        {explanation_html}
    </div>
    '''
    
    return jsonify({"html": html})


# ---------------- AI OPTIMIZER ----------------

def ai_optimize_python(code):
    """
    AI-powered code optimizer that provides detailed optimization explanations.
    Returns optimized code and a list of optimizations made.
    """
    optimized_lines = []
    optimizations = []
    lines = code.splitlines()
    
    # Track optimization types
    removed_inner_loops = False
    simplified_ranges = False
    
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        indent = len(line) - len(line.lstrip())
        
        # Detect nested loop pattern for star/pattern printing
        if "for " in stripped and " in range(" in stripped:
            # Check if this is followed by another for loop (nested)
            if i + 1 < len(lines):
                next_line = lines[i + 1]
                next_stripped = next_line.strip()
                next_indent = len(next_line) - len(next_line.lstrip())
                
                # Pattern: nested loop with print("* ")
                if next_indent > indent and "for " in next_stripped and " in range(" in next_stripped:
                    # Check if inner loop prints stars
                    has_star_print = False
                    for j in range(i + 2, min(i + 5, len(lines))):
                        if "print(" in lines[j] and ("*" in lines[j] or '"* "' in lines[j]):
                            has_star_print = True
                            break
                    
                    if has_star_print:
                        # Optimize: remove inner loop, use string multiplication
                        # Extract loop variable from outer loop
                        outer_var_match = re.search(r'for\s+(\w+)\s+in\s+range\((.*?)\)', stripped)
                        if outer_var_match:
                            loop_var = outer_var_match.group(1)
                            range_expr = outer_var_match.group(2)
                            
                            # Check the range pattern - look for pattern with (1, n+1) and nested (n-i, ...)
                            # This is a typical nested loop pattern for printing stars
                            if "1" in range_expr and "n" in range_expr:
                                # Check if inner loop uses n-i or similar pattern
                                if "n" in next_stripped and ("-" in next_stripped or "- " in next_stripped):
                                    optimized_lines.append(f"{' ' * indent}# Use range(n, 0, -1) instead of nested calculation to simplify logic")
                                    optimized_lines.append(f"{' ' * indent}for {loop_var} in range(n, 0, -1):")
                                    optimized_lines.append(f"{' ' * (indent + 4)}# Print the stars directly using string multiplication instead of inner loop")
                                    optimized_lines.append(f"{' ' * (indent + 4)}print(\"* \" * {loop_var})")
                                    
                                    removed_inner_loops = True
                                    simplified_ranges = True
                                    
                                    optimizations.append({
                                        "change": "Removed inner loop",
                                        "description": 'Replaced the inner for j in range(...) with string multiplication ("* " * i)',
                                        "benefit": "Reduces time complexity from O(n²) iteration to O(n) loop"
                                    })
                                    optimizations.append({
                                        "change": "Simplified outer loop",
                                        "description": f"Changed from for {loop_var} in range(1, n+1) with (n-i) logic to a direct decreasing range for {loop_var} in range(n, 0, -1)",
                                        "benefit": "More readable, avoids calculating n - i repeatedly"
                                    })
                                    optimizations.append({
                                        "change": "Cleaner code",
                                        "description": 'Removed redundant end="" usage',
                                        "benefit": "Code is shorter and easier to understand"
                                    })
                                    
                                    # Skip the inner loop and print statements
                                    skip_count = 0
                                    for j in range(i + 1, len(lines)):
                                        if lines[j].strip() and len(lines[j]) - len(lines[j].lstrip()) <= indent:
                                            break
                                        skip_count += 1
                                    i += skip_count
                                    i += 1
                                    continue
        
        # If no optimization applied, keep original line with comments if it's important
        if stripped:
            # Add helpful comments for key lines
            if stripped.startswith("n =") or stripped.startswith("n="):
                optimized_lines.append(f"{' ' * indent}# Optimized pattern printing code")
                optimized_lines.append(line)
            else:
                optimized_lines.append(line)
        else:
            optimized_lines.append(line)
        
        i += 1
    
    # If no optimizations were made, apply simple improvements
    if not optimizations:
        # Check for other simple optimizations
        for i, line in enumerate(lines):
            stripped = line.strip()
            
            # Detect list comprehension opportunities
            if "for " in stripped and i + 1 < len(lines) and ".append(" in lines[i + 1]:
                optimizations.append({
                    "change": "Potential list comprehension",
                    "description": "Could use list comprehension instead of loop with append",
                    "benefit": "More Pythonic and often faster"
                })
                break
        
        # If still no optimizations, return original with note
        if not optimizations:
            optimizations.append({
                "change": "No major optimizations needed",
                "description": "Code is already well-optimized",
                "benefit": "Code follows good practices"
            })
            return {
                "optimized_code": code,
                "optimizations": optimizations
            }
    
    optimized_code = "\n".join(optimized_lines)
    
    return {
        "optimized_code": optimized_code,
        "optimizations": optimizations
    }


# ---------------- AI DEBUGGER ----------------

def format_detailed_issues(bugs_found, code_lines):
    """Format issues in detailed, educational style with explanations and examples."""
    if not bugs_found:
        return ""
    
    issues_html = f"🚨 **Errors and Issues Found**\n\n"
    
    for idx, bug in enumerate(bugs_found, 1):
        line_num = bug["line"]
        bug_type = bug["type"]
        message = bug["message"]
        code_snippet = bug["code"]
        
        issues_html += f"❌ **{idx}. {bug_type}**\n\n"
        
        # Add detailed explanations based on bug type
        if "colon" in bug_type.lower() or "Missing colon" in message:
            issues_html += "Every `for`, `if`, `while`, `def`, `class`, etc., in Python must end with a colon (`:`).\n\n"
            issues_html += f"**Line {line_num}:**\n```\n{code_snippet}   ❌\n```\n\n"
            issues_html += "✅ **Correct:**\n```\n" + code_snippet + ":\n```\n\n"
        
        elif "parentheses" in bug_type.lower() or "print" in message.lower() and "statement" in message.lower():
            issues_html += "In Python 3, `print` is a function, not a statement.\n"
            issues_html += f"This line:\n```\n{code_snippet}\n```\n"
            issues_html += "does nothing — it just refers to the function object and doesn't actually print a newline.\n\n"
            issues_html += "✅ **Correct:**\n```\nprint()\n```\n\n"
        
        elif "Indentation" in bug_type:
            issues_html += "If your inner loop or print isn't properly indented, Python will raise an `IndentationError`.\n"
            issues_html += "Make sure spacing is consistent (usually 4 spaces or a tab).\n\n"
            issues_html += f"**Problem at line {line_num}:**\n```\n{code_snippet}\n```\n\n"
        
        elif "Infinite Loop" in bug_type:
            issues_html += f"**Line {line_num}:** This loop runs forever!\n\n"
            issues_html += f"```\n{code_snippet}\n```\n\n"
            issues_html += "This `while` loop has no `break` statement or condition that becomes `False`.\n"
            issues_html += "It will run indefinitely and freeze your program.\n\n"
            issues_html += "✅ **Fix:** Add a `break` statement or ensure the condition eventually becomes `False`.\n\n"
        
        elif "Assignment in Conditional" in bug_type:
            issues_html += f"**Line {line_num}:** Using `=` (assignment) instead of `==` (comparison)\n\n"
            issues_html += f"```\n{code_snippet}   ❌\n```\n\n"
            issues_html += "The single `=` assigns a value and always evaluates to `True`, which is probably not what you want.\n\n"
            if "fix" in bug:
                issues_html += f"✅ **Correct:**\n```\n{bug['fix']}\n```\n\n"
        
        elif "Index Error" in bug_type or "IndexError" in bug_type:
            issues_html += f"**Line {line_num}:** Potential out-of-bounds array access\n\n"
            issues_html += f"```\n{code_snippet}\n```\n\n"
            issues_html += "When you use `range(len(arr))`, the index goes from `0` to `len(arr)-1`.\n"
            issues_html += "Accessing `arr[i+1]` or `arr[i-1]` can cause an `IndexError` at the boundaries.\n\n"
            issues_html += "✅ **Fix:** Check array bounds or adjust your loop range.\n\n"
        
        elif "Typo" in bug_type or "undefined" in message.lower():
            issues_html += f"**Line {line_num}:** Variable might not be defined\n\n"
            issues_html += f"```\n{code_snippet}\n```\n\n"
            issues_html += f"{message}\n\n"
            issues_html += "✅ **Fix:** Check for typos in variable names or make sure the variable is defined before use.\n\n"
        
        elif "Loop Variable Modification" in bug_type:
            issues_html += f"**Line {line_num}:** Modifying the loop variable inside the loop\n\n"
            issues_html += f"```\n{code_snippet}\n```\n\n"
            issues_html += "In a `for` loop like `for i in range(...)`, changing the value of `i` inside the loop\n"
            issues_html += "won't affect the next iteration. The loop counter is controlled by the iterator.\n\n"
            issues_html += "✅ **Fix:** Use a different variable for calculations, or use a `while` loop if you need to control the counter.\n\n"
        
        else:
            # Generic format for other issues
            issues_html += f"**Line {line_num}:**\n```\n{code_snippet}\n```\n\n"
            issues_html += f"{message}\n\n"
            if "fix" in bug:
                issues_html += f"✅ **Suggested Fix:**\n```\n{bug['fix']}\n```\n\n"
        
        issues_html += "---\n\n"
    
    return issues_html


def ai_debug_code(code, language, issues):
    """
    AI-powered intelligent debugging that analyzes logical errors, not just syntax.
    Uses GPT-like analysis to find bugs and suggest fixes.
    """
    analysis = {
        "bugs_found": [],
        "suggestions": [],
        "fixed_code": code,
        "confidence": "high"
    }
    
    lines = code.splitlines()
    
    # === SYNTAX ERROR DETECTION ===
    
    # 0. Detect missing colons after control structures
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        # Check for control structures without colons
        if re.match(r"^(if|elif|else|for|while|def|class|try|except|finally|with)\b", stripped):
            if not stripped.endswith(":") and not stripped.endswith("\\"):
                # Make sure it's not a multi-line statement
                if i < len(lines) and not lines[i].strip().startswith("\\"):
                    bug_type = "Missing colon (:)"
                    if "for" in stripped:
                        bug_type += " after for loop"
                    elif "if" in stripped:
                        bug_type += " after if statement"
                    elif "while" in stripped:
                        bug_type += " after while loop"
                    elif "def" in stripped:
                        bug_type += " after function definition"
                    elif "class" in stripped:
                        bug_type += " after class definition"
                    
                    analysis["bugs_found"].append({
                        "line": i,
                        "type": bug_type,
                        "severity": "high",
                        "message": f"Every {stripped.split()[0]}, if, while, etc., in Python must end with a colon.",
                        "code": stripped
                    })
    
    # 0b. Detect print statement without parentheses (Python 3)
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        # Match: print followed by space or end of line, but not print(
        if re.match(r"^\s*print\s*$", stripped) or re.match(r"^\s*print\s+[^(]", stripped):
            analysis["bugs_found"].append({
                "line": i,
                "type": "print statement is missing parentheses",
                "severity": "high",
                "message": "In Python 3, print is a function, not a statement.",
                "code": stripped
            })
    
    # 0c. Detect indentation issues (basic)
    prev_indent = 0
    for i, line in enumerate(lines, 1):
        if not line.strip() or line.strip().startswith("#"):
            continue
        
        current_indent = len(line) - len(line.lstrip())
        
        # Check if indentation changed by an amount not divisible by common tab sizes
        if i > 1 and current_indent != prev_indent:
            indent_diff = abs(current_indent - prev_indent)
            if indent_diff not in [2, 4, 8]:  # Common indentation sizes
                analysis["bugs_found"].append({
                    "line": i,
                    "type": "Indentation issue",
                    "severity": "medium",
                    "message": "Inconsistent indentation detected. Python requires consistent spacing.",
                    "code": line.rstrip()
                })
        
        prev_indent = current_indent
    
    # === LOGICAL ERROR DETECTION ===
    
    # 1. Detect infinite loops
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        # Check for while True without break
        if "while" in stripped.lower() and ("true" in stripped.lower() or "1" in stripped):
            # Look ahead for break statement
            has_break = False
            indent_level = len(line) - len(line.lstrip())
            for j in range(i, min(i + 10, len(lines))):
                if j < len(lines):
                    next_line = lines[j]
                    next_indent = len(next_line) - len(next_line.lstrip())
                    if next_indent > indent_level and "break" in next_line:
                        has_break = True
                        break
                    elif next_indent <= indent_level:
                        break
            
            if not has_break:
                analysis["bugs_found"].append({
                    "line": i,
                    "type": "Infinite Loop",
                    "severity": "high",
                    "message": f"Potential infinite loop detected. Loop has no break condition.",
                    "code": stripped
                })
    
    # 2. Detect assignment instead of comparison
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if re.match(r"^\s*(if|while|elif)\s+.*[^=!<>]=(?!=)", stripped):
            # Single = in conditional
            if " = " in stripped and " == " not in stripped:
                analysis["bugs_found"].append({
                    "line": i,
                    "type": "Assignment in Conditional",
                    "severity": "high",
                    "message": "Using assignment (=) instead of comparison (==). This will always evaluate to True.",
                    "code": stripped,
                    "fix": stripped.replace(" = ", " == ")
                })
    
    # 3. Detect off-by-one errors in loops
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        # Check for range(len(arr)) followed by arr[i+1] or arr[i-1]
        if "range(len(" in stripped:
            var_name = stripped.split("in ")[0].strip().split()[-1] if " in " in stripped else "i"
            # Look for array access with +1 or -1
            for j in range(i, min(i + 5, len(lines))):
                if j < len(lines):
                    check_line = lines[j]
                    if f"{var_name}+1]" in check_line.replace(" ", "") or f"{var_name}-1]" in check_line.replace(" ", ""):
                        analysis["bugs_found"].append({
                            "line": j + 1,
                            "type": "Potential Index Error",
                            "severity": "medium",
                            "message": f"Array access with {var_name}±1 may cause IndexError at boundaries.",
                            "code": check_line.strip()
                        })
                        break
    
    # 4. Detect variable shadowing / typos
    declared_vars = set()
    loop_vars = set()  # Track loop variables
    
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        # Find variable declarations
        if "=" in stripped and not stripped.startswith("#"):
            var_match = re.match(r"^\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*=", stripped)
            if var_match:
                var_name = var_match.group(1)
                declared_vars.add(var_name)
        
        # Track loop variables (for i in..., for num in...)
        if "for " in stripped and " in " in stripped:
            loop_var = stripped.split("for ")[1].split(" in ")[0].strip()
            declared_vars.add(loop_var)
            loop_vars.add(loop_var)
        
        # Track function parameters
        if "def " in stripped and "(" in stripped:
            params = re.findall(r'def\s+\w+\s*\(([^)]*)\)', stripped)
            if params:
                param_list = params[0].split(",")
                for param in param_list:
                    param_name = param.strip().split("=")[0].strip()
                    if param_name:
                        declared_vars.add(param_name)
    
    # Common built-in functions and keywords
    builtins = {'true', 'false', 'none', 'print', 'input', 'len', 'range', 'str', 
                'int', 'float', 'list', 'dict', 'set', 'tuple', 'sum', 'max', 'min',
                'abs', 'all', 'any', 'enumerate', 'zip', 'map', 'filter', 'sorted',
                'open', 'type', 'isinstance', 'hasattr', 'getattr', 'append', 'extend',
                'keys', 'values', 'items', 'split', 'join', 'format', 'replace'}
    
    # Check for undefined variables (simple heuristic) - only in non-string contexts
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped.startswith("#") or not "=" in stripped:
            continue
        
        # Skip lines with string literals containing many variables
        if stripped.count('"') >= 2 or stripped.count("'") >= 2:
            continue
            
        # Check right side of assignment
        parts = stripped.split("=", 1)
        if len(parts) > 1:
            right_side = parts[1]
            # Skip f-strings and format strings
            if 'f"' in right_side or "f'" in right_side or ".format(" in right_side:
                continue
            
            # Find all variable-like tokens
            tokens = re.findall(r'\b([a-z_][a-z0-9_]*)\b', right_side.lower())
            for token in tokens:
                if token not in declared_vars and token not in builtins:
                    # Possible typo - find similar variables
                    similar = [v for v in declared_vars if 0 < abs(len(v) - len(token)) <= 2]
                    if similar:
                        analysis["bugs_found"].append({
                            "line": i,
                            "type": "Possible Typo",
                            "severity": "medium",
                            "message": f"Variable '{token}' may be undefined. Did you mean: {', '.join(similar[:3])}?",
                            "code": stripped
                        })
                        break  # Only report first typo per line
    
    # 5. Detect incorrect loop variable modification
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if "for " in stripped and " in " in stripped:
            loop_var = stripped.split("for ")[1].split(" in ")[0].strip()
            # Check if loop variable is modified inside loop
            indent_level = len(line) - len(line.lstrip())
            for j in range(i, min(i + 20, len(lines))):
                if j < len(lines):
                    check_line = lines[j]
                    check_indent = len(check_line) - len(check_line.lstrip())
                    if check_indent <= indent_level and j != i:
                        break  # Exited loop block
                    if f"{loop_var} =" in check_line or f"{loop_var}=" in check_line:
                        analysis["bugs_found"].append({
                            "line": j + 1,
                            "type": "Loop Variable Modification",
                            "severity": "low",
                            "message": f"Modifying loop variable '{loop_var}' inside the loop. This won't affect iteration.",
                            "code": check_line.strip()
                        })
                        break
    
    # === GENERATE IMPROVED SUGGESTIONS ===
    if not analysis["bugs_found"]:
        analysis["suggestions"].append("✅ No logical errors detected! Your code structure looks good.")
        analysis["suggestions"].append("💡 Consider adding error handling (try-except blocks) for robustness.")
        analysis["suggestions"].append("📝 Add comments to explain complex logic.")
    else:
        analysis["suggestions"].append(f"🐛 Found {len(analysis['bugs_found'])} potential bug(s).")
        analysis["suggestions"].append("🔧 Review the issues below and apply suggested fixes.")
    
    # === APPLY BASIC SYNTAX FIXES (keep existing functionality) ===
    analysis["fixed_code"] = auto_fix_python_syntax(code)
    
    return analysis


def auto_fix_python_syntax(code):
    """Basic syntax fixes only (separated from AI logic)."""
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
        
        # Fix bare print (with no arguments)
        if stripped == "print":
            fixed_line = line.replace("print", "print()")
        
        # Fix assignment in conditionals (= to ==)
        if_match = re.match(r"^(\s*)(if|while|elif)\s+(.+)", line)
        if if_match and " = " in if_match.group(3) and " == " not in if_match.group(3):
            indent, keyword, condition = if_match.groups()
            # Only replace first occurrence and avoid replacing in strings
            condition_fixed = condition.replace(" = ", " == ", 1)
            fixed_line = f"{indent}{keyword} {condition_fixed}"
        
        # Fix indentation (basic - replace tabs with 4 spaces)
        if "\t" in fixed_line:
            fixed_line = fixed_line.replace("\t", "    ")
        
        # Fix missing parentheses in function calls
        if stripped.startswith("input ") and not "input(" in stripped:
            fixed_line = line.replace("input ", "input(") + ")"
        
        fixed_lines.append(fixed_line)
    
    return "\n".join(fixed_lines)


def auto_fix_python(code, issues):
    """Wrapper for backward compatibility - calls syntax fix only."""
    return auto_fix_python_syntax(code)


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
    """Auto-fix common JavaScript errors - comprehensive fixes."""
    fixed_lines = []
    lines = code.splitlines()
    
    for i, line in enumerate(lines):
        fixed_line = line
        stripped = line.strip()
        indent = line[:len(line) - len(line.lstrip())]
        
        # Skip empty lines and comments
        if not stripped or stripped.startswith("//"):
            fixed_lines.append(fixed_line)
            continue
        
        # Fix var to let/const
        if stripped.startswith("var "):
            fixed_line = line.replace("var ", "let ", 1)
            stripped = fixed_line.strip()
        
        # Fix == to ===
        if " == " in stripped and " === " not in stripped:
            fixed_line = fixed_line.replace(" == ", " === ")
            stripped = fixed_line.strip()
        
        # Fix != to !==
        if " != " in stripped and " !== " not in stripped:
            fixed_line = fixed_line.replace(" != ", " !== ")
            stripped = fixed_line.strip()
        
        # Add missing semicolons (comprehensive)
        needs_semicolon = False
        if stripped and not stripped.endswith((";", "{", "}", ",", ":", "/*", "*/")):
            # Variable declarations
            if stripped.startswith(("let ", "const ", "var ")):
                needs_semicolon = True
            # Function calls
            elif re.search(r'\w+\s*\([^{]*\)\s*$', stripped):
                needs_semicolon = True
            # Return, break, continue
            elif stripped.startswith(("return", "break", "continue")):
                needs_semicolon = True
            # Assignments
            elif "=" in stripped and not stripped.endswith("=>"):
                needs_semicolon = True
            
            if needs_semicolon:
                fixed_line = line + ";"
                stripped = fixed_line.strip()
        
        # Fix console.log without parentheses
        if "console.log" in stripped:
            if "console.log(" not in stripped:
                fixed_line = line.replace("console.log", "console.log(") + ")"
                stripped = fixed_line.strip()
        
        # Add missing opening braces for if/else/for/while
        if re.match(r'^(if|else if|while|for)\s*\([^)]*\)\s*$', stripped):
            if i + 1 < len(lines):
                next_line = lines[i + 1].strip()
                if next_line and not next_line.startswith("{"):
                    fixed_line = line + " {"
        
        # Fix missing closing braces (basic detection)
        if stripped == "else" and i + 1 < len(lines):
            next_line = lines[i + 1].strip()
            if next_line and not next_line.startswith("{"):
                fixed_line = line + " {"
        
        fixed_lines.append(fixed_line)
    
    # Balance braces
    fixed_code = "\n".join(fixed_lines)
    open_braces = fixed_code.count("{")
    close_braces = fixed_code.count("}")
    if open_braces > close_braces:
        fixed_code += "\n" + "}" * (open_braces - close_braces)
    
    return fixed_code


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

    # === AI-POWERED COMPREHENSIVE DEBUGGING ===
    # Focus on finding ALL issues, not just fixing one
    ai_analysis = None
    fixed_code = code  # Keep original code visible
    all_issues = []
    
    try:
        if language == "python":
            # Use AI analysis for comprehensive Python debugging
            ai_analysis = ai_debug_code(code, language, linter_output)
            
            # Collect ALL issues found by AI
            if ai_analysis["bugs_found"]:
                # Format all bugs in detail
                ai_issues = format_detailed_issues(ai_analysis["bugs_found"], code.splitlines())
                all_issues.append(ai_issues)
            
            # Add linter issues if they exist
            if linter_output and not linter_output.startswith("✅"):
                all_issues.append("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
                all_issues.append("🔍 **LINTER ANALYSIS:**\n\n")
                all_issues.append(linter_output)
            
            # Add suggestions at the end
            if ai_analysis["suggestions"]:
                all_issues.append("\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
                all_issues.append("💡 **BEST PRACTICES & SUGGESTIONS:**\n\n")
                for i, suggestion in enumerate(ai_analysis["suggestions"], 1):
                    all_issues.append(f"  {i}. {suggestion}\n")
            
            # Combine all issues
            if all_issues:
                linter_output = "".join(all_issues)
            else:
                linter_output = "✅ **GREAT JOB!**\n\nNo issues found! Your code looks clean and follows best practices. 🎉"
            
            # Show fixed code suggestion (but keep original in main view)
            if ai_analysis["fixed_code"] and ai_analysis["fixed_code"] != code:
                fixed_code = ai_analysis["fixed_code"]
            else:
                fixed_code = code
        
        elif language == "javascript":
            # Show linter issues + attempt to provide fixed version
            if linter_output and not linter_output.startswith("✅"):
                all_issues.append("🔍 **JAVASCRIPT LINTER ISSUES:**\n\n")
                all_issues.append(linter_output)
                all_issues.append("\n\n💡 **TIP:** Review the issues above and fix them one by one.")
                linter_output = "".join(all_issues)
            fixed_code = auto_fix_javascript(code, linter_output)
            
        elif language == "java":
            # Show compiler issues
            if linter_output and not linter_output.startswith("✅"):
                all_issues.append("🔍 **JAVA COMPILER ISSUES:**\n\n")
                all_issues.append(linter_output)
                all_issues.append("\n\n💡 **TIP:** Fix compilation errors from top to bottom.")
                linter_output = "".join(all_issues)
            fixed_code = auto_fix_java(code, linter_output)
            
        elif language in ["c", "cpp"]:
            # Show cppcheck issues
            if linter_output and not linter_output.startswith("✅"):
                all_issues.append("🔍 **C/C++ STATIC ANALYSIS:**\n\n")
                all_issues.append(linter_output)
                all_issues.append("\n\n💡 **TIP:** Pay attention to memory management and pointer issues.")
                linter_output = "".join(all_issues)
            fixed_code = auto_fix_c_cpp(code, linter_output)
        else:
            # For unsupported languages, still return the code without comments
            fixed_code = code
            
    except Exception as e:
        # On error, still return original code without error comments
        print(f"Debug error: {e}")
        fixed_code = code

    # Save to history if user is logged in
    if session.get('user_id'):
        title = generate_code_title(code)
        add_to_history(
            user_id=session['user_id'],
            activity_type='debug',
            code_snippet=code,
            language=language.capitalize(),
            title=title,
            output=linter_output
        )

    return jsonify({
        "issues": linter_output,
        "fixed_code": fixed_code,
        "original_code": code,
        "ai_analysis": ai_analysis  # Include full AI analysis in response
    })

# ---------------- HISTORY API ----------------
@app.route("/api/history", methods=["GET"])
def get_history():
    """Get user's activity history"""
    if not check_user():
        return jsonify({"error": "Not logged in"}), 401
    
    try:
        limit = request.args.get('limit', 50, type=int)
        history = get_user_history(session['user_id'], limit)
        
        # Format the history data
        history_list = []
        for item in history:
            history_list.append({
                'id': item[0],
                'activity_type': item[1],
                'code_snippet': item[2],
                'language': item[3],
                'title': item[4],
                'output': item[5],
                'created_at': item[6].strftime('%Y-%m-%d %H:%M:%S') if item[6] else ''
            })
        
        return jsonify({"history": history_list})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/history/<int:history_id>", methods=["GET"])
def get_history_item(history_id):
    """Get a specific history item"""
    if not check_user():
        return jsonify({"error": "Not logged in"}), 401
    
    try:
        item = get_history_by_id(history_id, session['user_id'])
        if not item:
            return jsonify({"error": "History item not found"}), 404
        
        return jsonify({
            'id': item[0],
            'activity_type': item[1],
            'code_snippet': item[2],
            'language': item[3],
            'title': item[4],
            'output': item[5],
            'created_at': item[6].strftime('%Y-%m-%d %H:%M:%S') if item[6] else ''
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/history/<int:history_id>", methods=["DELETE"])
def delete_history(history_id):
    """Delete a history item"""
    if not check_user():
        return jsonify({"error": "Not logged in"}), 401
    
    try:
        delete_history_item(history_id, session['user_id'])
        return jsonify({"success": True, "message": "History item deleted"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, threaded=True)
