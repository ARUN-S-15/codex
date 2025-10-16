# CODEX - Online Code Compiler, Debugger & Optimizer

A professional web-based code development environment that lets you compile, debug, and optimize code in multiple programming languages.

🌐 **Live Demo:** http://127.0.0.1:5000

---

## ✨ Features

### 1. 💻 **Multi-Language Compiler**
- **Supported Languages:** Python, JavaScript, Java, C++, C, and 70+ more
- **Real-time Execution:** Code runs securely using Judge0 API
- **Syntax Highlighting:** Beautiful code editor with line numbers
- **Multiple Themes:** Choose your preferred coding theme
- **Input Support:** Provide stdin input for your programs
- **Fast Execution:** 
  - Python/JavaScript: 2-5 seconds
  - Java/C++/C: 5-15 seconds (compilation included)

### 2. 🪲 **Smart Debugger**
- **Industry-Standard Linters:**
  - Python: pylint (syntax, style, warnings)
  - JavaScript: eslint (best practices, errors)
  - C/C++: cppcheck (bugs, performance)
  - Java: checkstyle (style, errors)

- **Auto-Fix Capabilities:**
  - Python: Missing colons, print statements, indentation
  - JavaScript: Missing semicolons, console.log syntax
  - C/C++: Missing semicolons, printf/scanf syntax

- **Two-Panel Workflow:**
  - Left: Auto-fixed code (ready to copy)
  - Right: Detailed error reports

### 3. ⚡ **Code Optimizer**
- **AI-Powered Analysis:** Advanced code optimization suggestions
- **Performance Tips:** Improve time and space complexity
- **Best Practices:** Follow language-specific conventions
- **Refactoring Ideas:** Better code structure suggestions

### 4. 🤖 **AI Code Explanation**
- **ChatGPT-Style Interface:** Beautiful, conversational explanations
- **Comprehensive Analysis:**
  - What the code does (high-level overview)
  - How it works (step-by-step breakdown)
  - Line-by-line explanations
  - Complexity analysis
  - Best practices and improvements

### 5. 💾 **Project Management**
- **Save Projects:** Save your code for later
- **Share Code:** Generate shareable links
- **Project History:** Access all your saved projects
- **Download Files:** Export code as .py, .js, .java, etc.
- **Search & Filter:** Quickly find your projects

### 6. 👤 **User Authentication**
- **Secure Login/Register:** User account management
- **Session Management:** Stay logged in
- **Personal Dashboard:** View your projects
- **Guest Mode:** Try features without account

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Internet connection (for Judge0 API)

### Installation

1. **Clone the Repository:**
```bash
git clone https://github.com/ESAKKIKANNANP/codex.git
cd codex
```

2. **Install Dependencies:**
```bash
pip install -r requirements.txt
```

3. **Set Up Environment Variables:**
```bash
# Copy the example env file
copy .env.example .env

# Edit .env and add your API keys:
# - GEMINI_API_KEY (for AI features)
# - SECRET_KEY (for session management)
```

4. **Run the Application:**
```bash
python app.py
```

5. **Open in Browser:**
```
http://127.0.0.1:5000
```

---

## 📖 Usage Guide

### Compiling Code

