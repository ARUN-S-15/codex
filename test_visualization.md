# Testing the Visualization Feature

## Test Cases

### Test 1: Simple Variable Assignment
```python
x = 5
y = 10
z = x + y
print(z)
```

**Expected Output:**
- Step 1: Line 1, x = 5, variables: {x: {value: 5, type: "int", changed: true}}
- Step 2: Line 2, y = 10, variables: {x: {value: 5, type: "int", changed: false}, y: {value: 10, type: "int", changed: true}}
- Step 3: Line 3, z = x + y, variables: {x: 5, y: 10, z: {value: 15, type: "int", changed: true}}
- Step 4: Line 4, print(z), output: "15"

---

### Test 2: Loop Execution
```python
for i in range(3):
    print(i)
```

**Expected Output:**
- Multiple steps showing i changing from 0 to 2
- Print statements showing 0, 1, 2

---

### Test 3: Function Call
```python
def add(a, b):
    return a + b

result = add(3, 5)
print(result)
```

**Expected Output:**
- Call stack showing: main() -> add(a, b)
- Variables showing a=3, b=5 inside function
- Return value captured in result
- Final print showing 8

---

## Potential Issues to Check

### Issue 1: JSON Parsing
**Problem:** Gemini might return markdown-wrapped JSON
**Solution:** Already implemented - removes ```json markers

### Issue 2: onclick not working
**Problem:** Dynamic HTML with onclick might need event delegation
**Solution:** Test if buttons work, if not, use addEventListener

### Issue 3: Variable display for complex types
**Problem:** Objects/arrays might not display nicely
**Solution:** Use JSON.stringify with proper formatting

---

## Manual Testing Steps

1. Start server: `python app.py`
2. Navigate to: http://127.0.0.1:5000
3. Login with test account
4. Go to compiler page
5. Paste test code
6. Click "🎬 Visualize" button
7. Check:
   - Loading spinner appears
   - API call succeeds
   - Steps display correctly
   - Previous/Next buttons work
   - Variables show correct values
   - Variable changes are highlighted green

---

## Debug Checklist

If visualization doesn't work:

- [ ] Check browser console for JavaScript errors
- [ ] Check Flask terminal for backend errors
- [ ] Verify Gemini API key is set in .env
- [ ] Check if user is logged in
- [ ] Verify API endpoint returns valid JSON
- [ ] Check if buttons are created correctly
- [ ] Test stepForward/stepBackward functions manually in console

---

## Browser Console Test

Open browser console and try:
```javascript
// Check if functions exist
console.log(typeof window.stepForward);  // Should be "function"
console.log(typeof window.stepBackward); // Should be "function"

// Check current state
console.log(currentStep);  // Should be a number
console.log(visualizationData);  // Should be an object or null
```

---

## API Test with curl

Test backend directly:
```bash
curl -X POST http://127.0.0.1:5000/api/visualize \
  -H "Content-Type: application/json" \
  -d '{"code": "x = 5\nprint(x)", "language": "python"}'
```

Expected response: JSON with steps array

---

## Known Limitations

1. Works best with simple algorithms
2. Complex code might produce too many steps
3. Gemini might occasionally return invalid JSON
4. Some languages might not trace as well as Python

---

## If It Doesn't Work - Quick Fixes

### Fix 1: Replace onclick with event listeners
In `displayVisualization()`, after setting innerHTML, add:
```javascript
document.querySelectorAll('button[onclick]').forEach(btn => {
  const onclick = btn.getAttribute('onclick');
  btn.removeAttribute('onclick');
  btn.addEventListener('click', () => {
    eval(onclick);
  });
});
```

### Fix 2: Simplify AI prompt
If Gemini returns invalid JSON, make prompt more strict:
- Add "CRITICAL: Respond with ONLY valid JSON, no explanation"
- Add example JSON output
- Reduce complexity of requested data

### Fix 3: Add fallback visualization
If AI fails, create simple line-by-line display without variable tracking
