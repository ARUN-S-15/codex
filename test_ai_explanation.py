"""Test the new AI explanation generation"""

def analyze_code_purpose(code, language):
    """Analyze what the code does and provide high-level overview"""
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
    
    # Build overview
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
    overview.append("📊 **Code Statistics:**")
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
        if "=" in stripped and not any(op in stripped for op in ["==", "!=", "<=", ">=", "+=", "-=", "*=", "/="]):
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


# Test it
test_code = """
n = int(input("enter number: "))
for i in range(n, 0, -1):
    for j in range(i):
        print("* ", end="")
    print()
"""

print("=" * 80)
print("AI EXPLANATION TEST")
print("=" * 80)
print()

overview = analyze_code_purpose(test_code, "python")
for line in overview:
    print(line)

print()
print("=" * 80)
print("LINE-BY-LINE BREAKDOWN:")
print("=" * 80)
print()

for i, line in enumerate(test_code.splitlines(), start=1):
    stripped = line.strip()
    if not stripped or stripped.startswith("#"):
        continue
    
    print(f"Line {i}: {line}")
    print("-" * 80)
    explanation = generate_detailed_line_explanation(line, stripped, i, "python")
    print(explanation)
    print()
    print()
