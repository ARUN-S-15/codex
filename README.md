# CODEX - Online Code Compiler, Debugger & Optimizer

A web-based code development environment that lets you compile, debug, and optimize code in multiple languages.

## Features

### 1. **Compiler**
- Write and run code in Python, C, C++, JavaScript, and Java
- Uses Judge0 API for safe code execution
- Real-time syntax highlighting and line numbers
- Copy code functionality

### 2. **Debugger** ✨
- **Comprehensive error detection** using industry-standard linters:
  - **Python**: pylint (detects syntax errors, style issues, warnings)
  - **JavaScript**: eslint (checks syntax, best practices)
  - **C/C++**: cppcheck (finds bugs, performance issues)
  - **Java**: checkstyle (style and error checking)
  
- **Auto-fix capabilities** for common errors:
  - **Python**: Missing colons, print statements, indentation, assignment in conditionals
  - **JavaScript**: Missing semicolons, console.log syntax, var → let/const conversion
  - **C/C++**: Missing semicolons, printf/scanf syntax
  
- **Two-panel workflow**:
  1. **Left panel**: Auto-fixed code (line-by-line) with line numbers - ready to copy and use
  2. **Right panel**: Issues found by linter (errors, warnings, style issues) - comprehensive report
  
- **Smart workflow**:
  1. Write code in the compiler
  2. Click the "🪲 Debug" button
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
pip install flask requests pylint

# Install Node.js and ESLint (for JavaScript debugging)
npm install -g eslint

# Initialize ESLint config (run in project root)
npm init @eslint/config
```

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

## Security Notes

⚠️ **Important**: This is a development/learning tool. For production:

1. **Add authentication**: Current login is hardcoded (`admin`/`123`)
2. **Sandbox linters**: Run linters in containers or isolated environments
3. **Rate limiting**: Prevent abuse of Judge0 API
4. **Input validation**: Sanitize all user code before processing
5. **HTTPS**: Use TLS in production
6. **Resource limits**: Cap code execution time and memory

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
