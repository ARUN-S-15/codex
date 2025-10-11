# Installing cppcheck on Windows

## Problem
You installed cppcheck but it's not accessible from the command line, causing the error:
```
⚠️ Linter not installed for c. Please install the required tool.
```

## Solution
The application now includes:
1. **Automatic search** for cppcheck in common installation paths
2. **Helpful error messages** with installation instructions
3. **Auto-fix still works** even if cppcheck isn't found

## How to Properly Install cppcheck on Windows

### Option 1: Using winget (Recommended)
```powershell
winget install cppcheck
```
Then restart PowerShell to refresh PATH.

### Option 2: Manual Installation
1. **Download cppcheck:**
   - Go to: https://github.com/danmar/cppcheck/releases
   - Download the latest Windows installer (e.g., `cppcheck-2.xx-x64-Setup.msi`)

2. **Install:**
   - Run the installer
   - During installation, **CHECK** the option "Add to PATH"
   - Default location: `C:\Program Files\Cppcheck\`

3. **Add to PATH manually** (if installer didn't):
   - Press `Win + X`, select "System"
   - Click "Advanced system settings"
   - Click "Environment Variables"
   - Under "System variables", find "Path"
   - Click "Edit" → "New"
   - Add: `C:\Program Files\Cppcheck`
   - Click "OK" on all dialogs

4. **Verify installation:**
   ```powershell
   cppcheck --version
   ```
   Should output something like: `Cppcheck 2.xx`

### Option 3: Using Chocolatey
```powershell
choco install cppcheck
```

## What Changed in the Code

### Before:
```python
elif language in ["c", "cpp"]:
    cmd = ["cppcheck", "--enable=all", "--quiet", tmpfile]
```
❌ Only looked for `cppcheck` in PATH

### After:
```python
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
```
✅ Checks multiple locations AND provides helpful instructions

## Current Behavior

### When cppcheck is NOT installed:
- ✅ Shows helpful installation instructions in Issues box
- ✅ Still auto-fixes your C/C++ code
- ✅ Provides working fixed code in left panel

### When cppcheck IS installed:
- ✅ Runs full static analysis
- ✅ Shows actual code issues (memory leaks, uninitialized variables, etc.)
- ✅ Auto-fixes common syntax errors

## Testing
Run the test to verify behavior:
```powershell
python test_cppcheck_fallback.py
```

Expected output:
- Shows friendly error message about cppcheck
- Provides installation instructions
- Still auto-fixes the code (adds `()`, `;`, `{}`)

## Files Modified
- `app.py` (lines ~750-780): Added cppcheck path detection and helpful error messages
- `test_cppcheck_fallback.py`: Created test to verify graceful fallback

## Next Steps
1. **Install cppcheck** using one of the methods above
2. **Restart PowerShell** to refresh PATH
3. **Verify:** Run `cppcheck --version`
4. **Test in app:** Debug your C code - should now show cppcheck analysis!