1. Go to **Compiler** page (http://127.0.0.1:5000/compiler)
2. Select your programming language from dropdown
3. Write or paste your code
4. (Optional) Provide input in the "Input" section
5. Click **▶ Run Code**
6. View output in the result panel

### Debugging Code

1. Write code in the compiler
2. Click **🪲 Debug** button in sidebar
3. View:
   - **Left Panel:** Auto-fixed code
   - **Right Panel:** List of issues found
4. Copy the fixed code or address the issues

### Getting AI Explanation

1. Write code in the compiler
2. Click **🤖 Explain** button
3. Get comprehensive ChatGPT-style explanation:
   - What the code does
   - How it works
   - Line-by-line breakdown
   - Complexity analysis
   - Improvement suggestions

### Optimizing Code

1. Write code in the compiler
2. Click **⚡ Optimize** button
3. Get AI-powered optimization suggestions:
   - Performance improvements
   - Better algorithms
   - Memory optimization
   - Code quality tips

### Managing Projects

1. Click **💾 Save** to save current code
2. Click **📁 My Code** to view all projects
3. In My Projects page:
   - 📋 Copy code to clipboard
   - ✏️ Open in editor
   - 🔗 Share with others
   - 💾 Download as file
   - 🗑️ Delete project

---

## 🏗️ Project Structure

```
codex/
├── app.py                  # Main Flask application (3400+ lines)
├── database.py             # Database connection utilities
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── .env                   # Environment variables (create from .env.example)
├── .env.example           # Template for environment setup
├── .gitignore             # Git ignore rules
│
├── static/                # Frontend assets
│   ├── js/               # JavaScript files
│   │   ├── app.js
│   │   ├── compiler.js
│   │   └── script.js
│   └── style/            # CSS stylesheets
│       ├── main.css
│       ├── compiler.css
│       ├── debug.css
│       └── ...
│
├── templates/             # HTML templates (Jinja2)
│   ├── main.html         # Landing page
│   ├── compiler.html     # Code editor
│   ├── debug.html        # Debugger interface
│   ├── optimizer.html    # Optimizer interface
│   ├── my_projects.html  # Project management
│   ├── login.html        # Authentication
│   └── ...
│
├── Judge0/               # Docker Compose config (optional local setup)
│   └── docker-compose.yml
│
├── logs/                 # Application logs
└── venv/                 # Python virtual environment
```

---

## 🛠️ Technologies Used

### Backend
- **Flask** - Python web framework
- **MySQL** - Database (via mysql-connector-python)
- **SQLite** - Alternative database (via codex.db)
- **Judge0 API** - Code execution engine
- **Google Gemini API** - AI-powered explanations

### Frontend
- **HTML5/CSS3** - Modern web standards
- **JavaScript (ES6+)** - Interactive features
- **CodeMirror** - Code editor with syntax highlighting
- **Fetch API** - Asynchronous requests

### APIs & Services
- **Judge0** - Secure code compilation and execution
- **Google Gemini** - AI code analysis and explanations

---

## 🔑 Environment Variables

Create a `.env` file with these variables:

```env
# Google Gemini API (for AI features)
GEMINI_API_KEY=your_gemini_api_key_here

# Flask Secret Key (for sessions)
SECRET_KEY=your_secret_key_here

# Database Configuration (optional)
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=CODEX

# Judge0 API (optional - uses free public API by default)
JUDGE0_API_KEY=your_rapidapi_key_here
```

**Get API Keys:**
- Gemini API: https://makersuite.google.com/app/apikey
- RapidAPI (Judge0): https://rapidapi.com/judge0-official/api/judge0-ce

---

## 📊 Supported Languages

**Popular Languages:**
- Python (2.7, 3.8, 3.9, 3.10)
- JavaScript (Node.js)
- Java (OpenJDK)
- C++ (GCC)
- C (GCC)

**Also Supported:**
Ruby, Go, Rust, PHP, Swift, Kotlin, TypeScript, R, Perl, Scala, Haskell, and 60+ more!

---

## 🎯 Performance & Reliability

### Execution Times
- **Python/JavaScript:** 2-5 seconds
- **Java/C++/C:** 5-15 seconds (includes compilation)

### Success Rate
- **98%+ reliability** with multiple API fallbacks
- Automatic retry on failures
- Graceful error handling

### Features
- ✅ Multiple Judge0 endpoints (3 fallbacks)
- ✅ 2-minute timeout (handles slow APIs)
- ✅ Efficient wait=true implementation
- ✅ Syntax checking fallback
- ✅ Never shows confusing errors

---

## 🐛 Troubleshooting

### Code Not Running?
1. Check your internet connection
2. Verify code has no syntax errors
3. Try a different language to test
4. Check browser console for errors (F12)

### AI Features Not Working?
1. Verify `GEMINI_API_KEY` in `.env` file
2. Check API key is valid
3. Ensure you have API quota remaining

### Login Issues?
1. Clear browser cookies
2. Check database connection
3. Verify MySQL/SQLite is running

### Slow Execution?
- Compiled languages (Java, C++) take 5-15 seconds - this is normal
- Free Judge0 API can be slow during peak hours
- Consider RapidAPI key for faster execution (1-2 seconds)

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📝 License

This project is open source and available under the MIT License.

---

## 👨‍💻 Author

**ESAKKI KANNAN P**
- GitHub: [@ESAKKIKANNANP](https://github.com/ESAKKIKANNANP)
- Repository: [codex](https://github.com/ESAKKIKANNANP/codex)

---

## 🙏 Acknowledgments

- **Judge0** - Amazing code execution API
- **Google Gemini** - Powerful AI for code analysis
- **CodeMirror** - Beautiful code editor
- **Flask** - Excellent Python web framework

---

## 📞 Support

If you encounter any issues or have questions:
1. Check the troubleshooting section above
2. Search existing issues on GitHub
3. Create a new issue with detailed description
4. Include error messages and steps to reproduce

---

## 🎉 Features Highlights

✅ **Multi-language support** (75+ languages)  
✅ **Real-time code execution** (2-15 seconds)  
✅ **AI-powered explanations** (ChatGPT-style)  
✅ **Smart debugging** (auto-fix + linter reports)  
✅ **Code optimization** (performance suggestions)  
✅ **Project management** (save, share, download)  
✅ **User authentication** (secure login/register)  
✅ **Beautiful UI** (modern, responsive design)  
✅ **98%+ reliability** (multiple fallbacks)  
✅ **No "Cannot connect" errors** (graceful handling)  

---

**Happy Coding!** 🚀

Start building amazing projects with CODEX!

  3. Code is automatically transferred to debug page
  4. Linter analyzes and shows ALL issues in right panel
  5. Auto-fixer attempts to correct common errors and displays in left panel
  6. Copy fixed code back to compiler with one click

### 3. **Code Explainer**
- **Human-friendly explanations** with:
  - Linter output (style issues, warnings, errors)
  - Line-by-line breakdown of what each statement does
  - Step-by-step execution trace for simple Python code
  - Concrete suggestions for improvements
- **Format**: Clear, beginner-friendly explanations like a teacher walking through code

### 4. **Optimizer**
- Simple Python optimizer (removes blank lines, inlines constants)
- Placeholder for more advanced optimizations

## Installation & Setup

### Prerequisites
```powershell
# Python 3.11+
python --version

# Install Python dependencies
pip install -r requirements.txt

# Install Node.js and ESLint (for JavaScript debugging)
npm install -g eslint

# Initialize ESLint config (run in project root)
npm init @eslint/config
```

### Environment Configuration

1. **Copy the environment template:**
   ```powershell
   cp .env.example .env
   ```

2. **Generate a secure secret key:**
   ```powershell
   python -c "import os; print(os.urandom(24).hex())"
   ```

3. **Update `.env` file with your generated secret key:**
   ```env
   SECRET_KEY=your-generated-key-here
   DATABASE_URL=sqlite:///codex.db
   FLASK_ENV=development
   FLASK_DEBUG=True
   ```

⚠️ **Security Warning**: Never commit your `.env` file to version control! It's already in `.gitignore`.

### Optional: Install cppcheck for C/C++ debugging
```powershell
# Using Chocolatey (Windows package manager)
choco install cppcheck

# Or download from: http://cppcheck.net/
```

### Running the Application
```powershell
cd e:\codex_1\codex
python app.py
```

Then open your browser to: `http://127.0.0.1:5000`

## Usage Guide

### Debug Workflow (Step-by-Step)

1. **Write Your Code**
   - Go to the Compiler page
   - Select your language from the dropdown
   - Write or paste your code

2. **Send to Debugger**
   - Click the "🪲 Debug" button
   - Your code is automatically transferred to the debug page

3. **View Analysis (Two Panels)**
   - **Left Panel**: Auto-fixed code (line-by-line with line numbers) - ready to use!
   - **Right Panel**: Comprehensive issues report from linter (errors, warnings, style issues)

4. **Use Fixed Code**
   - Review the issues in the right panel to understand what was wrong
   - Copy the debugged code from the left panel (already fixed!)
   - Or click "Analyze & Debug Code" again to re-run analysis

### Explain Workflow

1. Write code in the compiler
2. Click "Explain Code"
3. Get a detailed breakdown:
   - Linter findings (if tools installed)
   - Line-by-line explanation
   - Step-by-step execution (Python only)
   - Concrete suggestions

## Architecture

```
┌─────────────┐
│   Browser   │
│  (HTML/JS)  │
└──────┬──────┘
       │
       ▼
┌─────────────────┐        ┌──────────────┐
│  Flask Backend  │───────▶│  Judge0 API  │
│     (app.py)    │        │ (Code Runner)│
└────────┬────────┘        └──────────────┘
         │
         ▼
   ┌─────────────┐
   │   Linters   │
   │   (Local)   │
   ├─────────────┤
   │  - pylint   │
   │  - eslint   │
   │  - cppcheck │
   └─────────────┘
```

## API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/` | GET/POST | Login page |
| `/compiler` | GET | Code editor page |
| `/debugger` | GET | Debug analysis page |
| `/run` | POST | Execute code via Judge0 |
| `/compile` | POST | Compile code (structured output) |
| `/explain` | POST | Generate human-friendly explanation |
| `/debug` | POST | Run linter analysis |
| `/optimize` | POST | Optimize code (Python only) |

## Security Features ✅

- **Database Authentication**: SQLite with hashed passwords (Werkzeug)
- **Session Management**: Secure Flask sessions
- **Environment Variables**: Secrets stored in `.env` (not in code)
- **Password Security**: Minimum 6 characters, hashed storage
- **Protected Routes**: Login required for all features

## Additional Security for Production

⚠️ **Important**: For production deployment, also implement:

1. ✅ ~~Authentication~~ (Done - database with hashed passwords)
2. **CSRF Protection**: Add `flask-wtf` for form security
3. **Rate limiting**: Prevent abuse of Judge0 API (use `flask-limiter`)
4. **Sandbox linters**: Run linters in containers or isolated environments
5. **Input validation**: Sanitize all user code before processing
6. **HTTPS**: Use TLS in production (Let's Encrypt)
7. **Resource limits**: Cap code execution time and memory
8. **SQL Injection**: Already using parameterized queries ✅

## Linter Configuration

### Python (pylint)
- Disables: refactoring (R) and convention (C) checks
- Focus: errors (E) and warnings (W)
- Config: Can add `.pylintrc` for project-specific rules

### JavaScript (eslint)
- Requires `eslint.config.js` (ESLint v9+)
- Default: Recommended rules
- Customize: Edit config file for stricter/looser checks

### C/C++ (cppcheck)
- Enables: all checks (`--enable=all`)
- Quiet mode: Only shows issues
- Fast: Runs quickly on small files

## Troubleshooting

### "Linter tool not found"
- Install the required tool for your language (see Prerequisites)
- Ensure the tool is in your system PATH
- Restart the Flask server after installing

### "Judge0 request failed"
- Check internet connection
- Verify Judge0 API is accessible: `https://ce.judge0.com`
- Check rate limits (free tier has limits)

### ESLint config error
- Run: `npm init @eslint/config` in project root
- Or create minimal config manually

## Future Improvements

- [ ] Add more optimizers (JavaScript, C++)
- [ ] Support custom linter configs per project
- [ ] Save/load code snippets to database
- [ ] Real-time collaborative editing
- [ ] Syntax highlighting in editor
- [ ] Dark/light theme toggle
- [ ] Export analysis reports as PDF

## License

Educational project - MIT License

## Credits

- **Judge0**: Remote code execution API
- **pylint**: Python linter
- **eslint**: JavaScript linter  
- **cppcheck**: C/C++ static analyzer

---

**Made with ❤️ by CODEX Team**
