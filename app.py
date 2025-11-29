# app.py
import os
from flask import Flask, request, jsonify, render_template, redirect, url_for, make_response, Response, session, flash
import sys, ast, traceback, re, requests, subprocess, tempfile
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
from dotenv import load_dotenv
from database import init_db, fetch_one, execute_query, add_to_history, get_user_history, get_history_by_id, delete_history_item, generate_code_title
import google.generativeai as genai
import json
from email_utils import init_mail, generate_verification_token, generate_reset_token, send_verification_email, send_password_reset_email, send_welcome_email
from oauth_config import init_oauth

# Load environment variables from .env file
load_dotenv()

# Configure Google Gemini API
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    # Use gemini-1.5-flash - stable model with better free tier limits
    gemini_model = genai.GenerativeModel('gemini-1.5-flash')
    print("✅ Gemini AI enabled: gemini-1.5-flash")
else:
    gemini_model = None
    print("⚠️ WARNING: GEMINI_API_KEY not found in .env file. AI features will be disabled.")

app = Flask(__name__)
# Use environment variable for secret key, fallback to generated key if not found
app.secret_key = os.getenv('SECRET_KEY', os.urandom(24).hex())

# Session configuration - make sessions permanent (30 days)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=30)
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_HTTPONLY'] = True

# Configuration from environment
app.config['DB_TYPE'] = os.getenv('DB_TYPE', 'mysql')
app.config['FLASK_ENV'] = os.getenv('FLASK_ENV', 'production')
app.config['DEBUG'] = os.getenv('FLASK_DEBUG', 'False') == 'True'

# File upload configuration
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'static', 'uploads', 'profiles')
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB max file size
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize email system
mail = init_mail(app)

# Initialize OAuth
oauth, google_oauth, github_oauth = init_oauth(app)

# Initialize database on startup
init_db()

# ---------------- HELPER FUNCTIONS ----------------
def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def check_user():
    """Check if user is logged in"""
    return 'user_id' in session and 'username' in session

def require_email_verification(user_id):
    """Check if user's email is verified"""
    user = fetch_one('SELECT email_verified FROM users WHERE id = ?', (user_id,))
    return user and user[0]

def is_admin():
    """Check if current user is admin"""
    if not session.get('user_id'):
        return False
    user = fetch_one('SELECT is_admin FROM users WHERE id = ?', (session['user_id'],))
    return user and user[0]

# ---------------- AUTHENTICATION ----------------
@app.route("/")
def index():
    """Landing page - Main page accessible to everyone"""
    return redirect(url_for("main"))

