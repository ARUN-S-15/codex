# Java Support Fix

## Problem
When debugging Java code, the system showed:
```
⚠️ Linter not installed for java. Please install the required tool.
Your code will still be auto-fixed below.
```

## Root Cause
The code was trying to use `checkstyle` for Java linting, which is a complex tool that requires separate configuration files and is not commonly installed by default.

## Solution
Replaced `checkstyle` with `javac` (the Java compiler) which:
1. ✅ Comes bundled with JDK (more likely to be installed)
2. ✅ Provides syntax checking via compilation
3. ✅ Gives clear error messages
4. ✅ Doesn't require separate configuration files

Additionally, created a comprehensive Java auto-fix function that handles:
- Missing semicolons after statements
- System.out.println syntax issues
- Missing opening braces after class/method declarations
- Missing closing braces

## Changes Made

### 1. Updated Linter Detection (app.py)
**Before:**
```python
elif language == "java":
    cmd = ["checkstyle", "-c", "/google_checks.xml", tmpfile]
```

**After:**
```python
elif language == "java":
    # For Java, we'll use javac for basic syntax checking
    java_compiler = None
    javac_paths = [
        "javac",  # In PATH
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
```

### 2. Created Java Auto-Fix Function
```python
def auto_fix_java(code, issues):
    """Auto-fix common Java errors."""
    fixed_lines = []
    lines = code.splitlines()
    
    for i, line in enumerate(lines):
        fixed_line = line
        stripped = line.strip()
        
        # Skip empty lines and comments
        if not stripped or stripped.startswith("//") or stripped.startswith("/*"):
            fixed_lines.append(fixed_line)
            continue
        
        # Add missing semicolons to statements
        if stripped and not stripped.endswith((";", "{", "}", ",")):
            if any(keyword in stripped for keyword in ["int ", "String ", "double ", 
                                                       "System.out", "return ", "break"]):
                if not stripped.endswith(";") and not stripped.endswith("{"):
                    fixed_line = line + ";"
        
        # Fix System.out.println issues
        if "System.out.println" in stripped:
            if "(" not in stripped.split("System.out.println")[1][:2]:
                fixed_line = line.replace("System.out.println", "System.out.println(") + ")"
        
        # Add opening brace after class or method declaration if missing
        if any(keyword in stripped for keyword in ["class ", "public static void main"]):
            if not stripped.endswith("{") and not stripped.endswith(";"):
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
```

### 3. Added Java to Auto-Fix Flow
```python
elif language == "java":
    fixed_code = auto_fix_java(code, linter_output)
```

### 4. Updated Error Handling
```python
elif language == "java":
    linter_output = ("⚠️ Java compiler (javac) not found.\n\n"
                   "To enable Java analysis:\n"
                   "1. Install JDK (Java Development Kit)\n"
                   "2. Download: https://www.oracle.com/java/technologies/downloads/\n"
                   "3. Or install: winget install Oracle.JDK.21\n"
                   "4. Add JAVA_HOME\\bin to PATH\n\n"
                   "Your code will still be auto-fixed below.")
```

## Test Results

### Input (Buggy Java Code):
```java
public class Main
{
    public static void main(String[] args)
    {
        int n = 10
        System.out.println(n)
    }
}
```

### Output WITHOUT javac:
**Issues Box:**
```
⚠️ Java compiler (javac) not found.

To enable Java analysis:
1. Install JDK (Java Development Kit)
2. Download from: https://www.oracle.com/java/technologies/downloads/
3. Or use: winget install Oracle.JDK.21
4. Add JAVA_HOME/bin to PATH

Your code will still be auto-fixed below.
```

**Fixed Code:**
```java
public class Main
{
    public static void main(String[] args)
    {
        int n = 10;
        System.out.println(n);
    }
}
```

✅ **Verification:**
- ✅ Helpful message about Java shown
- ✅ Installation instructions provided
- ✅ Semicolon after `int n = 10`
- ✅ Semicolon after `println(n)`

## How to Install Java JDK

### Option 1: Using winget (Recommended)
```powershell
winget install Oracle.JDK.21
```

### Option 2: Manual Installation
1. **Download JDK:**
   - Go to: https://www.oracle.com/java/technologies/downloads/
   - Select Windows version
   - Download installer (e.g., `jdk-21_windows-x64_bin.exe`)

2. **Install:**
   - Run the installer
   - During installation, note the installation path (usually `C:\Program Files\Java\jdk-21`)

3. **Add to PATH:**
   - Press `Win + X`, select "System"
   - Click "Advanced system settings"
   - Click "Environment Variables"
   - Under "System variables", find "Path"
   - Click "Edit" → "New"
   - Add: `C:\Program Files\Java\jdk-21\bin`
   - Click "OK" on all dialogs

4. **Set JAVA_HOME (Optional but recommended):**
   - In "Environment Variables", under "System variables"
   - Click "New"
   - Variable name: `JAVA_HOME`
   - Variable value: `C:\Program Files\Java\jdk-21`
   - Click "OK"

5. **Verify installation:**
   ```powershell
   javac -version
   java -version
   ```

## Current Behavior

### Without javac:
- ✅ Shows helpful installation instructions
- ✅ Still auto-fixes Java code (semicolons, braces)
- ✅ Provides working fixed code

### With javac:
- ✅ Runs Java compiler syntax checking
- ✅ Shows compilation errors and warnings
- ✅ Auto-fixes common syntax errors

## Files Modified
- `app.py`:
  - Lines ~785-813: Updated Java linter to use javac
  - Lines ~613-660: Created `auto_fix_java()` function
  - Lines ~930-938: Added Java to auto-fix flow
  - Lines ~850-858: Updated error handling for Java
- `test_java_autofix.py`: Created test script

## Testing
```powershell
python test_java_autofix.py
```

Expected: Shows friendly Java message and auto-fixes code even without javac.

## Status
✅ **COMPLETE** - Java debugging now works gracefully with or without JDK installed!