@app.route("/login", methods=["GET", "POST"])
def login():
    # If already logged in, redirect to main
    if check_user():
        return redirect(url_for("main"))
    
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        
        # Check credentials in database
        user = fetch_one('SELECT id, username, password FROM users WHERE username = ?', (username,))
        
        if user and check_password_hash(user[2], password):
            # Login successful
            session.permanent = True
            session['user_id'] = user[0]
            session['username'] = user[1]
            
            # Update last login (optional tracking)
            try:
                execute_query('UPDATE users SET last_login = NOW() WHERE id = ?', (user[0],))
            except:
                pass  # Ignore if column doesn't exist in older databases
            
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
            return render_template("login.html", register_error="All fields are required!")
        
        if password != confirm_password:
            return render_template("login.html", register_error="Passwords do not match!")
        
        if len(password) < 6:
            return render_template("login.html", register_error="Password must be at least 6 characters!")
        
        # Check if user already exists
        existing_user = fetch_one('SELECT id FROM users WHERE username = ? OR email = ?', (username, email))
        
        if existing_user:
            return render_template("login.html", register_error="Username or email already exists!")
        
        # Create new user
        hashed_password = generate_password_hash(password)
        
        try:
            execute_query('''
                INSERT INTO users (username, email, password, email_verified)
                VALUES (?, ?, ?, ?)
            ''', (username, email, hashed_password, True))
            
            return render_template("login.html", success="Registration successful! You can now login.")
        except Exception as e:
            return render_template("login.html", register_error=f"Registration failed: {str(e)}")
    
    return render_template("register.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("main"))

# ---------------- EMAIL VERIFICATION ----------------
@app.route("/verify-email/<token>")
def verify_email(token):
    """Verify user email with token"""
    try:
        # Find user by verification token
        user = fetch_one('SELECT id, username, email FROM users WHERE verification_token = ?', (token,))
        
        if not user:
            return render_template("message.html", 
                                 title="Verification Failed",
                                 message="Invalid or expired verification link.",
                                 type="error")
        
        # Update user as verified
        execute_query('UPDATE users SET email_verified = TRUE, verification_token = NULL WHERE id = ?', (user[0],))
        
        # Send welcome email
        send_welcome_email(mail, user[2], user[1])
        
        return render_template("message.html",
                             title="Email Verified!",
                             message=f"Success! Your email has been verified. You can now <a href='{url_for('login')}'>login</a> to your account.",
                             type="success")
    except Exception as e:
        print(f"Error verifying email: {e}")
        return render_template("message.html",
                             title="Error",
                             message="An error occurred during verification. Please try again.",
                             type="error")

# ---------------- PASSWORD RESET ----------------
@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    """Request password reset"""
    if request.method == "POST":
        email = request.form.get("email")
        
        # Find user by email
        user = fetch_one('SELECT id, username, email FROM users WHERE email = ?', (email,))
        
        if user:
            # Generate reset token
            reset_token = generate_reset_token()
            expiry = datetime.now() + timedelta(hours=1)
            
            # Save token to database
            execute_query('UPDATE users SET reset_token = ?, reset_token_expiry = ? WHERE id = ?',
                        (reset_token, expiry, user[0]))
            
            # Send reset email
            send_password_reset_email(mail, user[2], user[1], reset_token, request.host)
        
        # Always show success message (security: don't reveal if email exists)
        return render_template("forgot_password.html", 
                             success="If that email exists, you'll receive a password reset link shortly.")
    
    return render_template("forgot_password.html")

@app.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    """Reset password with token"""
    # Verify token
    user = fetch_one('SELECT id, username, reset_token_expiry FROM users WHERE reset_token = ?', (token,))
    
    if not user:
        return render_template("message.html",
                             title="Invalid Link",
                             message="This password reset link is invalid.",
                             type="error")
    
    # Check if token expired
    if user[2] and datetime.now() > user[2]:
        return render_template("message.html",
                             title="Link Expired",
                             message="This password reset link has expired. Please request a new one.",
                             type="error")
    
    if request.method == "POST":
        new_password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")
        
        if not new_password or len(new_password) < 6:
            return render_template("reset_password.html", token=token,
                                 error="Password must be at least 6 characters!")
        
        if new_password != confirm_password:
            return render_template("reset_password.html", token=token,
                                 error="Passwords do not match!")
        
        # Update password
        hashed_password = generate_password_hash(new_password)
        execute_query('UPDATE users SET password = ?, reset_token = NULL, reset_token_expiry = NULL WHERE id = ?',
                    (hashed_password, user[0]))
        
        return render_template("message.html",
                             title="Password Reset Successfully",
                             message=f"Your password has been reset! You can now <a href='{url_for('login')}'>login</a> with your new password.",
                             type="success")
    
    return render_template("reset_password.html", token=token)

# ---------------- OAUTH LOGIN ----------------
@app.route("/login/google")
def google_login():
    """Initiate Google OAuth login"""
    if not google_oauth:
        return render_template("message.html",
                             title="OAuth Disabled",
                             message="Google login is not configured.",
                             type="error")
    redirect_uri = url_for('google_callback', _external=True)
    return google_oauth.authorize_redirect(redirect_uri)

@app.route("/login/google/callback")
def google_callback():
    """Handle Google OAuth callback"""
    if not google_oauth:
        return redirect(url_for('login'))
    
    try:
        token = google_oauth.authorize_access_token()
        user_info = token.get('userinfo')
        
        if user_info:
            email = user_info.get('email')
            name = user_info.get('name', email.split('@')[0])
            google_id = user_info.get('sub')
            picture = user_info.get('picture')
            
            # Check if user exists
            user = fetch_one('SELECT id, username FROM users WHERE email = ? OR oauth_id = ?', (email, google_id))
            
            if user:
                # Existing user - login
                session.permanent = True
                session['user_id'] = user[0]
                session['username'] = user[1]
                execute_query('UPDATE users SET last_login = NOW() WHERE id = ?', (user[0],))
            else:
                # New user - create account
                username = name.replace(' ', '_').lower()
                # Ensure unique username
                counter = 1
                original_username = username
                while fetch_one('SELECT id FROM users WHERE username = ?', (username,)):
                    username = f"{original_username}{counter}"
                    counter += 1
                
                user_id = execute_query('''
                    INSERT INTO users (username, email, password, email_verified, oauth_provider, oauth_id, profile_picture)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (username, email, '', True, 'google', google_id, picture))
                
                session.permanent = True
                session['user_id'] = user_id
                session['username'] = username
            
            return redirect(url_for('main'))
    except Exception as e:
        print(f"Google OAuth error: {e}")
        return redirect(url_for('login'))

@app.route("/login/github")
def github_login():
    """Initiate GitHub OAuth login"""
    if not github_oauth:
        return render_template("message.html",
                             title="OAuth Disabled",
                             message="GitHub login is not configured.",
                             type="error")
    redirect_uri = url_for('github_callback', _external=True)
    return github_oauth.authorize_redirect(redirect_uri)

@app.route("/login/github/callback")
def github_callback():
    """Handle GitHub OAuth callback"""
    if not github_oauth:
        return redirect(url_for('login'))
    
    try:
        token = github_oauth.authorize_access_token()
        resp = github_oauth.get('user', token=token)
        user_info = resp.json()
        
        if user_info:
            github_id = str(user_info.get('id'))
            username_github = user_info.get('login')
            name = user_info.get('name', username_github)
            email = user_info.get('email')
            picture = user_info.get('avatar_url')
            
            # Get email if not in profile
            if not email:
                resp = github_oauth.get('user/emails', token=token)
                emails = resp.json()
                for e in emails:
                    if e.get('primary'):
                        email = e.get('email')
                        break
            
            # Check if user exists
            user = fetch_one('SELECT id, username FROM users WHERE oauth_id = ?', (github_id,))
            
            if user:
                # Existing user - login
                session.permanent = True
                session['user_id'] = user[0]
                session['username'] = user[1]
                execute_query('UPDATE users SET last_login = NOW() WHERE id = ?', (user[0],))
            else:
                # New user - create account
                username = username_github.lower()
                counter = 1
                original_username = username
                while fetch_one('SELECT id FROM users WHERE username = ?', (username,)):
                    username = f"{original_username}{counter}"
                    counter += 1
                
                user_id = execute_query('''
                    INSERT INTO users (username, email, password, email_verified, oauth_provider, oauth_id, profile_picture)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (username, email or f"{username}@github.com", '', True, 'github', github_id, picture))
                
                session.permanent = True
                session['user_id'] = user_id
                session['username'] = username
            
            return redirect(url_for('main'))
    except Exception as e:
        print(f"GitHub OAuth error: {e}")
        return redirect(url_for('login'))

# ---------------- PROFILE PAGE ----------------
@app.route("/profile")
def profile():
    """View user profile"""
    if not check_user():
        return redirect(url_for('login'))
    
    user = fetch_one('''
        SELECT id, username, email, email_verified, profile_picture, oauth_provider, created_at, last_login, is_admin
        FROM users WHERE id = ?
    ''', (session['user_id'],))
    
    if not user:
        return redirect(url_for('login'))
    
    # Get user statistics
    from database import get_db_connection
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM code_history WHERE user_id = %s', (session['user_id'],))
    total_activities = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM code_history WHERE user_id = %s AND activity_type = "saved"', (session['user_id'],))
    total_projects = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM code_history WHERE user_id = %s AND activity_type = "shared"', (session['user_id'],))
    total_shared = cursor.fetchone()[0]
    
    cursor.close()
    conn.close()
    
    user_data = {
        'id': user[0],
        'username': user[1],
        'email': user[2],
        'email_verified': user[3],
        'profile_picture': user[4],
        'oauth_provider': user[5],
        'created_at': user[6],
        'last_login': user[7],
        'is_admin': user[8],
        'total_activities': total_activities,
        'total_projects': total_projects,
        'total_shared': total_shared
    }
    
    return render_template("profile.html", user=user_data)

@app.route("/profile/change-password", methods=["GET", "POST"])
def change_password():
    """Change user password"""
    if not check_user():
        return redirect(url_for('login'))
    
    # Check if user uses OAuth (no password change needed)
    user = fetch_one('SELECT oauth_provider FROM users WHERE id = ?', (session['user_id'],))
    if user and user[0]:
        flash("You're using OAuth login. Password change is not available.", "info")
        return redirect(url_for('profile'))
    
    if request.method == "POST":
        current_password = request.form.get("current_password")
        new_password = request.form.get("new_password")
        confirm_password = request.form.get("confirm_password")
        
        # Verify current password
        user = fetch_one('SELECT password FROM users WHERE id = ?', (session['user_id'],))
        if not check_password_hash(user[0], current_password):
            flash("Current password is incorrect!", "error")
            return redirect(url_for('change_password'))
        
        if len(new_password) < 6:
            flash("New password must be at least 6 characters!", "error")
            return redirect(url_for('change_password'))
        
        if new_password != confirm_password:
            flash("Passwords do not match!", "error")
            return redirect(url_for('change_password'))
        
        # Update password
        hashed_password = generate_password_hash(new_password)
        execute_query('UPDATE users SET password = ? WHERE id = ?', (hashed_password, session['user_id']))
        
        flash("Password changed successfully!", "success")
        return redirect(url_for('profile'))
    
    return render_template("change_password.html")

@app.route("/profile/upload-picture", methods=["POST"])
def upload_profile_picture():
    """Upload profile picture"""
    if not check_user():
        return jsonify({"success": False, "error": "Not logged in"}), 401
    
    if 'profile_picture' not in request.files:
        return jsonify({"success": False, "error": "No file uploaded"}), 400
    
    file = request.files['profile_picture']
    
    if file.filename == '':
        return jsonify({"success": False, "error": "No file selected"}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(f"user_{session['user_id']}_{datetime.now().strftime('%Y%m%d%H%M%S')}.{file.filename.rsplit('.', 1)[1].lower()}")
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Update database
        picture_url = f"/static/uploads/profiles/{filename}"
        execute_query('UPDATE users SET profile_picture = ? WHERE id = ?', (picture_url, session['user_id']))
        
        return jsonify({"success": True, "picture_url": picture_url})
    
    return jsonify({"success": False, "error": "Invalid file type"}), 400

# ---------------- ADMIN DASHBOARD ----------------
@app.route("/admin")
def admin_dashboard():
    """Admin dashboard"""
    if not check_user() or not is_admin():
        return render_template("message.html",
                             title="Access Denied",
                             message="You don't have permission to access this page.",
                             type="error")
    
    from database import get_db_connection
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Get statistics
    cursor.execute('SELECT COUNT(*) as total FROM users')
    total_users = cursor.fetchone()['total']
    
    cursor.execute('SELECT COUNT(*) as total FROM code_history')
    total_activities = cursor.fetchone()['total']
    
    cursor.execute('SELECT COUNT(*) as total FROM code_history WHERE activity_type = "saved"')
    total_projects = cursor.fetchone()['total']
    
    cursor.execute('SELECT COUNT(*) as total FROM code_history WHERE activity_type = "shared"')
    total_shared = cursor.fetchone()['total']
    
    # Get recent users
    cursor.execute('''
        SELECT id, username, email, email_verified, oauth_provider, created_at, last_login
        FROM users ORDER BY created_at DESC LIMIT 10
    ''')
    recent_users = cursor.fetchall()
    
    # Get activity breakdown
    cursor.execute('''
        SELECT activity_type, COUNT(*) as count
        FROM code_history
        GROUP BY activity_type
    ''')
    activity_breakdown = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    stats = {
        'total_users': total_users,
        'total_activities': total_activities,
        'total_projects': total_projects,
        'total_shared': total_shared,
        'recent_users': recent_users,
        'activity_breakdown': activity_breakdown
    }
    
    return render_template("admin_dashboard.html", stats=stats)

@app.route("/admin/users")
def admin_users():
    """View all users"""
    if not check_user() or not is_admin():
        return redirect(url_for('login'))
    
    from database import get_db_connection
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute('''
        SELECT id, username, email, email_verified, oauth_provider, is_admin, created_at, last_login
        FROM users ORDER BY created_at DESC
    ''')
    users = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template("admin_users.html", users=users)

@app.route("/admin/toggle-admin/<int:user_id>", methods=["POST"])
def toggle_admin(user_id):
    """Toggle admin status for user"""
    if not check_user() or not is_admin():
        return jsonify({"success": False, "error": "Unauthorized"}), 403
    
    # Don't allow toggling own admin status
    if user_id == session['user_id']:
        return jsonify({"success": False, "error": "Cannot modify your own admin status"}), 400
    
    # Toggle admin status
    user = fetch_one('SELECT is_admin FROM users WHERE id = ?', (user_id,))
    new_status = not user[0]
    execute_query('UPDATE users SET is_admin = ? WHERE id = ?', (new_status, user_id))
    
    return jsonify({"success": True, "is_admin": new_status})

@app.route("/main")
def main():
    """Main landing page - accessible without login"""
    user_logged_in = check_user()
    username = session.get('username', None) if user_logged_in else None
    return render_template("main.html", user_logged_in=user_logged_in, username=username)

@app.route("/compiler")
def compiler():
    """Compiler page - accessible without login"""
    user_logged_in = check_user()
    username = session.get('username', None) if user_logged_in else None
    print(f"DEBUG /compiler - user_logged_in: {user_logged_in}, username: {username}, session: {dict(session)}")
    return render_template("compiler.html", user_logged_in=user_logged_in, username=username)

@app.route("/api/check-session")
def check_session():
    """Debug endpoint to check session status"""
    return jsonify({
        "logged_in": check_user(),
        "username": session.get('username'),
        "user_id": session.get('user_id'),
        "session_keys": list(session.keys())
    })

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

def is_valid_code(code):
    """
    Check if the input is actual code, not just plain text.
    Returns True if it looks like code, False if it's just text.
    """
    if not code or not code.strip():
        return False
    
    # Programming keywords that indicate actual code
    code_indicators = [
        # Python
        'def ', 'class ', 'import ', 'from ', 'if ', 'elif ', 'else:', 'for ', 'while ', 
        'return ', 'try:', 'except:', 'with ', 'lambda ', 'yield ', 'async ', 'await ', 'print(',
        # JavaScript/Java/C++
        'function ', 'var ', 'let ', 'const ', 'public ', 'private ', 'static ',
        'void ', 'int ', 'String ', 'class ', 'interface ', 'extends ', 'implements ',
        # Common patterns
        '()', '[]', '{}', '==', '!=', '<=', '>=', '&&', '||', '=>',
        'console.log', 'System.out', 'printf', 'scanf', 'cout', 'cin'
    ]
    
    code_lower = code.lower()
    
    # Check if at least one code indicator is present
    has_code_indicator = any(indicator.lower() in code_lower for indicator in code_indicators)
    
    # Check for assignment or function call patterns
    has_assignment = '=' in code and '==' not in code  # Variable assignment
    has_function_call = '(' in code and ')' in code  # Function calls
    has_brackets = '{' in code or '[' in code  # Data structures or blocks
    
    # Must have at least one strong code indicator
    return has_code_indicator or (has_assignment and has_function_call) or has_brackets


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


# ---------------- JUDGE0 API with multiple reliable fallback options ----------------
# NOTE: Multiple endpoints ensure execution always works - never shows "Cannot connect" error!
JUDGE0_URLS = [
    # "http://localhost:2358",  # ❌ DISABLED: cgroup v2 incompatibility on Windows
    "https://ce.judge0.com",  # Primary: Free Public API
    "https://judge0.p.rapidapi.com",  # Fallback 1: RapidAPI (auto-handled)
    "https://judge0-ce.p.rapidapi.com"  # Fallback 2: RapidAPI CE
]

# RapidAPI key from environment or hardcoded
RAPIDAPI_KEY = os.getenv('JUDGE0_API_KEY', None)  # Set in .env file or here


def run_judge0(code, language_id=71, stdin=""):
    """
    Try to run code on Judge0 with multiple fallback options.
    GUARANTEED: Always returns result - never shows "Cannot connect" error!
    
    Attempts:
    1. Free public API (ce.judge0.com)
    2. RapidAPI endpoints (if key configured)
    3. Graceful fallback with syntax check
    """
    payload = {
        "source_code": code,
        "language_id": language_id,
        "stdin": stdin
    }
    
    last_error = None
    attempted_urls = []
    
    # Try each Judge0 endpoint
    for base_url in JUDGE0_URLS:
        # Skip RapidAPI if no key configured
        if "rapidapi.com" in base_url and not RAPIDAPI_KEY:
            continue
        
        attempted_urls.append(base_url)
            
        try:
            headers = {"Content-Type": "application/json"}
            
            # Add RapidAPI headers if needed
            if "rapidapi.com" in base_url and RAPIDAPI_KEY:
                headers.update({
                    "X-RapidAPI-Key": RAPIDAPI_KEY,
                    "X-RapidAPI-Host": "judge0-ce.p.rapidapi.com"
                })
            
            # Submit code with LONG timeout for compilation (Java/C++ take time)
            timeout_seconds = 120  # 2 minutes for slow free API + compilation
            
            # Try with wait=true first (blocking call, returns result immediately)
            submit = requests.post(
                f"{base_url}/submissions/?base64_encoded=false&wait=true",
                json=payload,
                headers=headers,
                timeout=timeout_seconds
            )
            
            if submit.status_code not in [200, 201]:
                last_error = f"Server returned status {submit.status_code}"
                continue
            
            result = submit.json()
            
            # Check if we got the result directly (wait=true worked)
            if result.get("status"):
                status = result.get("status", {}).get("description")
                if status == "Accepted" or result.get("stdout") or result.get("stderr"):
                    output = ""
                    if result.get("stdout"):
                        output += result.get("stdout")
                    if result.get("stderr"):
                        output += "\n[stderr]:\n" + result.get("stderr")
                    if result.get("compile_output"):
                        output += "\n[compile_output]:\n" + result.get("compile_output")
                    return output or "⚠️ No output"
                elif status not in ["In Queue", "Processing"]:
                    last_error = f"Execution failed with status: {status}"
                    continue
            
            # If wait=true didn't return result, fall back to polling
            token = result.get("token")
            if not token:
                last_error = "No token received from server"
                continue

            # Poll for result with LONGER timing (max 60 attempts = 2 minutes)
            import time
            for attempt in range(60):  # More attempts for Java/C++ compilation
                time.sleep(2)  # 2 second delays
                res = requests.get(
                    f"{base_url}/submissions/{token}?base64_encoded=false",
                    headers=headers,
                    timeout=60  # Longer timeout for compilation
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
            last_error = f"Connection error"
            continue
        except requests.exceptions.Timeout:
            last_error = f"Request timeout"
            continue
        except requests.exceptions.RequestException as e:
            last_error = f"Request error: {str(e)}"
            continue
        except Exception as e:
            last_error = f"Unexpected error: {str(e)}"
            continue
    
    # If all endpoints failed, provide helpful output instead of error
    # GRACEFUL FALLBACK: Never show "Cannot connect" error!
    
    # Simple syntax check as fallback
    syntax_ok = True
    syntax_msg = ""
    
    # Basic Python syntax validation for common errors
    if language_id in [71, 92, 93, 94]:  # Python
        try:
            import ast
            ast.parse(code)
            syntax_msg = "✅ Python syntax is valid!"
        except SyntaxError as e:
            syntax_ok = False
            syntax_msg = f"❌ Syntax Error at line {e.lineno}:\n{str(e)}"
    
    output = "⚠️ Code Execution Service Temporarily Unavailable\n\n"
    output += f"🔍 Syntax Check: {syntax_msg}\n\n"
    output += "📝 Your code:\n"
    output += "=" * 50 + "\n"
    output += code[:500]  # Show first 500 chars
    if len(code) > 500:
        output += f"\n... ({len(code) - 500} more characters)"
    output += "\n" + "=" * 50 + "\n\n"
    
    if syntax_ok:
        output += "✨ Good news: Your code looks syntactically correct!\n\n"
        output += "💡 The execution service will retry automatically.\n"
        output += "   Please try running your code again in a moment.\n\n"
    else:
        output += "💡 Fix the syntax error above and try again.\n\n"
    
    output += f"🔧 Technical info: Attempted {len(attempted_urls)} endpoint(s)\n"
    output += f"   Last issue: {last_error}\n"
    
    return output


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
    """Optimize code - requires login"""
    if not check_user():
        return jsonify({"error": "Please login to use the optimizer feature"}), 401
    
    data = request.get_json() or {}
    code = data.get("code", "")
    language = data.get("language", "python").lower()

    if not code:
        return jsonify({"error": "No code provided"}), 400

    try:
        # Use AI optimizer for all languages
        result = ai_optimize_code(code, language)
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


# ---------------- AI CODE QUALITY SCORE ----------------

@app.route("/api/code-quality", methods=["POST"])
def analyze_code_quality():
    """Analyze code quality and provide comprehensive scoring - requires login"""
    if not check_user():
        return jsonify({"error": "Please login to use the code quality analyzer"}), 401
    
    data = request.get_json() or {}
    code = data.get("code", "")
    language = data.get("language", "python").lower()

    if not code:
        return jsonify({"error": "No code provided"}), 400

    if not gemini_model:
        return jsonify({"error": "AI service unavailable"}), 503

    try:
        # Create comprehensive prompt for Gemini
        prompt = f"""You are an expert code reviewer and senior software engineer. Analyze this {language.upper()} code and provide a comprehensive quality assessment.

CODE TO ANALYZE:
```{language}
{code}
```

Provide a detailed analysis in the following JSON format (respond ONLY with valid JSON, no markdown):

{{
    "overall_score": <0-100 integer>,
    "grade": "<A+, A, B+, B, C+, C, D, F>",
    "scores": {{
        "code_quality": <0-100>,
        "readability": <0-100>,
        "maintainability": <0-100>,
        "performance": <0-100>,
        "security": <0-100>,
        "best_practices": <0-100>
    }},
    "strengths": [
        "Specific strength 1",
        "Specific strength 2",
        "Specific strength 3"
    ],
    "issues": [
        {{
            "severity": "critical|high|medium|low",
            "category": "bug|security|performance|style|best-practice",
            "title": "Issue title",
            "description": "Detailed description",
            "line": <line number or null>,
            "suggestion": "How to fix it"
        }}
    ],
    "complexity": {{
        "cyclomatic": <integer>,
        "cognitive": "low|medium|high",
        "description": "Brief explanation"
    }},
    "recommendations": [
        "Specific actionable recommendation 1",
        "Specific actionable recommendation 2",
        "Specific actionable recommendation 3"
    ],
    "summary": "One paragraph summary of the code quality"
}}

Be thorough, specific, and constructive. Focus on actionable feedback."""

        response = gemini_model.generate_content(prompt)
        response_text = response.text.strip()
        
        # Remove markdown code blocks if present
        if response_text.startswith("```"):
            response_text = re.sub(r'^```(?:json)?\s*\n', '', response_text)
            response_text = re.sub(r'\n```\s*$', '', response_text)
        
        # Parse JSON response
        quality_data = json.loads(response_text)
        
        # Save to history
        if session.get('user_id'):
            title = generate_code_title(code)
            add_to_history(
                user_id=session['user_id'],
                activity_type='quality_check',
                code_snippet=code,
                language=language.capitalize(),
                title=title,
                output=f"Quality Score: {quality_data.get('overall_score', 0)}/100 (Grade: {quality_data.get('grade', 'N/A')})"
            )
        
        return jsonify(quality_data)
        
    except json.JSONDecodeError as e:
        print(f"JSON Parse Error: {e}")
        print(f"Response: {response_text[:500]}")
        return jsonify({
            "error": "Failed to parse AI response",
            "detail": "The AI returned an invalid format"
        }), 500
    except Exception as e:
        print(f"Quality Analysis Error: {e}")
        error_msg = str(e)
        
        # Check for quota/rate limit errors
        if "429" in error_msg or "quota" in error_msg.lower() or "rate" in error_msg.lower():
            return jsonify({
                "error": "API Rate Limit Exceeded",
                "detail": "You've reached the Gemini API free tier limit. Please wait 15-30 seconds and try again, or upgrade your API plan."
            }), 429
        
        return jsonify({
            "error": "Quality analysis failed",
            "detail": str(e)
        }), 500


# ---------------- CODE EXECUTION VISUALIZATION ----------------

def create_simple_visualization(code, language):
    """Fallback: Create a simple line-by-line visualization without AI"""
    lines = [line for line in code.split('\n') if line.strip()]
    steps = []
    
    for i, line in enumerate(lines, 1):
        step = {
            "step": i,
            "line": i,
            "code": line.strip(),
            "action": f"Execute line {i}",
            "variables": {},
            "call_stack": [],
            "output": None
        }
        steps.append(step)
    
    return {
        "steps": steps,
        "summary": {
            "total_steps": len(steps),
            "variables_created": [],
            "functions_called": [],
            "complexity": "Simple line-by-line trace (AI analysis unavailable)",
            "final_output": "See code execution above"
        }
    }

@app.route("/api/visualize", methods=["POST"])
def visualize_execution():
    """Generate step-by-step execution visualization - requires login"""
    if not check_user():
        return jsonify({"error": "Please login to use the code visualizer"}), 401
    
    data = request.get_json() or {}
    code = data.get("code", "")
    language = data.get("language", "python").lower()

    if not code:
        return jsonify({"error": "No code provided"}), 400

    if not gemini_model:
        return jsonify({"error": "AI service unavailable"}), 503

    try:
        prompt = f"""You are a code execution trace generator. Analyze this {language.upper()} code and create a step-by-step execution visualization.

CODE:
{code}

CRITICAL INSTRUCTIONS:
1. Respond with ONLY valid JSON (no explanations, no markdown, no code blocks)
2. Start your response with {{ and end with }}
3. Follow this exact structure:

{{
    "steps": [
        {{
            "step": 1,
            "line": 1,
            "code": "x = 5",
            "action": "Assign value 5 to variable x",
            "variables": {{
                "x": {{"value": "5", "type": "int", "changed": true}}
            }},
            "call_stack": [],
            "output": null
        }}
    ],
    "summary": {{
        "total_steps": 4,
        "variables_created": ["x", "y"],
        "functions_called": [],
        "complexity": "O(1) - simple sequential execution",
        "final_output": "Program completed successfully"
    }}
}}

Rules:
- Keep code simple (max 10 steps for complex programs)
- Show variables as strings for consistency
- Set "changed" to true only when variable value changes
- Use empty array [] for call_stack if no functions
- Use null for output unless there's a print statement
- Keep action descriptions brief (under 50 characters)

Now generate the trace for the code above. Remember: ONLY JSON, no other text."""

        response = gemini_model.generate_content(prompt)
        response_text = response.text.strip()
        
        print(f"[VISUALIZE] Raw response length: {len(response_text)}")
        print(f"[VISUALIZE] First 200 chars: {response_text[:200]}")
        
        # Clean up the response - remove any markdown or extra text
        # Try to find JSON object
        json_start = response_text.find('{')
        json_end = response_text.rfind('}') + 1
        
        if json_start != -1 and json_end > json_start:
            response_text = response_text[json_start:json_end]
            print(f"[VISUALIZE] Extracted JSON from position {json_start} to {json_end}")
        
        # Remove markdown code blocks if present
        response_text = re.sub(r'^```(?:json)?\s*', '', response_text)
        response_text = re.sub(r'\s*```$', '', response_text)
        
        # Parse JSON response
        viz_data = json.loads(response_text)
        
        # Validate structure
        if not isinstance(viz_data.get('steps'), list) or len(viz_data['steps']) == 0:
            raise ValueError("Invalid visualization data: missing or empty steps")
        
        # Save to history
        if session.get('user_id'):
            title = generate_code_title(code)
            add_to_history(
                user_id=session['user_id'],
                activity_type='visualize',
                code_snippet=code,
                language=language.capitalize(),
                title=title,
                output=f"Visualized {viz_data.get('summary', {}).get('total_steps', 0)} execution steps"
            )
        
        return jsonify(viz_data)
        
    except json.JSONDecodeError as e:
        print(f"[VISUALIZE] JSON Parse Error: {e}")
        print(f"[VISUALIZE] Failed response (first 500 chars): {response_text[:500] if 'response_text' in locals() else 'No response'}")
        
        # Return a helpful error with the actual response snippet
        return jsonify({
            "error": "AI returned invalid JSON format",
            "detail": f"Parse error: {str(e)}. The AI response couldn't be converted to visualization data. Try simplifying your code or try again.",
            "debug_info": response_text[:200] if 'response_text' in locals() else "No response received"
        }), 500
        
    except ValueError as e:
        print(f"[VISUALIZE] Validation Error: {e}")
        return jsonify({
            "error": "Invalid visualization data",
            "detail": str(e)
        }), 500
        
    except Exception as e:
        print(f"[VISUALIZE] Unexpected Error: {e}")
        print(f"[VISUALIZE] Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        
        error_msg = str(e)
        
        # Check for quota/rate limit errors
        if "429" in error_msg or "quota" in error_msg.lower() or "rate" in error_msg.lower():
            return jsonify({
                "error": "API Rate Limit Exceeded",
                "detail": "You've reached the Gemini API free tier limit. Please wait 15-30 seconds and try again, or upgrade your API plan."
            }), 429
        
        return jsonify({
            "error": "Visualization failed",
            "detail": f"{type(e).__name__}: {str(e)}. Please try again or use simpler code."
        }), 500


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


def ai_explain_code(code, language):
    """
    AI-powered code explanation using Google Gemini API.
    Provides intelligent, context-aware explanations for any language.
    """
    if not gemini_model:
        print("⚠️ Gemini model not available - API key may be missing")
        return None  # Fall back to rule-based explanation
    
    try:
        prompt = f"""You are an expert programming tutor. Explain this {language} code in a clear, educational way.

**Code:**
```{language}
{code}
```

**Return ONLY valid JSON with this structure:**
{{
  "summary": "One sentence describing what this code does",
  "algorithm": "Explain the algorithm/approach used",
  "time_complexity": "O(n) or O(n²) etc.",
  "time_explanation": "Brief explanation of time complexity",
  "space_complexity": "O(1) or O(n) etc.",
  "space_explanation": "Brief explanation of space complexity",
  "steps": [
    {{
      "title": "Step name (3-5 words)",
      "explanation": "What this step does",
      "code_snippet": "key line(s) of code for this step",
      "why": "Why this step is important"
    }}
  ],
  "key_insights": [
    "Important insight about the code",
    "Another key learning point"
  ]
}}

Focus on:
- Clear, beginner-friendly language
- Actual code logic and flow
- Important concepts demonstrated
- Common pitfalls or edge cases

Return ONLY the JSON, no markdown formatting."""

        print(f"🤖 Calling Gemini AI for {language} explanation...")
        
        # Set timeout using signal (Unix) or threading (Windows)
        import time
        from threading import Thread
        
        result_container = {'response': None, 'error': None}
        
        def call_gemini():
            try:
                result_container['response'] = gemini_model.generate_content(prompt)
            except Exception as e:
                result_container['error'] = str(e)
        
        start_time = time.time()
        thread = Thread(target=call_gemini)
        thread.daemon = True
        thread.start()
        thread.join(timeout=30)  # 30 second timeout
        
        if thread.is_alive():
            print(f"❌ Gemini API timeout after 30s - using fallback")
            return None
        
        if result_container['error']:
            print(f"❌ Gemini API error: {result_container['error']}")
            return None
        
        if not result_container['response']:
            print(f"❌ No response from Gemini API")
            return None
        
        response_text = result_container['response'].text.strip()
        elapsed = time.time() - start_time
        print(f"✅ AI response received ({len(response_text)} chars) in {elapsed:.1f}s")
        
        # Clean up markdown code blocks (Gemini often wraps JSON in ```json ... ```)
        if response_text.startswith('```'):
            # Remove all lines that are just markdown delimiters
            lines = response_text.split('\n')
            clean_lines = [line for line in lines if not line.strip().startswith('```')]
            response_text = '\n'.join(clean_lines).strip()
            print("🧹 Removed markdown wrapper")
        
        # Parse JSON
        result = json.loads(response_text)
        print(f"✅ JSON parsed successfully - {len(result.get('steps', []))} steps found")
        return result
        
    except json.JSONDecodeError as e:
        print(f"❌ AI explanation JSON parse error: {e}")
        print(f"Response preview: {response_text[:200]}...")
        return None
    except Exception as e:
        print(f"❌ AI explanation error: {e}")
        return None  # Fall back to rule-based


def generate_comprehensive_explanation(code, language):
    """
    Generate clean, colorful code explanation like ChatGPT/Claude style.
    Simple sections with beautiful gradients and icons.
    """
    print("\n🔍 generate_comprehensive_explanation() called")
    print(f"   Language: {language}, Code length: {len(code)}")
    
    # Try AI explanation first, fall back to rule-based if unavailable
    ai_result = ai_explain_code(code, language)
    
    print(f"   AI Result: {'✅ SUCCESS' if ai_result else '❌ NONE (falling back)'}")
    
    if ai_result:
        # Use AI-generated analysis
        code_analysis = {
            'summary': ai_result.get('summary', ''),
            'steps': [
                {
                    'title': step.get('title', ''),
                    'explanation': step.get('explanation', ''),
                    'code_block': step.get('code_snippet', ''),
                    'why': step.get('why', '')
                }
                for step in ai_result.get('steps', [])
            ],
            'time_complexity': ai_result.get('time_complexity', ''),
            'time_explanation': ai_result.get('time_explanation', ''),
            'space_complexity': ai_result.get('space_complexity', ''),
            'space_explanation': ai_result.get('space_explanation', ''),
            'insights': ai_result.get('key_insights', [])
        }
    else:
        # Fall back to rule-based analysis
        code_analysis = deep_analyze_code(code, language)
    
    # Build beautiful, clean HTML sections with colorful theme
    html_parts = []
    
    # Header with code preview
    safe_code = code.replace('<', '&lt;').replace('>', '&gt;').replace('\n', '<br>')
    html_parts.append(f'''
    <div style="background: linear-gradient(135deg, #1e293b 0%, #334155 100%); border-radius: 8px; padding: 0.8rem 1rem; margin-bottom: 1rem; border: 1px solid rgba(59, 130, 246, 0.3);">
        <div style="color: #94a3b8; font-size: 0.75rem; font-weight: 600; margin-bottom: 0.4rem; text-transform: uppercase; letter-spacing: 0.5px;">
            📄 Your Code
        </div>
        <pre style="margin: 0; font-family: 'Consolas', 'Monaco', monospace; font-size: 0.9rem; color: #e2e8f0; line-height: 1.5; overflow-x: auto;"><code>{safe_code}</code></pre>
    </div>
    ''')
    
    # High-Level Overview
    html_parts.append(f'''
    <div style="margin-bottom: 1.2rem;">
        <h2 style="color: #3b82f6; font-size: 1.3rem; font-weight: 700; margin: 0 0 0.6rem 0; display: flex; align-items: center; gap: 0.5rem;">
            <span style="background: linear-gradient(135deg, #3b82f6, #2563eb); padding: 0.3rem 0.6rem; border-radius: 8px; color: white;">🎯</span>
            High-Level Overview
        </h2>
        <p style="color: var(--color-text); font-size: 0.95rem; line-height: 1.6; margin: 0; background: linear-gradient(135deg, rgba(59, 130, 246, 0.1), rgba(59, 130, 246, 0.05)); padding: 0.9rem; border-radius: 8px; border-left: 3px solid #3b82f6;">
            {code_analysis.get('summary', 'This code implements a specific functionality.')}
        </p>
    </div>
    ''')
    
    # Detailed Explanation
    html_parts.append('''
    <div style="margin-bottom: 1.2rem;">
        <h2 style="color: #10b981; font-size: 1.3rem; font-weight: 700; margin: 0 0 0.6rem 0; display: flex; align-items: center; gap: 0.5rem;">
            <span style="background: linear-gradient(135deg, #10b981, #059669); padding: 0.3rem 0.6rem; border-radius: 8px; color: white;">📖</span>
            Detailed Explanation
        </h2>
    ''')
    
    # Step-by-step breakdown
    for i, step in enumerate(code_analysis.get('steps', []), 1):
        step_title = step.get('title', f'Step {i}')
        step_explanation = step.get('explanation', '')
        step_code = step.get('code_block', '')
        step_why = step.get('why', '')
        
        html_parts.append(f'''
        <div style="margin-bottom: 1rem;">
            <h3 style="color: var(--color-text); font-size: 1rem; font-weight: 700; margin: 0 0 0.5rem 0;">
                <span style="background: #10b981; color: white; padding: 0.25rem 0.6rem; border-radius: 6px; font-size: 0.85rem; margin-right: 0.5rem; display: inline-block; min-width: 26px; text-align: center;">{i}</span>
                {step_title}
            </h3>
            <p style="color: var(--color-text-secondary); font-size: 0.9rem; line-height: 1.6; margin: 0 0 0.6rem 0; padding-left: 2.5rem;">
                {step_explanation}
            </p>
        ''')
        
        if step_code:
            safe_step_code = step_code.replace('<', '&lt;').replace('>', '&gt;')
            html_parts.append(f'''
            <div style="background: #1e293b; border-radius: 6px; padding: 0.7rem; margin: 0.5rem 0 0.5rem 2.5rem; border-left: 3px solid #10b981;">
                <pre style="margin: 0; font-family: 'Consolas', 'Monaco', monospace; font-size: 0.85rem; color: #e2e8f0; line-height: 1.5; overflow-x: auto;"><code>{safe_step_code}</code></pre>
            </div>
            ''')
        
        if step_why:
            html_parts.append(f'''
            <div style="background: linear-gradient(135deg, rgba(245, 158, 11, 0.15), rgba(245, 158, 11, 0.05)); padding: 0.7rem; border-radius: 6px; margin: 0.5rem 0 0 2.5rem; border-left: 3px solid #f59e0b;">
                <p style="margin: 0; color: var(--color-text); font-size: 0.85rem; line-height: 1.6;">
                    <strong style="color: #f59e0b; font-weight: 700;">💡 Why:</strong> {step_why}
                </p>
            </div>
            ''')
        
        html_parts.append('</div>')
    
    html_parts.append('</div>')
    
    # Performance Analysis
    if code_analysis.get('time_complexity') or code_analysis.get('space_complexity'):
        html_parts.append('''
        <div style="margin-bottom: 1.2rem;">
            <h2 style="color: #f59e0b; font-size: 1.3rem; font-weight: 700; margin: 0 0 0.6rem 0; display: flex; align-items: center; gap: 0.5rem;">
                <span style="background: linear-gradient(135deg, #f59e0b, #d97706); padding: 0.3rem 0.6rem; border-radius: 8px; color: white;">⚡</span>
                Performance Analysis
            </h2>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.8rem;">
        ''')
        
        if code_analysis.get('time_complexity'):
            html_parts.append(f'''
                <div style="background: linear-gradient(135deg, rgba(245, 158, 11, 0.1), rgba(245, 158, 11, 0.05)); padding: 0.9rem; border-radius: 8px; border-left: 3px solid #f59e0b;">
                    <div style="color: #f59e0b; font-weight: 700; font-size: 0.8rem; margin-bottom: 0.4rem; text-transform: uppercase; letter-spacing: 0.5px;">
                        ⏱️ Time Complexity
                    </div>
                    <div style="color: var(--color-text); font-family: 'Consolas', monospace; font-size: 1.2rem; font-weight: 700; margin-bottom: 0.5rem;">
                        {code_analysis['time_complexity']}
                    </div>
                    <p style="margin: 0; color: var(--color-text-secondary); font-size: 0.85rem; line-height: 1.5;">
                        {code_analysis.get('time_explanation', '')}
                    </p>
                </div>
            ''')
        
        if code_analysis.get('space_complexity'):
            html_parts.append(f'''
                <div style="background: linear-gradient(135deg, rgba(139, 92, 246, 0.1), rgba(139, 92, 246, 0.05)); padding: 0.9rem; border-radius: 8px; border-left: 3px solid #8b5cf6;">
                    <div style="color: #8b5cf6; font-weight: 700; font-size: 0.8rem; margin-bottom: 0.4rem; text-transform: uppercase; letter-spacing: 0.5px;">
                        💾 Space Complexity
                    </div>
                    <div style="color: var(--color-text); font-family: 'Consolas', monospace; font-size: 1.2rem; font-weight: 700; margin-bottom: 0.5rem;">
                        {code_analysis['space_complexity']}
                    </div>
                    <p style="margin: 0; color: var(--color-text-secondary); font-size: 0.85rem; line-height: 1.5;">
                        {code_analysis.get('space_explanation', '')}
                    </p>
                </div>
            ''')
        
        html_parts.append('</div></div>')
    
    # Key Concepts/Insights
    if code_analysis.get('insights'):
        html_parts.append('''
        <div style="margin-bottom: 1.2rem;">
            <h2 style="color: #8b5cf6; font-size: 1.3rem; font-weight: 700; margin: 0 0 0.6rem 0; display: flex; align-items: center; gap: 0.5rem;">
                <span style="background: linear-gradient(135deg, #8b5cf6, #7c3aed); padding: 0.3rem 0.6rem; border-radius: 8px; color: white;">💡</span>
                Key Concepts Highlighted
            </h2>
            <div style="background: linear-gradient(135deg, rgba(139, 92, 246, 0.1), rgba(139, 92, 246, 0.05)); padding: 0.9rem; border-radius: 8px; border-left: 3px solid #8b5cf6;">
        ''')
        
        for insight in code_analysis['insights']:
            html_parts.append(f'''
                <div style="margin-bottom: 0.6rem; padding-left: 1.2rem; position: relative;">
                    <span style="position: absolute; left: 0; top: 0.15rem; color: #8b5cf6; font-size: 1rem;">●</span>
                    <p style="margin: 0; color: var(--color-text); font-size: 0.9rem; line-height: 1.6;">
                        {insight}
                    </p>
                </div>
            ''')
        
        html_parts.append('</div></div>')
    
    # Potential Improvements
    if code_analysis.get('optimizations') or code_analysis.get('edge_cases'):
        html_parts.append('''
        <div style="margin-bottom: 1rem;">
            <h2 style="color: #ec4899; font-size: 1.3rem; font-weight: 700; margin: 0 0 0.6rem 0; display: flex; align-items: center; gap: 0.5rem;">
                <span style="background: linear-gradient(135deg, #ec4899, #db2777); padding: 0.3rem 0.6rem; border-radius: 8px; color: white;">🚀</span>
                Potential Improvements or Notes
            </h2>
        ''')
        
        improvements = code_analysis.get('optimizations', []) + code_analysis.get('edge_cases', [])
        if improvements:
            html_parts.append('<div style="background: linear-gradient(135deg, rgba(236, 72, 153, 0.1), rgba(236, 72, 153, 0.05)); padding: 0.9rem; border-radius: 8px; border-left: 3px solid #ec4899;">')
            for improvement in improvements:
                html_parts.append(f'''
                    <div style="margin-bottom: 0.6rem; padding-left: 1.2rem; position: relative;">
                        <span style="position: absolute; left: 0; top: 0.15rem; color: #ec4899; font-size: 1rem;">●</span>
                        <p style="margin: 0; color: var(--color-text); font-size: 0.9rem; line-height: 1.6;">
                            {improvement}
                        </p>
                    </div>
                ''')
            html_parts.append('</div>')
        
        html_parts.append('</div>')
    
    # Summary
    html_parts.append(f'''
    <div style="margin-top: 1.2rem;">
        <h2 style="color: #06b6d4; font-size: 1.3rem; font-weight: 700; margin: 0 0 0.6rem 0; display: flex; align-items: center; gap: 0.5rem;">
            <span style="background: linear-gradient(135deg, #06b6d4, #0891b2); padding: 0.3rem 0.6rem; border-radius: 8px; color: white;">📝</span>
            Summary
        </h2>
        <p style="color: var(--color-text); font-size: 0.95rem; line-height: 1.6; margin: 0; background: linear-gradient(135deg, rgba(6, 182, 212, 0.1), rgba(6, 182, 212, 0.05)); padding: 0.9rem; border-radius: 8px; border-left: 3px solid #06b6d4;">
            {code_analysis.get('summary', 'This code demonstrates fundamental programming concepts and can be used as a building block for more complex applications.')}
        </p>
    </div>
    ''')
    
    return "".join(html_parts)


def deep_analyze_code(code, language):
    """
    Deeply analyze code to understand the actual algorithm, not just patterns.
    Returns a comprehensive analysis with step-by-step breakdown.
    SUPPORTS ALL LANGUAGES: Python, Java, C++, C, JavaScript
    """
    import re
    
    # Normalize language name
    language = language.lower().strip()
    lang_map = {'javascript (node.js 12.14.0)': 'javascript', 'java (openjdk 13.0.1)': 'java', 'c++': 'cpp'}
    language = lang_map.get(language, language)
    
    # Remove comments based on language
    if language in ['python']:
        lines = [l for l in code.strip().split('\n') if l.strip() and not l.strip().startswith('#')]
    elif language in ['java', 'cpp', 'c', 'javascript']:
        lines = [l for l in code.strip().split('\n') if l.strip() and not l.strip().startswith('//')]
    else:
        lines = [l for l in code.strip().split('\n') if l.strip()]
    
    code_lower = code.lower()
    
    analysis = {
        'summary': '',
        'steps': [],
        'time_complexity': '',
        'time_explanation': '',
        'space_complexity': '',
        'space_explanation': '',
        'insights': [],
        'edge_cases': [],
        'optimizations': []
    }
    
    # Detect algorithm type by analyzing patterns ACROSS ALL LANGUAGES
    # BFS Detection (multi-language)
    has_bfs = ('deque' in code or 'queue' in code_lower and ('poll' in code_lower or 'popleft' in code or 'remove' in code_lower))
    
    # DFS Detection (multi-language)
    has_dfs = ('stack' in code_lower or 'recursion' in code_lower or 
               ('def ' in code and any(func in code for func in extract_function_names(code))) or  # Python
               (language in ['java', 'cpp', 'c'] and count_function_calls(code) > 0))  # Java/C++/C
    
    # Dynamic Programming (multi-language)
    has_dp = 'dp[' in code or 'memo' in code_lower or 'cache' in code_lower or 'table' in code_lower
    
    # Graph algorithms (multi-language)
    has_graph = ('graph' in code_lower or 'adjacency' in code_lower or 'adj' in code_lower or 
                 'vertex' in code_lower or 'edge' in code_lower or 'node' in code_lower)
    
    # Sorting (multi-language)
    has_sorting = ('sort' in code_lower or 'bubble' in code_lower or 'merge' in code_lower or 
                   'quick' in code_lower or ('swap' in code_lower and count_loop_depth(code) >= 2))
    
    # Binary Search (multi-language)
    has_binary_search = ('binary' in code_lower or ('left' in code_lower and 'right' in code_lower and 'mid' in code_lower))
    
    # Two Pointers (multi-language)
    has_two_pointers = (('while ' in code or 'while(' in code) and 'left' in code_lower and 'right' in code_lower)
    
    # Sliding Window (multi-language)
    has_sliding_window = 'window' in code_lower or ('start' in code_lower and 'end' in code_lower and count_loop_depth(code) == 1)
    
    # Calculate loop depth early
    loop_depth = count_loop_depth(code)
    
    # Generate summary based on algorithm detection
    if has_graph and has_bfs:
        analysis['summary'] = "**Algorithm Type:** Graph Traversal using BFS (Breadth-First Search)\n\nThis solution uses BFS to find shortest paths in an unweighted graph. BFS explores nodes level by level, guaranteeing the shortest path in terms of edge count."
        analysis['time_complexity'] = "O(V + E)"
        analysis['time_explanation'] = "Where V = number of vertices (nodes) and E = number of edges. Each node is visited once, each edge is explored once per direction."
        analysis['space_complexity'] = "O(V)"
        analysis['space_explanation'] = "Queue can hold up to V nodes in worst case, plus distance dictionary stores V entries."
    elif has_graph and has_dfs:
        analysis['summary'] = "**Algorithm Type:** Graph Traversal using DFS (Depth-First Search)\n\nThis solution uses DFS to explore the graph deeply along each branch before backtracking. Useful for pathfinding, cycle detection, and connectivity checks."
        analysis['time_complexity'] = "O(V + E)"
        analysis['time_explanation'] = "Visits each vertex once and explores each edge once."
        analysis['space_complexity'] = "O(V)"
        analysis['space_explanation'] = "Recursion stack (or explicit stack) can go V deep in worst case."
    elif has_dp:
        analysis['summary'] = "**Algorithm Type:** Dynamic Programming\n\nThis solution breaks down the problem into overlapping subproblems and stores results to avoid recomputation. Classic DP approach for optimization problems."
        analysis['time_complexity'] = detect_dp_complexity(code)
        analysis['time_explanation'] = "DP typically reduces exponential time to polynomial by memoization."
        analysis['space_complexity'] = "O(n) to O(n²)"
        analysis['space_explanation'] = "Depends on DP table size - 1D or 2D array."
    elif has_sorting:
        analysis['summary'] = "**Algorithm Type:** Sorting Algorithm\n\nThis code implements a sorting algorithm to arrange elements in order."
        if 'bubble' in code_lower:
            analysis['time_complexity'] = "O(n²)"
            analysis['time_explanation'] = "Nested loops - each element compared with every other element."
        else:
            analysis['time_complexity'] = "O(n log n)"
            analysis['time_explanation'] = "Efficient sorting (merge sort, quick sort, or built-in sort)."
        analysis['space_complexity'] = "O(1) to O(n)"
        analysis['space_explanation'] = "In-place sorts use O(1), recursive sorts use O(log n) stack space."
    elif has_binary_search:
        analysis['summary'] = "**Algorithm Type:** Binary Search\n\nDivide and conquer approach that repeatedly halves the search space. Works only on sorted data."
        analysis['time_complexity'] = "O(log n)"
        analysis['time_explanation'] = "Halves the search space each iteration - logarithmic time."
        analysis['space_complexity'] = "O(1)"
        analysis['space_explanation'] = "Only uses a few variables (left, right, mid)."
    elif has_two_pointers:
        analysis['summary'] = "**Algorithm Type:** Two Pointers Technique\n\nUses two pointers moving towards each other or in same direction to solve the problem efficiently in one pass."
        analysis['time_complexity'] = "O(n)"
        analysis['time_explanation'] = "Single pass through the data with two pointers."
        analysis['space_complexity'] = "O(1)"
        analysis['space_explanation'] = "Only uses pointer variables."
    else:
        # Generic analysis
        loop_depth = count_loop_depth(code)
        if loop_depth >= 2:
            analysis['summary'] = "**Algorithm Type:** Nested Iteration\n\nUses nested loops to process data. Each level of nesting multiplies the complexity."
            analysis['time_complexity'] = f"O(n^{loop_depth})"
            analysis['time_explanation'] = f"Nested loops at depth {loop_depth} - each element processed multiple times."
        elif loop_depth == 1:
            analysis['summary'] = "**Algorithm Type:** Linear Iteration\n\nProcesses data in a single pass through the collection."
            analysis['time_complexity'] = "O(n)"
            analysis['time_explanation'] = "Single loop through the data."
        else:
            analysis['summary'] = "**Algorithm Type:** Sequential Execution\n\nExecutes statements in order without loops or complex control flow."
            analysis['time_complexity'] = "O(1)"
            analysis['time_explanation'] = "Fixed number of operations."
        
        analysis['space_complexity'] = "O(1) to O(n)"
        analysis['space_explanation'] = "Depends on data structures used."
    
    # Generate step-by-step explanation
    analysis['steps'] = generate_intelligent_steps(code, language, has_bfs, has_dfs, has_dp, has_graph, has_sorting)
    
    # Generate insights - ALWAYS provide insights for ALL languages
    if has_bfs:
        analysis['insights'].append("BFS guarantees shortest path in unweighted graphs")
        analysis['insights'].append("Level-by-level exploration ensures optimal solution")
    if has_graph:
        analysis['insights'].append("Adjacency list representation enables O(1) neighbor access")
    if has_dp:
        analysis['insights'].append("Memoization prevents redundant calculations")
    if 'defaultdict' in code:
        analysis['insights'].append("defaultdict automatically initializes missing keys")
    
    # Add general insights based on language features (all languages)
    if language in ['cpp', 'c++']:
        if 'cout' in code:
            analysis['insights'].append("Uses C++ iostream for formatted output")
        if 'vector' in code_lower:
            analysis['insights'].append("STL vectors provide dynamic array functionality with automatic memory management")
        if 'std::' in code:
            analysis['insights'].append("Explicitly uses std namespace for better code clarity")
    elif language in ['java']:
        if 'System.out' in code:
            analysis['insights'].append("Uses standard output stream for console display")
        if 'Scanner' in code:
            analysis['insights'].append("Scanner class provides easy input parsing from various sources")
        if 'public static void main' in code:
            analysis['insights'].append("Main method serves as program entry point - required by JVM")
    elif language in ['javascript', 'js']:
        if 'console.log' in code:
            analysis['insights'].append("console.log() provides output to browser console or Node.js terminal")
        if 'let' in code or 'const' in code:
            analysis['insights'].append("Uses ES6+ variable declarations for better scoping")
    elif language in ['c']:
        if 'printf' in code:
            analysis['insights'].append("printf() provides formatted output with type specifiers")
        if 'scanf' in code:
            analysis['insights'].append("scanf() reads formatted input - requires format specifiers and address-of operator")
    
    # ALWAYS provide at least 2-3 general insights if none exist
    if len(analysis['insights']) == 0:
        analysis['insights'].append("Code follows structured programming principles")
        analysis['insights'].append("Clear variable naming improves code readability")
        if loop_depth > 0:
            analysis['insights'].append("Loop structure enables repetitive operations efficiently")
    
    # Edge cases - ALWAYS provide edge cases for ALL languages
    if has_graph:
        analysis['edge_cases'].append("Disconnected components - some nodes unreachable")
        analysis['edge_cases'].append("Empty graph - no nodes or edges")
    if 'len(' in code or '.length' in code or '.size()' in code:
        analysis['edge_cases'].append("Empty input - array/list with no elements")
    if '/' in code or 'divide' in code_lower:
        analysis['edge_cases'].append("Division by zero - need validation")
    if '[0]' in code or 'first' in code_lower or '.get(0)' in code:
        analysis['edge_cases'].append("Index out of bounds - empty collection access")
    
    # Add language-specific edge cases
    if language in ['c', 'cpp', 'c++']:
        if 'cin' in code or 'scanf' in code:
            analysis['edge_cases'].append("Invalid input type - user enters wrong data type")
        if 'new' in code or 'malloc' in code:
            analysis['edge_cases'].append("Memory allocation failure - insufficient RAM")
        if 'pointer' in code_lower or '*' in code:
            analysis['edge_cases'].append("Null pointer dereference - accessing invalid memory")
    elif language in ['java']:
        if 'Scanner' in code:
            analysis['edge_cases'].append("InputMismatchException - wrong input type provided")
        if 'Integer.parseInt' in code:
            analysis['edge_cases'].append("NumberFormatException - invalid number format")
    
    # ALWAYS provide at least 2-3 general edge cases if none exist
    if len(analysis['edge_cases']) == 0:
        analysis['edge_cases'].append("Invalid input - data doesn't match expected format")
        analysis['edge_cases'].append("Boundary conditions - minimum/maximum input values")
        if 'int' in code_lower or 'integer' in code_lower:
            analysis['edge_cases'].append("Integer overflow - result exceeds data type limits")
    
    # Optimizations - ALWAYS provide optimizations for ALL languages
    if loop_depth >= 2 and not has_dp:
        analysis['optimizations'].append("Consider using dynamic programming to reduce time complexity")
    if 'append' in code and 'for ' in code:
        analysis['optimizations'].append("Use list comprehension instead of append in loop")
    if has_dfs and not 'iterative' in code_lower:
        analysis['optimizations'].append("Iterative DFS with explicit stack to avoid recursion depth limit")
    
    # Add language-specific optimizations
    if language in ['cpp', 'c++']:
        if 'endl' in code:
            analysis['optimizations'].append("Use '\\n' instead of endl to avoid unnecessary buffer flushes")
        if 'cout' in code and loop_depth > 0:
            analysis['optimizations'].append("Cache I/O operations - consider buffered output for large data")
    elif language in ['java']:
        if 'String' in code and '+' in code and loop_depth > 0:
            analysis['optimizations'].append("Use StringBuilder instead of String concatenation in loops")
        if 'System.out.println' in code and loop_depth > 0:
            analysis['optimizations'].append("Consider buffered output for better performance with many prints")
    elif language in ['python']:
        if 'append' in code and loop_depth > 0:
            analysis['optimizations'].append("Use list comprehension for cleaner and faster code")
    
    # ALWAYS provide at least 2-3 general optimizations if none exist
    if len(analysis['optimizations']) == 0:
        analysis['optimizations'].append("Add input validation to handle edge cases gracefully")
        analysis['optimizations'].append("Consider adding comments for complex logic")
        if loop_depth == 0:
            analysis['optimizations'].append("Code is already simple and efficient for its purpose")
    
    return analysis


def extract_function_names(code):
    """Extract function names from code (all languages)"""
    import re
    # Python
    py_matches = re.findall(r'def\s+(\w+)\s*\(', code)
    # Java/C++/C/JavaScript
    c_matches = re.findall(r'\b(?:void|int|String|boolean|char|float|double|long|short)\s+(\w+)\s*\(', code)
    js_matches = re.findall(r'\bfunction\s+(\w+)\s*\(', code)
    return py_matches + c_matches + js_matches


def count_function_calls(code):
    """Count how many times functions are called (for recursion detection)"""
    import re
    func_names = extract_function_names(code)
    call_count = 0
    for func in func_names:
        # Count occurrences of function name followed by ( that are NOT the definition
        pattern = r'\b' + re.escape(func) + r'\s*\('
        all_matches = len(re.findall(pattern, code))
        # Subtract 1 for the definition itself
        if all_matches > 1:
            call_count += (all_matches - 1)
    return call_count


def count_loop_depth(code):
    """Count maximum nesting depth of loops (all languages)"""
    max_depth = 0
    current_depth = 0
    for line in code.split('\n'):
        indent = len(line) - len(line.lstrip())
        # Python/JavaScript/Java/C++/C style loops
        if 'for ' in line or 'for(' in line or 'while ' in line or 'while(' in line:
            current_depth += 1
            max_depth = max(max_depth, current_depth)
        elif indent == 0 and line.strip():
            current_depth = 0
    return max_depth


def detect_dp_complexity(code):
    """Detect DP complexity based on table dimensions"""
    if 'dp[' in code:
        if '][' in code:
            return "O(n²) or O(n*m)"
        else:
            return "O(n)"
    return "O(n)"


def generate_intelligent_steps(code, language, has_bfs, has_dfs, has_dp, has_graph, has_sorting):
    """
    Generate intelligent step-by-step explanation based on actual code structure.
    SUPPORTS ALL LANGUAGES: Python, Java, C++, C, JavaScript
    """
    steps = []
    lines = [l for l in code.strip().split('\n') if l.strip()]
    
    # Language-specific patterns
    is_python = language in ['python']
    is_java = language in ['java']
    is_cpp = language in ['cpp', 'c++', 'c']
    is_js = language in ['javascript', 'js']
    
    # Group lines into logical sections
    current_section = []
    section_type = None
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        
        # Detect section boundaries (multi-language)
        # Imports/Includes
        if ('import ' in stripped or 'from ' in stripped or '#include' in stripped or 'require(' in stripped):
            if current_section:
                steps.append(create_step_from_section(current_section, section_type, language))
            current_section = [line]
            section_type = 'import'
        # Function definitions (all languages)
        elif (stripped.startswith('def ') or  # Python
              'public ' in stripped or 'private ' in stripped or 'static ' in stripped or  # Java
              'function ' in stripped or  # JavaScript
              ('void' in stripped or 'int' in stripped or 'String' in stripped) and '(' in stripped):  # C/C++/Java
            if current_section:
                steps.append(create_step_from_section(current_section, section_type, language))
            current_section = [line]
            section_type = 'function_def'
        # Graph initialization (all languages)
        elif ('graph' in stripped.lower() or 'adj' in stripped.lower()) and '=' in stripped:
            if current_section:
                steps.append(create_step_from_section(current_section, section_type, language))
            current_section = [line]
            section_type = 'graph_init'
        # Loop detection (all languages)
        elif ('for ' in stripped or 'for(' in stripped or 'while ' in stripped or 'while(' in stripped):
            if current_section and section_type != 'loop':
                steps.append(create_step_from_section(current_section, section_type, language))
            current_section.append(line)
            section_type = 'loop'
        # Condition detection (all languages)
        elif ('if ' in stripped or 'if(' in stripped) and section_type != 'loop':
            if current_section:
                steps.append(create_step_from_section(current_section, section_type, language))
            current_section = [line]
            section_type = 'condition'
        # Return statements (all languages)
        elif 'return ' in stripped or 'return;' in stripped:
            current_section.append(line)
            steps.append(create_step_from_section(current_section, section_type, language))
            current_section = []
            section_type = None
        else:
            current_section.append(line)
    
    if current_section:
        steps.append(create_step_from_section(current_section, section_type, language))
    
    # FALLBACK: Ensure EVERY language gets detailed steps (minimum 3-5 steps)
    if len(steps) < 3:
        # If we have very few steps, add more detailed analysis
        all_lines = '\n'.join(lines)
        
        # Add step for includes/imports if present
        if any(kw in all_lines for kw in ['#include', 'import ', 'using', 'require(']):
            if not any(s.get('title') == 'Load Required Libraries' for s in steps):
                include_lines = [l for l in lines if any(kw in l for kw in ['#include', 'import ', 'using', 'require('])]
                if include_lines:
                    steps.insert(0, {
                        'title': 'Load Required Libraries',
                        'code_block': '\n'.join(include_lines),
                        'explanation': 'Imports necessary libraries and modules that provide pre-built functionality. This allows the code to use external tools without reimplementing them.',
                        'why': 'External libraries save development time and provide tested, optimized implementations.'
                    })
        
        # Add step for main function/entry point
        if 'main' in all_lines.lower() or 'def ' in all_lines or 'function ' in all_lines:
            if not any('main' in s.get('title', '').lower() or 'function' in s.get('title', '').lower() for s in steps):
                main_lines = [l for l in lines if 'main' in l.lower() or 'def ' in l or 'function ' in l]
                if main_lines:
                    steps.append({
                        'title': 'Program Entry Point',
                        'code_block': main_lines[0],
                        'explanation': 'Defines the starting point of program execution. When the program runs, this is where it begins. This is required by most programming languages to know where to start.',
                        'why': 'Every program needs a clear entry point for the runtime environment to begin execution.'
                    })
        
        # Add step for variable declarations/initialization
        if '=' in all_lines:
            if not any('variable' in s.get('title', '').lower() or 'initialize' in s.get('title', '').lower() for s in steps):
                var_lines = [l for l in lines if '=' in l and '==' not in l and '!=' not in l][:3]
                if var_lines:
                    steps.append({
                        'title': 'Initialize Variables',
                        'code_block': '\n'.join(var_lines),
                        'explanation': 'Declares and initializes variables with starting values. Variables are named storage locations in memory that hold data during program execution.',
                        'why': 'Proper initialization ensures variables have defined values before use, preventing unpredictable behavior.'
                    })
        
        # Add step for output statements
        if any(kw in all_lines for kw in ['cout', 'printf', 'println', 'print(', 'console.log']):
            if not any('output' in s.get('title', '').lower() or 'display' in s.get('title', '').lower() or 'print' in s.get('title', '').lower() for s in steps):
                output_lines = [l for l in lines if any(kw in l for kw in ['cout', 'printf', 'println', 'print(', 'console.log'])][:2]
                if output_lines:
                    steps.append({
                        'title': 'Display Output',
                        'code_block': '\n'.join(output_lines),
                        'explanation': 'Outputs results to the console/terminal for the user to see. This is how programs communicate their results or status to users.',
                        'why': 'Displaying output allows users to verify program behavior and see computed results.'
                    })
        
        # Add step for input operations
        if any(kw in all_lines for kw in ['cin', 'scanf', 'Scanner', 'input(', 'readline']):
            if not any('input' in s.get('title', '').lower() or 'read' in s.get('title', '').lower() for s in steps):
                input_lines = [l for l in lines if any(kw in l for kw in ['cin', 'scanf', 'Scanner', 'input(', 'readline'])][:2]
                if input_lines:
                    steps.append({
                        'title': 'Read User Input',
                        'code_block': '\n'.join(input_lines),
                        'explanation': 'Reads data from the user or external source. Programs often need input to make decisions or perform calculations based on user-provided data.',
                        'why': 'Input operations make programs interactive and adaptable to different scenarios.'
                    })
    
    return steps[:10]  # Limit to 10 steps for readability


def create_step_from_section(lines, section_type, language):
    """Create a step explanation from a code section - SUPPORTS ALL LANGUAGES"""
    code_block = '\n'.join(lines)
    code_lower = code_block.lower()
    
    # Detect BFS/Queue usage (multi-language)
    has_queue = ('deque' in code_block or 'queue' in code_lower or 
                 'Queue' in code_block or 'LinkedList' in code_block or
                 'poll' in code_lower or 'offer' in code_lower)
    
    if section_type == 'graph_init':
        # Language-specific graph explanations
        if language in ['java']:
            graph_type = "HashMap" if "HashMap" in code_block else "adjacency list"
        elif language in ['cpp', 'c++', 'c']:
            graph_type = "vector" if "vector" in code_block else "adjacency list"
        elif language in ['javascript', 'js']:
            graph_type = "Map" if "Map" in code_block else "object"
        else:
            graph_type = "dictionary" if "dict" in code_lower or "{}" in code_block else "adjacency list"
        
        return {
            'title': 'Initialize Graph Structure',
            'code_block': code_block,
            'explanation': f'Creates an adjacency list using {graph_type} to represent the graph. Each key/index is a node, and its value is a list of neighboring nodes. This representation allows O(1) average-case access to neighbors.',
            'why': 'Adjacency lists are efficient for sparse graphs and make traversal algorithms simple to implement.'
        }
    elif section_type == 'loop' and has_queue:
        return {
            'title': 'BFS Traversal',
            'code_block': code_block,
            'explanation': 'Performs breadth-first search using a queue. Explores nodes level by level, ensuring shortest path discovery. Each node is visited once and marked as visited.',
            'why': 'BFS guarantees shortest path in unweighted graphs because it explores all nodes at distance k before exploring nodes at distance k+1.'
        }
    elif section_type == 'loop':
        return {
            'title': 'Iterate Through Data',
            'code_block': code_block,
            'explanation': f'Loops through the collection processing each element. {analyze_loop_body(code_block, language)}',
            'why': 'Iteration is necessary to examine or transform each element in the data structure.'
        }
    elif section_type == 'condition':
        return {
            'title': 'Conditional Check',
            'code_block': code_block,
            'explanation': f'Evaluates a condition and takes different paths based on the result. {extract_condition_logic(code_block, language)}',
            'why': 'Handles different scenarios or edge cases in the algorithm.'
        }
    elif section_type == 'function_def':
        return {
            'title': 'Function Definition',
            'code_block': code_block,
            'explanation': f'Defines a reusable function that encapsulates part of the algorithm. {extract_function_purpose(code_block, language)}',
            'why': 'Functions enable code reuse and make the algorithm more modular and testable.'
        }
    else:
        return {
            'title': 'Process Data',
            'code_block': code_block,
            'explanation': f'Executes operations on the data. {summarize_operations(code_block, language)}',
            'why': 'Necessary computation step in the algorithm.'
        }


def analyze_loop_body(code, language):
    """Analyze what happens inside a loop - SUPPORTS ALL LANGUAGES"""
    code_lower = code.lower()
    
    # Detect collection operations (multi-language)
    has_add = ('append' in code or 'add(' in code or 'push(' in code or 
               'push_back' in code or 'insert' in code)
    has_condition = 'if ' in code or 'if(' in code
    has_accumulation = '+=' in code or '-=' in code or '*=' in code or '/=' in code
    
    if has_add:
        return "Builds a new collection by adding elements one by one."
    elif has_condition:
        return "Applies conditional logic to filter or transform elements."
    elif has_accumulation:
        return "Accumulates values or maintains a running total."
    else:
        return "Processes each element with some operation."


def extract_condition_logic(code, language):
    """Extract the purpose of a conditional - SUPPORTS ALL LANGUAGES"""
    code_lower = code.lower()
    
    # Multi-language pattern detection
    has_not_in = 'not in' in code or '!contains' in code or '.find' in code or 'count' in code_lower
    has_size_check = ('len(' in code or '.size()' in code or '.length' in code) and ('== 1' in code or '==1' in code)
    has_zero_check = '== 0' in code or '==0' in code or 'not ' in code or '!' in code
    
    if has_not_in:
        return "Checks if an element hasn't been seen before (visited tracking)."
    elif has_size_check:
        return "Identifies elements with exactly one connection (leaf nodes)."
    elif has_zero_check:
        return "Handles the empty or base case."
    else:
        return "Evaluates a specific condition relevant to the algorithm."


def extract_function_purpose(code, language):
    """Determine what a function does - SUPPORTS ALL LANGUAGES"""
    has_return = 'return ' in code or 'return;' in code
    has_operation = '+' in code or '-' in code or '*' in code or '/' in code
    
    if has_return and has_operation:
        return "Combines or aggregates values to produce a result."
    elif has_return:
        return "Computes and returns a value based on the input."
    else:
        return "Performs operations without returning a value."


def summarize_operations(code, language):
    """Summarize what operations are being performed - SUPPORTS ALL LANGUAGES"""
    operations = []
    if '=' in code and '[' in code:
        operations.append("Initializes or updates data structures")
    if 'sum(' in code or 'max(' in code or 'min(' in code:
        operations.append("Applies aggregate functions")
    if '.get(' in code:
        operations.append("Safely accesses dictionary values with defaults")
    
    return ', '.join(operations) if operations else "Performs necessary computations"


def detect_program_purpose(code, language):
    """Detect what the program does"""
    code_lower = code.lower()
    
    if 'sort' in code_lower or 'sorted' in code_lower:
        return "Sorting algorithm - arranges elements in order"
    elif 'search' in code_lower or 'find' in code_lower:
        return "Search algorithm - finds specific elements"
    elif 'fibonacci' in code_lower or 'fib' in code_lower:
        return "Fibonacci sequence generator"
    elif 'prime' in code_lower:
        return "Prime number checker/generator"
    elif 'factorial' in code_lower:
        return "Factorial calculator"
    elif 'sum' in code_lower or 'total' in code_lower:
        return "Summation/accumulation of values"
    elif 'max' in code_lower or 'min' in code_lower:
        return "Find maximum/minimum value"
    elif 'reverse' in code_lower:
        return "Reverse data structure or string"
    elif 'palindrome' in code_lower:
        return "Palindrome checker"
    elif 'count' in code_lower:
        return "Count occurrences or elements"
    elif 'print' in code_lower or 'output' in code_lower:
        return "Display/output data to user"
    else:
        return "General computation and data processing"


def detect_algorithm_approach(code, language):
    """Detect the algorithmic approach used"""
    code_lower = code.lower()
    
    if 'for' in code_lower and 'for' in code_lower[code_lower.find('for')+3:]:
        return "Nested iteration (nested loops) - O(n²) or higher complexity"
    elif 'while' in code_lower or 'for' in code_lower:
        return "Iterative approach - processes data step-by-step in loops"
    elif 'def' in code and code.count('def') > 0:
        func_name = code.split('def')[1].split('(')[0].strip() if 'def' in code else ''
        if func_name and func_name in code[code.find(func_name)+len(func_name):]:
            return "Recursive approach - function calls itself"
        else:
            return "Modular approach - uses functions for code organization"
    elif 'if' in code_lower:
        return "Conditional logic - makes decisions based on conditions"
    else:
        return "Sequential execution - runs statements in order"


def analyze_lines_with_complexity(code, language):
    """Analyze each line with complexity annotations"""
    lines = [l for l in code.strip().split('\n') if l.strip() and not l.strip().startswith('#')]
    analysis = []
    
    for i, line in enumerate(lines[:10], 1):  # Limit to first 10 lines for readability
        stripped = line.strip()
        
        info = {
            'line_num': i,
            'code': stripped[:60],  # Truncate long lines
            'what': explain_what(stripped, language),
            'why': explain_why(stripped, language),
            'time_complexity': estimate_time_complexity(stripped),
            'space_complexity': estimate_space_complexity(stripped)
        }
        analysis.append(info)
    
    if len(lines) > 10:
        analysis.append({
            'line_num': '...',
            'code': f'({len(lines) - 10} more lines)',
            'what': 'Additional code continues...',
            'why': 'Omitted for brevity',
            'time_complexity': 'Varies',
            'space_complexity': 'Varies'
        })
    
    return analysis


def explain_what(line, language):
    """Explain what the line does - SUPPORTS ALL LANGUAGES"""
    line_lower = line.lower()
    
    # Function definitions (all languages)
    if ('def ' in line or 'function ' in line or 
        ('public ' in line and '(' in line) or ('private ' in line and '(' in line) or
        ('void' in line and '(' in line) or ('int main' in line)):
        return "Function definition - creates reusable code block"
    
    # Loops (all languages)
    elif 'for ' in line or 'for(' in line or 'while ' in line or 'while(' in line:
        return "Loop statement - repeats code multiple times"
    
    # Conditionals (all languages)
    elif 'if ' in line or 'if(' in line or 'else' in line or 'switch' in line:
        return "Conditional check - makes decision"
    
    # Return statements (all languages)
    elif 'return' in line:
        return "Returns value back to caller"
    
    # Output statements (multi-language)
    elif ('print' in line or 'console.log' in line or 'System.out' in line or 
          'cout' in line or 'printf' in line or 'Console.Write' in line):
        return "Output statement - displays result"
    
    # Input statements (multi-language)
    elif ('input(' in line or 'Scanner' in line or 'cin' in line or 'scanf' in line):
        return "Input statement - reads user data"
    
    # Class/Object creation (multi-language)
    elif 'class ' in line or 'struct ' in line:
        return "Class/Structure definition - defines custom data type"
    elif 'new ' in line:
        return "Object instantiation - creates new instance"
    
    # Assignment (all languages)
    elif '=' in line and '==' not in line and '!=' not in line:
        return "Assignment - stores value in variable"
    
    # Import/Include statements (all languages)
    elif 'import ' in line or '#include' in line or 'using' in line or 'require(' in line:
        return "Import statement - loads external library"
    
    # Array/Collection operations
    elif '.append(' in line or '.add(' in line or '.push(' in line or 'push_back' in line:
        return "Collection operation - adds element to collection"
    elif '.pop(' in line or '.remove(' in line:
        return "Collection operation - removes element from collection"
    
    else:
        return "Executes statement or expression"


def explain_why(line, language):
    """Explain why this line is needed - SUPPORTS ALL LANGUAGES"""
    line_lower = line.lower()
    
    # Function definitions (all languages)
    if ('def ' in line or 'function ' in line or 
        ('public ' in line and '(' in line) or ('private ' in line and '(' in line) or
        ('void' in line and '(' in line) or ('int main' in line)):
        return "Enables code reuse and organization"
    
    # Loops (all languages)
    elif 'for ' in line or 'for(' in line or 'while ' in line or 'while(' in line:
        return "Processes multiple items or repeats until condition met"
    
    # Conditionals (all languages)
    elif 'if ' in line or 'if(' in line or 'else' in line or 'switch' in line:
        return "Handles different scenarios based on conditions"
    
    # Return statements
    elif 'return' in line:
        return "Provides result to be used elsewhere"
    
    # Output statements (multi-language)
    elif ('print' in line or 'console.log' in line or 'System.out' in line or 
          'cout' in line or 'printf' in line):
        return "Shows results to user for verification/debugging"
    
    # Input statements (multi-language)
    elif ('input(' in line or 'Scanner' in line or 'cin' in line or 'scanf' in line):
        return "Collects data from user for processing"
    
    # Class/Object creation
    elif 'class ' in line or 'struct ' in line:
        return "Encapsulates related data and behavior"
    elif 'new ' in line:
        return "Allocates memory and initializes object state"
    
    # Assignment
    elif '=' in line and '==' not in line and '!=' not in line:
        return "Stores data for later use in program"
    
    # Import/Include
    elif 'import ' in line or '#include' in line or 'using' in line or 'require(' in line:
        return "Adds functionality from external code"
    
    # Collection operations
    elif '.append(' in line or '.add(' in line or '.push(' in line or 'push_back' in line:
        return "Builds or modifies data collection"
    elif '.pop(' in line or '.remove(' in line:
        return "Removes processed or unnecessary elements"
    
    else:
        return "Performs necessary computation or operation"


def estimate_time_complexity(line):
    """Estimate time complexity of a line"""
    if 'for ' in line or 'while ' in line:
        return "O(n) - linear iteration"
    elif 'sort' in line.lower():
        return "O(n log n) - efficient sorting"
    elif '.append' in line or '.push' in line:
        return "O(1) - constant time"
    elif '.pop' in line and '(0)' in line:
        return "O(n) - removes from front"
    else:
        return "O(1) - constant time operation"


def estimate_space_complexity(line):
    """Estimate space complexity of a line"""
    if '[' in line and ']' in line and 'for' in line:
        return "O(n) - creates new list"
    elif '=' in line and ('[' in line or '{' in line):
        return "O(n) - allocates collection"
    elif 'def ' in line:
        return "O(1) - function definition"
    else:
        return "O(1) - uses existing memory"


def calculate_overall_complexity(code, language):
    """Calculate overall time and space complexity"""
    code_lower = code.lower()
    
    # Count nested loops
    loop_depth = 0
    max_depth = 0
    for char in code:
        if 'for ' in code[max(0, code.find(char)-4):code.find(char)+4]:
            loop_depth += 1
            max_depth = max(max_depth, loop_depth)
    
    # Detect complexity patterns
    has_nested_loop = code_lower.count('for') >= 2 or code_lower.count('while') >= 2
    has_recursion = 'def' in code and any(func in code.split('def')[1:][0] for func in [''])
    has_sort = 'sort' in code_lower
    
    if has_nested_loop:
        time = "O(n²)"
        time_exp = "Nested loops cause quadratic growth - doubles input = 4x time"
        example = "For n=100: ~10,000 operations; For n=1000: ~1,000,000 operations"
    elif has_sort:
        time = "O(n log n)"
        time_exp = "Efficient sorting algorithm - balanced between linear and quadratic"
        example = "For n=100: ~664 operations; For n=1000: ~9,966 operations"
    elif 'for' in code_lower or 'while' in code_lower:
        time = "O(n)"
        time_exp = "Linear growth - doubles input = doubles time"
        example = "For n=100: ~100 operations; For n=1000: ~1000 operations"
    else:
        time = "O(1)"
        time_exp = "Constant time - same speed regardless of input size"
        example = "Always takes same time regardless of data size"
    
    # Space complexity
    if '[]' in code or '{}' in code or 'list' in code_lower:
        space = "O(n)"
        space_exp = "Stores data in memory proportional to input size"
    else:
        space = "O(1)"
        space_exp = "Uses fixed memory regardless of input size"
    
    return {
        'time': time,
        'time_explanation': time_exp,
        'space': space,
        'space_explanation': space_exp,
        'example': example if 'example' in locals() else None
    }


def analyze_edge_cases_and_optimizations(code, language):
    """Identify edge cases and suggest optimizations"""
    code_lower = code.lower()
    edge_cases = []
    optimizations = []
    
    # Edge cases
    if 'list' in code_lower or '[' in code:
        edge_cases.append("Empty list/array - handle [] case")
        edge_cases.append("Single element - ensure works with minimal data")
    
    if '/' in code or 'divide' in code_lower:
        edge_cases.append("Division by zero - add validation")
    
    if 'int' in code_lower or 'number' in code_lower:
        edge_cases.append("Negative numbers - verify logic handles them")
        edge_cases.append("Zero value - test with 0 input")
    
    if 'string' in code_lower or '"' in code or "'" in code:
        edge_cases.append("Empty string - handle '' case")
        edge_cases.append("Special characters - test with spaces/symbols")
    
    # Optimizations
    if code_lower.count('for') >= 2:
        optimizations.append("Consider reducing nested loops - use hash maps or dynamic programming")
    
    if 'append' in code_lower and 'for' in code_lower:
        optimizations.append("Use list comprehension instead of append in loop for better performance")
    
    if 'sort' in code_lower:
        optimizations.append("If data already partially sorted, use insertion sort for O(n) best case")
    
    if not edge_cases:
        edge_cases.append("No obvious edge cases detected - still test with boundary values")
    
    if not optimizations:
        optimizations.append("Code looks reasonably efficient for the task")
    
    return {
        'edge_cases': edge_cases[:3],  # Limit to top 3
        'optimizations': optimizations[:3]  # Limit to top 3
    }


@app.route("/explain", methods=["POST"])
def explain_code():
    """Generate comprehensive code explanations using the new 4-box system"""
    print("\n" + "="*60)
    print("📝 EXPLAIN ROUTE CALLED")
    print("="*60)
    data = request.get_json() or {}
    code = data.get("code", "")
    language = data.get("language", "python").lower().strip()
    print(f"📌 Code length: {len(code)} chars")
    print(f"📌 Language: {language}")

    if not code:
        return jsonify({"explanation": "⚠️ No code provided."}), 400

    # Validate that input is actual code, not just text
    if not is_valid_code(code):
        return jsonify({"explanation": "⚠️ Please enter actual code, not plain text."}), 400

    # Normalize language names
    lang_normalize = {
        "javascript (node.js 12.14.0)": "javascript",
        "java (openjdk 13.0.1)": "java",
        "c++": "cpp"
    }
    language = lang_normalize.get(language, language)

    # Generate comprehensive explanation using new system
    explanation_text = generate_comprehensive_explanation(code, language)

    return jsonify({"explanation": explanation_text})


# Old explanation code removed - using new comprehensive system above


@app.route("/old_explain_backup", methods=["POST"])
def old_explain_code():
    """OLD SYSTEM - Kept as backup"""
    data = request.get_json() or {}
    code = data.get("code", "")
    language = data.get("language", "python").lower().strip()

    if not code:
        return jsonify({"explanation": "⚠️ No code provided."}), 400

    lang_normalize = {
        "javascript (node.js 12.14.0)": "javascript",
        "java (openjdk 13.0.1)": "java",
        "c++": "cpp"
    }
    language = lang_normalize.get(language, language)

    explanation_parts = []
    explanation_parts.append("╔" + "═" * 58 + "╗")
    explanation_parts.append("║" + " " * 15 + "📚 CODE EXPLANATION 📚" + " " * 20 + "║")
    explanation_parts.append("║" + " " * 10 + f"Language: {language.upper()} 🔤" + " " * (47 - len(language)) + "║")
    explanation_parts.append("╚" + "═" * 58 + "╝")
    explanation_parts.append("")

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
    """Generate comprehensive code explanations - requires login"""
    if not check_user():
        return jsonify({"html": "<div style='color:#ff5459; padding: 1rem; background: rgba(255,84,89,0.1); border-radius: 8px;'>⚠️ Please login to use the AI Explain feature. <a href='/login' style='color: #00d9ff; text-decoration: underline;'>Login here</a></div>"}), 401
    
    print("\n" + "="*60)
    print("🎨 EXPLAIN_HTML ROUTE CALLED")
    print("="*60)
    
    data = request.get_json() or {}
    code = data.get("code", "")
    language = data.get("language", "python").lower().strip()
    
    print(f"📌 Code length: {len(code)} chars")
    print(f"📌 Language: {language}")

    if not code:
        return jsonify({"html": "<div style='color:red;'>⚠️ No code provided.</div>"}), 400

    # Validate that input is actual code, not just text
    if not is_valid_code(code):
        return jsonify({"html": "<div style='color:orange;'>⚠️ Please enter actual code, not plain text.</div>"}), 400

    # Normalize language names
    lang_normalize = {
        "javascript (node.js 12.14.0)": "javascript",
        "java (openjdk 13.0.1)": "java",
        "c++": "cpp"
    }
    language = lang_normalize.get(language, language)

    # Generate AI-style comprehensive explanation with colored boxes
    # This now returns HTML directly, not plain text
    explanation_html = generate_comprehensive_explanation(code, language)
    
    # Build wrapper HTML with header
    html = f'''
    <div class="explanation-container" style="padding: 1.5rem;">
        <div class="header-box" style="text-align: center; margin-bottom: 2rem; padding-bottom: 1.2rem; border-bottom: 2px solid var(--color-primary);">
            <h2 style="color: var(--color-primary); margin: 0; font-size: 1.6rem; font-weight: 700;">
                📚 AI-Powered Code Explanation
            </h2>
            <p style="color: var(--color-text-secondary); margin: 0.5rem 0 0 0; font-size: 0.9rem;">
                Language: <span style="color: var(--color-primary); font-weight: 600;">{language.upper()}</span> | 
                Analysis: <span style="color: var(--color-success); font-weight: 600;">ChatGPT-Style</span>
            </p>
        </div>
        <div style="line-height: 1.6;">
            {explanation_html}
        </div>
    </div>
    '''
    
    return jsonify({"html": html})


# ---------------- AI OPTIMIZER ----------------

def ai_optimize_code(code, language):
    """
    AI-powered code optimizer using Google Gemini API.
    Works for ALL languages: Python, JavaScript, Java, C++, C, etc.
    Returns optimized code with detailed explanations.
    """
    if not gemini_model:
        # Fallback to old optimizer if API not available
        if language == "python":
            return ai_optimize_python_fallback(code)
        else:
            return {
                "optimized_code": code,
                "optimizations": [{
                    "change": "AI API not configured",
                    "description": "Add GEMINI_API_KEY to .env file to enable AI optimization",
                    "benefit": "Intelligent optimization for all languages"
                }]
            }
    
    try:
        prompt = f"""You are an expert code optimizer. Analyze this {language} code and provide optimizations.

**IMPORTANT INSTRUCTIONS:**
1. Return ONLY valid JSON (no markdown, no backticks, no extra text)
2. Provide actual optimized code, not just suggestions
3. Focus on: performance, readability, best practices, algorithm efficiency
4. If code is already optimal, make minor improvements and explain

**Code to optimize:**
```{language}
{code}
```

**Return this EXACT JSON format:**
{{
  "optimized_code": "the complete optimized code here",
  "optimizations": [
    {{
      "change": "Brief title of what changed",
      "description": "Detailed explanation of the optimization",
      "benefit": "What improvement this brings (performance/readability/maintainability)"
    }}
  ]
}}

Focus on real optimizations like:
- Algorithm complexity improvements (O(n²) → O(n log n))
- Removing redundant operations
- Better data structures (list → set, loops → comprehensions)
- Memory efficiency
- Language-specific best practices
- Code readability improvements

Return ONLY the JSON, nothing else."""

        response = gemini_model.generate_content(prompt)
        response_text = response.text.strip()
        
        # Clean up response (remove markdown code blocks if present)
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        elif response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        response_text = response_text.strip()
        
        # Parse JSON response
        result = json.loads(response_text)
        
        # Validate response format
        if "optimized_code" not in result or "optimizations" not in result:
            raise ValueError("Invalid response format from AI")
        
        return result
        
    except json.JSONDecodeError as e:
        print(f"JSON parsing error: {e}")
        print(f"Response was: {response_text[:500]}")
        # Fallback to old optimizer
        if language == "python":
            return ai_optimize_python_fallback(code)
        else:
            return {
                "optimized_code": code,
                "optimizations": [{
                    "change": "Optimization analysis failed",
                    "description": "Could not parse AI response. Try again or check your code syntax.",
                    "benefit": "Error in AI processing"
                }]
            }
    except Exception as e:
        print(f"AI optimization error: {e}")
        # Fallback to old optimizer
        if language == "python":
            return ai_optimize_python_fallback(code)
        else:
            return {
                "optimized_code": code,
                "optimizations": [{
                    "change": "Optimization failed",
                    "description": f"Error: {str(e)}",
                    "benefit": "Please try again"
                }]
            }


def ai_optimize_python_fallback(code):
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
    Enhanced with Google Gemini AI for deeper analysis.
    """
    # Try AI-powered debugging first if available
    if gemini_model and language in ['python', 'javascript', 'java', 'cpp', 'c']:
        ai_result = ai_enhance_debug(code, language, issues)
        if ai_result:
            return ai_result
    
    # Fallback to rule-based debugging
    return rule_based_debug(code, language, issues)


def ai_enhance_debug(code, language, linter_issues):
    """
    Use AI to provide intelligent bug detection and fixes.
    Combines linter output with AI insights.
    """
    try:
        # Prepare linter context
        linter_context = ""
        if linter_issues and not linter_issues.startswith("✅"):
            linter_context = f"\n\nLinter detected these issues:\n{linter_issues}"
        
        prompt = f"""You are an expert code debugger. Analyze this {language} code for bugs and issues.

**Code:**
```{language}
{code}
```
{linter_context}

**Return ONLY valid JSON with this structure:**
{{
  "bugs_found": [
    {{
      "line": 0,
      "type": "Bug category",
      "severity": "high/medium/low",
      "message": "Clear explanation of the issue",
      "code": "the problematic line of code",
      "fix": "suggested fix (optional)"
    }}
  ],
  "fixed_code": "complete corrected code here",
  "suggestions": [
    "Best practice suggestion 1",
    "Best practice suggestion 2"
  ],
  "confidence": "high/medium/low"
}}

Look for:
- Syntax errors (missing colons, parentheses, brackets)
- Logic errors (infinite loops, wrong operators, off-by-one)
- Runtime errors (null/undefined access, division by zero)
- Type errors (wrong data types)
- Edge cases not handled
- Performance issues
- Security vulnerabilities

Be specific about line numbers and provide actionable fixes. Return ONLY the JSON."""

        response = gemini_model.generate_content(prompt)
        response_text = response.text.strip()
        
        # Clean up response
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        elif response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        response_text = response_text.strip()
        
        # Parse JSON
        result = json.loads(response_text)
        
        # Validate structure
        if "bugs_found" not in result:
            result["bugs_found"] = []
        if "suggestions" not in result:
            result["suggestions"] = []
        if "fixed_code" not in result:
            result["fixed_code"] = code
        if "confidence" not in result:
            result["confidence"] = "medium"
        
        return result
        
    except Exception as e:
        print(f"AI debug error: {e}")
        return None


def rule_based_debug(code, language, issues):
    """
    Rule-based intelligent debugging (fallback when AI is not available).
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
    """Debug code - requires login"""
    if not check_user():
        return jsonify({
            "issues": "⚠️ Please login to use the debugger feature.",
            "fixed_code": "",
            "original_code": "",
            "login_required": True
        }), 401
    
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

# ═══════════════════════════════════════════════════════════════════════
# SAVE CODE API
# ═══════════════════════════════════════════════════════════════════════
@app.route("/api/save", methods=["POST"])
def save_code():
    """Save user code to database"""
    if not check_user():
        return jsonify({"success": False, "error": "Please login to save code"}), 401
    
    try:
        data = request.get_json()
        code = data.get('code', '').strip()
        language = data.get('language', 'Unknown')
        title = data.get('title', 'Untitled')
        
        if not code:
            return jsonify({"success": False, "error": "No code to save"}), 400
        
        # Save to code_history table
        from database import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO code_history (user_id, activity_type, code_snippet, language, title)
            VALUES (%s, %s, %s, %s, %s)
        ''', (session['user_id'], 'saved', code, language, title))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            "success": True,
            "message": f"Code '{title}' saved successfully!"
        })
        
    except Exception as e:
        print(f"Error saving code: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

# ═══════════════════════════════════════════════════════════════════════
# SHARE CODE API
# ═══════════════════════════════════════════════════════════════════════
@app.route("/api/share", methods=["POST"])
def share_code():
    """Create a shareable link for code"""
    if not check_user():
        return jsonify({"success": False, "error": "Please login to share code"}), 401
    
    try:
        data = request.get_json()
        code = data.get('code', '').strip()
        language = data.get('language', 'Unknown')
        title = data.get('title', 'Shared Code')
        
        if not code:
            return jsonify({"success": False, "error": "No code to share"}), 400
        
        # Save to code_history table with 'shared' type
        from database import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO code_history (user_id, activity_type, code_snippet, language, title)
            VALUES (%s, %s, %s, %s, %s)
        ''', (session['user_id'], 'shared', code, language, title))
        
        share_id = cursor.lastrowid
        conn.commit()
        cursor.close()
        conn.close()
        
        # Generate share link
        share_link = f"{request.host_url}shared/{share_id}"
        
        return jsonify({
            "success": True,
            "message": f"Share link created for '{title}'!",
            "share_link": share_link
        })
        
    except Exception as e:
        print(f"Error creating share link: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

# ═══════════════════════════════════════════════════════════════════════
# MY PROJECTS PAGE
# ═══════════════════════════════════════════════════════════════════════
@app.route("/my-projects")
def my_projects():
    """Display user's saved code projects"""
    if not check_user():
        return redirect("/")
    
    try:
        from database import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get user's saved code
        cursor.execute('''
            SELECT id, title, language, code_snippet, created_at, activity_type
            FROM code_history
            WHERE user_id = %s AND activity_type IN ('saved', 'shared')
            ORDER BY created_at DESC
        ''', (session['user_id'],))
        
        projects = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return render_template("my_projects.html", projects=projects, username=session.get('username'))
        
    except Exception as e:
        print(f"Error loading projects: {e}")
        return f"Error loading projects: {e}", 500

# ═══════════════════════════════════════════════════════════════════════
# VIEW SHARED CODE
# ═══════════════════════════════════════════════════════════════════════
@app.route("/shared/<int:share_id>")
def view_shared_code(share_id):
    """View a shared code snippet"""
    try:
        from database import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute('''
            SELECT ch.title, ch.language, ch.code_snippet, ch.created_at, u.username
            FROM code_history ch
            JOIN users u ON ch.user_id = u.id
            WHERE ch.id = %s AND ch.activity_type = 'shared'
        ''', (share_id,))
        
        shared_code = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not shared_code:
            return "Shared code not found", 404
        
        return render_template("shared_code.html", code=shared_code)
        
    except Exception as e:
        print(f"Error loading shared code: {e}")
        return f"Error loading shared code: {e}", 500

if __name__ == "__main__":
    app.run(debug=True, threaded=True)
