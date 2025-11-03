// ==================== TOAST NOTIFICATION SYSTEM ====================
const Toast = {
  container: null,
  
  init() {
    this.container = document.getElementById('toastContainer');
    if (!this.container) {
      this.container = document.createElement('div');
      this.container.id = 'toastContainer';
      this.container.className = 'toast-container';
      document.body.appendChild(this.container);
    }
  },
  
  show(message, type = 'info', duration = 3000) {
    if (!this.container) this.init();
    
    const icons = {
      success: '✅',
      error: '❌',
      warning: '⚠️',
      info: 'ℹ️'
    };
    
    const titles = {
      success: 'Success',
      error: 'Error',
      warning: 'Warning',
      info: 'Info'
    };
    
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `
      <div class="toast-icon">${icons[type] || icons.info}</div>
      <div class="toast-content">
        <div class="toast-title">${titles[type] || titles.info}</div>
        <div class="toast-message">${message}</div>
      </div>
      <button class="toast-close" onclick="this.parentElement.remove()">×</button>
      <div class="toast-progress"></div>
    `;
    
    this.container.appendChild(toast);
    
    // Trigger animation
    requestAnimationFrame(() => {
      toast.classList.add('show');
    });
    
    // Auto remove
    setTimeout(() => {
      toast.classList.add('hide');
      setTimeout(() => toast.remove(), 300);
    }, duration);
    
    // Click to dismiss
    toast.addEventListener('click', (e) => {
      if (!e.target.classList.contains('toast-close')) {
        toast.classList.add('hide');
        setTimeout(() => toast.remove(), 300);
      }
    });
    
    return toast;
  },
  
  success(message, duration) {
    return this.show(message, 'success', duration);
  },
  
  error(message, duration) {
    return this.show(message, 'error', duration);
  },
  
  warning(message, duration) {
    return this.show(message, 'warning', duration);
  },
  
  info(message, duration) {
    return this.show(message, 'info', duration);
  }
};

// Make Toast available globally
window.Toast = Toast;
console.log("✅ Toast notification system loaded!");

// ==================== MAIN APP ====================
document.addEventListener("DOMContentLoaded", () => {
  console.log("🚀 Compiler.js loaded successfully!");
  
  // Initialize toast system
  Toast.init();
  
  // ============================================
  // CODEMIRROR INITIALIZATION (Single Unified Editor)
  // ============================================
  const codeEditorTextarea = document.getElementById("codeEditor");
  
  // Language mode mapping for CodeMirror
  const languageModeMap = {
    "71": "python",        // Python
    "63": "javascript",    // JavaScript (Node.js)
    "62": "text/x-java",   // Java
    "54": "text/x-c++src", // C++
    "50": "text/x-csrc",   // C
    "51": "text/x-csharp", // C#
    "60": "text/x-go"      // Go
  };
  
  // Initialize CodeMirror
  const codeMirrorEditor = CodeMirror.fromTextArea(codeEditorTextarea, {
    mode: "python",  // Default to Python
    theme: "monokai",
    lineNumbers: true,
    autofocus: true,
    indentUnit: 4,
    tabSize: 4,
    lineWrapping: true,
    autoCloseBrackets: true,
    matchBrackets: true,
    styleActiveLine: true,
    extraKeys: {
      // Basic editing
      "Tab": (cm) => cm.execCommand("indentMore"),
      "Shift-Tab": (cm) => cm.execCommand("indentLess"),
      
      // IDE Shortcuts
      "F9": (cm) => { 
        if (runBtn) { 
          runBtn.click(); 
          return false; 
        } 
      },
      "F8": (cm) => { 
        if (debugBtn) { 
          debugBtn.click(); 
          return false; 
        } 
      },
      "Ctrl-S": (cm) => { 
        if (saveBtn) { 
          saveBtn.click(); 
        }
        return false; 
      },
      "Ctrl-M": (cm) => { 
        if (newCodeBtn) { 
          newCodeBtn.click(); 
          return false; 
        } 
      },
      
      // Copy/Duplicate line up
      "Alt-Shift-Up": (cm) => {
        const cursor = cm.getCursor();
        const line = cm.getLine(cursor.line);
        cm.replaceRange(line + "\n", {line: cursor.line, ch: 0});
        cm.setCursor({line: cursor.line, ch: cursor.ch});
      },
      
      // Copy/Duplicate line down
      "Alt-Shift-Down": (cm) => {
        const cursor = cm.getCursor();
        const line = cm.getLine(cursor.line);
        cm.replaceRange("\n" + line, {line: cursor.line, ch: line.length});
        cm.setCursor({line: cursor.line + 1, ch: cursor.ch});
      },
      
      // Move line up
      "Alt-Up": (cm) => {
        const cursor = cm.getCursor();
        if (cursor.line === 0) return;
        const line = cm.getLine(cursor.line);
        const prevLine = cm.getLine(cursor.line - 1);
        cm.replaceRange(line + "\n" + prevLine, {line: cursor.line - 1, ch: 0}, {line: cursor.line + 1, ch: 0});
        cm.setCursor({line: cursor.line - 1, ch: cursor.ch});
      },
      
      // Move line down
      "Alt-Down": (cm) => {
        const cursor = cm.getCursor();
        if (cursor.line === cm.lineCount() - 1) return;
        const line = cm.getLine(cursor.line);
        const nextLine = cm.getLine(cursor.line + 1);
        cm.replaceRange(nextLine + "\n" + line, {line: cursor.line, ch: 0}, {line: cursor.line + 2, ch: 0});
        cm.setCursor({line: cursor.line + 1, ch: cursor.ch});
      },
      
      // Comment toggle
      "Ctrl-/": (cm) => {
        cm.toggleComment();
      },
      
      // Delete line
      "Ctrl-D": (cm) => {
        const cursor = cm.getCursor();
        cm.replaceRange("", {line: cursor.line, ch: 0}, {line: cursor.line + 1, ch: 0});
      },
      
      // Duplicate selection/line
      "Ctrl-Shift-D": (cm) => {
        if (cm.somethingSelected()) {
          const selections = cm.getSelections();
          cm.replaceSelections(selections.concat(selections));
        } else {
          const cursor = cm.getCursor();
          const line = cm.getLine(cursor.line);
          cm.replaceRange("\n" + line, {line: cursor.line, ch: line.length});
          cm.setCursor({line: cursor.line + 1, ch: cursor.ch});
        }
      },
      
      // Find and replace
      "Ctrl-F": "find",
      "Ctrl-H": "replace",
      "Ctrl-G": "findNext",
      "Ctrl-Shift-G": "findPrev",
      
      // Go to line
      "Ctrl-L": (cm) => {
        const line = prompt("Go to line:", "");
        if (line) {
          cm.setCursor(parseInt(line) - 1, 0);
        }
      },
      
      // Select all
      "Ctrl-A": "selectAll",
      
      // Undo/Redo
      "Ctrl-Z": "undo",
      "Ctrl-Y": "redo",
      "Ctrl-Shift-Z": "redo",
      
      // Upper/Lower case
      "Ctrl-U": (cm) => {
        const selections = cm.getSelections();
        cm.replaceSelections(selections.map(s => s.toUpperCase()));
      },
      "Ctrl-Shift-U": (cm) => {
        const selections = cm.getSelections();
        cm.replaceSelections(selections.map(s => s.toLowerCase()));
      }
    }
  });
  
  // Function to get comment character based on language
  function getCommentChar(mode) {
    if (mode.includes("python")) return "#";
    if (mode.includes("javascript") || mode.includes("java") || mode.includes("c")) return "//";
    return "#";
  }
  
  // Create a wrapper for CodeMirror to maintain compatibility with old code
  const codeEditor = {
    get value() {
      return codeMirrorEditor.getValue();
    },
    set value(text) {
      codeMirrorEditor.setValue(text);
    },
    focus() {
      codeMirrorEditor.focus();
    }
  };
  
  console.log("✅ CodeMirror initialized successfully!");
  
  // ============================================
  // UI ELEMENTS
  // ============================================
  const runBtn = document.getElementById("runBtn");
  const explainBtn = document.getElementById("explainBtn");
  const debugBtn = document.getElementById("debugBtn");
  const saveBtn = document.getElementById("saveBtn");
  const shareBtn = document.getElementById("shareBtn");
  const newCodeBtn = document.getElementById("newCodeBtn");
  const languageSelect = document.getElementById("languageSelect");
  
  console.log("✅ Elements found:", {
    runBtn: !!runBtn,
    codeEditor: !!codeEditor,
    languageSelect: !!languageSelect,
    saveBtn: !!saveBtn,
    shareBtn: !!shareBtn,
    newCodeBtn: !!newCodeBtn
  });

  const resultBox = document.getElementById("resultBox");
  const explanationBox = document.getElementById("explanationBox");

  const resultSection = document.getElementById("resultSection");
  const explanationSection = document.getElementById("explanationSection");

  const debugSection = document.getElementById("debugSection"); // might not exist
  const debugBox = document.getElementById("debugOutput"); // might not exist

  // ---- BOTTOM SHEET HELPERS ----
  // Function to close/hide the output section (minimize it to show header only)
  const closeOutput = () => {
    if (resultSection) {
      resultSection.classList.remove("show");
      resultSection.classList.remove("hidden");
      resultSection.classList.add("minimized");
    }
  };
  
  // Function to open/show the output section
  const openOutput = () => {
    if (resultSection) {
      resultSection.classList.remove("hidden");
      resultSection.classList.remove("minimized");
      setTimeout(() => {
        resultSection.classList.add("show");
        // Scroll to output section smoothly
        resultSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
      }, 10);
    }
  };
  
  // Setup output section close button
  const closeOutputBtn = document.getElementById("closeOutputBtn");
  const outputHeader = document.querySelector(".output-header");
  
  if (closeOutputBtn) {
    closeOutputBtn.addEventListener("click", (e) => {
      e.stopPropagation();
      closeOutput();
    });
  }
  
  // Click header to toggle expand/collapse
  if (outputHeader) {
    outputHeader.addEventListener("click", () => {
      if (resultSection) {
        if (resultSection.classList.contains("show")) {
          closeOutput(); // Collapse to minimized state
        } else if (resultSection.classList.contains("minimized")) {
          openOutput(); // Expand from minimized state
        }
      }
    });
  }

  // ---- OLD TAB CODE (DISABLED - NO LONGER USED) ----
  // Tabs functionality removed per user request

  // ---- LOAD SHARED CODE FROM SESSION STORAGE ----
  const sharedCode = sessionStorage.getItem('sharedCode');
  const sharedLanguage = sessionStorage.getItem('sharedLanguage');
  const sharedTitle = sessionStorage.getItem('sharedTitle');
  
  if (sharedCode) {
    codeMirrorEditor.setValue(sharedCode);
    // Clear session storage after loading
    sessionStorage.removeItem('sharedCode');
    sessionStorage.removeItem('sharedLanguage');
    sessionStorage.removeItem('sharedTitle');
    
    alert(`✅ Loaded shared code: "${sharedTitle}"`);
  }

  // ---- NEW CODE BUTTON ----
  if (newCodeBtn) {
    newCodeBtn.addEventListener('click', () => {
      const currentCode = codeMirrorEditor.getValue().trim();
      
      // If there's code, ask for confirmation
      if (currentCode && !confirm("Clear current code? (Unsaved changes will be lost)")) {
        return;
      }
      
      // Clear the editor
      codeMirrorEditor.setValue("");
      
      // Fully hide result sections (not just minimize)
      if (resultSection) {
        resultSection.classList.remove("show", "minimized");
        resultSection.classList.add("hidden");
      }
      if (explanationSection) {
        explanationSection.classList.remove("show", "minimized");
        explanationSection.classList.add("hidden");
      }
      if (debugSection) debugSection.classList.add("hidden");
    });
  }

  // ---- SAVE & SHARE ----
  if (saveBtn) {
    saveBtn.addEventListener('click', async () => {
      // Check if user is logged in
      if (!window.USER_LOGGED_IN) {
        Toast.warning("Please login to save your code. Create a free account to save and manage your projects.");
        setTimeout(() => { window.location.href = "/login"; }, 1500);
        return;
      }
      
      const code = codeEditor.value.trim();
      const languageText = languageSelect.options[languageSelect.selectedIndex].text;
      
      if (!code) {
        Toast.warning("Please write some code before saving!");
        return;
      }
      
      // Prompt user for a title
      const title = prompt("Enter a title for your code:", "My Code");
      
      // If user cancels (title is null), abort the save operation
      if (title === null) {
        console.log("Save operation cancelled by user");
        return;
      }
      
      // Use "Untitled" only if user clicks OK with empty string
      const finalTitle = title.trim() || "Untitled";
      
      try {
        const response = await fetch('/api/save', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ code, language: languageText, title: finalTitle })
        });
        
        const data = await response.json();
        if (data.success) {
          Toast.success(data.message + " - View your saved projects in 📁 My Code");
        } else {
          Toast.error(data.error || "Failed to save");
        }
      } catch (err) {
        Toast.error("Error: " + err.message);
      }
    });
  }

  if (shareBtn) {
    shareBtn.addEventListener('click', async () => {
      // Check if user is logged in
      if (!window.USER_LOGGED_IN) {
        Toast.warning("Please login to share your code. Create a free account to share your projects with others.");
        setTimeout(() => { window.location.href = "/login"; }, 1500);
        return;
      }
      
      const code = codeEditor.value.trim();
      const languageText = languageSelect.options[languageSelect.selectedIndex].text;
      
      if (!code) {
        Toast.warning("Please write some code before sharing!");
        return;
      }
      
      // Prompt user for a title
      const title = prompt("Enter a title for sharing:", "Shared Code");
      
      // If user cancels (title is null), abort the share operation
      if (title === null) {
        console.log("Share operation cancelled by user");
        return;
      }
      
      // Use "Untitled" only if user clicks OK with empty string
      const finalTitle = title.trim() || "Untitled";
      
      try {
        const response = await fetch('/api/share', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ code, language: languageText, title: finalTitle })
        });
        
        const data = await response.json();
        if (data.success) {
          // Copy link to clipboard
          navigator.clipboard.writeText(data.share_link);
          Toast.success(data.message + " - Link copied to clipboard!");
        } else {
          Toast.error(data.error || "Failed to create share link");
        }
      } catch (err) {
        Toast.error("Error: " + err.message);
      }
    });
  }

  // ---- RUN CODE ---- (Terminal-style with inline input)
  if (runBtn && resultSection) {
    console.log("Run button listener attached successfully");
    
    const terminalOutput = document.getElementById("terminalOutput");
    const terminalInputLine = document.getElementById("terminalInputLine");
    const terminalInput = document.getElementById("terminalInput");
    const inputPrompt = document.getElementById("inputPrompt");
    
    let userInputs = []; // Store all user inputs
    let inputCount = 0; // Track how many inputs have been provided
    let isWaitingForInput = false;
    let inputPrompts = []; // Store extracted prompts from code
    
    runBtn.addEventListener("click", async () => {
      console.log("Run button clicked!");
      const code = codeEditor.value.trim();
      const language_id = parseInt(languageSelect.value);
      
      // Reset for new run
      userInputs = [];
      inputCount = 0;
      isWaitingForInput = false;
      inputPrompts = [];
      
      openOutput(); // Show output section with slide-up animation
      terminalInputLine.style.display = "none";

      if (!code) {
        terminalOutput.textContent = "⚠️ Please write some code before running!";
        return;
      }

      // Show loading state
      const originalText = runBtn.innerHTML;
      runBtn.disabled = true;
      runBtn.innerHTML = "⏳ Running...";

      try {
        // Check if code needs input
        const needsInput = detectInputRequired(code, language_id);
        
        if (needsInput) {
          // Extract prompts from code
          extractInputPrompts(code, language_id);
          
          // Start with first input prompt
          terminalOutput.textContent = "";
          const firstPrompt = inputPrompts[0] || "Enter input: ";
          showInputPrompt(firstPrompt);
          // Re-enable button for input mode
          runBtn.disabled = false;
          runBtn.innerHTML = originalText;
        } else {
          // Run normally without input
          terminalOutput.textContent = "⏳ Running your code...";
          await runCodeWithInputs(code, language_id, "");
        }
      } finally {
        // Re-enable button after execution
        runBtn.disabled = false;
        runBtn.innerHTML = originalText;
      }
    });
    
    // Extract input prompts from code
    function extractInputPrompts(code, language_id) {
      inputPrompts = [];
      
      if (language_id === 71) { // Python
        // Match input("prompt") patterns
        const matches = code.matchAll(/input\s*\(\s*["']([^"']+)["']\s*\)/g);
        for (const match of matches) {
          inputPrompts.push(match[1]);
        }
      } else if (language_id === 50 || language_id === 54) { // C or C++
        // Extract prompts from printf before scanf/cin
        // Match printf("prompt"); followed by scanf/cin
        const lines = code.split('\n');
        for (let i = 0; i < lines.length; i++) {
          const line = lines[i].trim();
          // Check if this line has scanf or cin (input operation)
          if (line.includes('scanf') || line.includes('cin >>')) {
            // Look backwards for the most recent printf
            for (let j = i - 1; j >= 0; j--) {
              const prevLine = lines[j].trim();
              const printfMatch = prevLine.match(/printf\s*\(\s*"([^"]+)"\s*\)/);
              if (printfMatch) {
                inputPrompts.push(printfMatch[1]);
                break;
              }
              // Stop if we hit another input statement or function boundary
              if (prevLine.includes('scanf') || prevLine.includes('cin >>') || prevLine.includes('{')) {
                break;
              }
            }
          }
        }
      } else if (language_id === 62) { // Java
        // Match Scanner.nextLine() with System.out.print before it
        const lines = code.split('\n');
        for (let i = 0; i < lines.length; i++) {
          const line = lines[i].trim();
          if (line.includes('.next')) {
            for (let j = i - 1; j >= 0; j--) {
              const prevLine = lines[j].trim();
              const printMatch = prevLine.match(/System\.out\.print(?:ln)?\s*\(\s*"([^"]+)"\s*\)/);
              if (printMatch) {
                inputPrompts.push(printMatch[1]);
                break;
              }
              if (prevLine.includes('.next') || prevLine.includes('{')) {
                break;
              }
            }
          }
        }
      }
      
      // Default prompts if none extracted
      if (inputPrompts.length === 0) {
        const inputCount = countExpectedInputs(code, language_id);
        for (let i = 0; i < inputCount; i++) {
          inputPrompts.push("Enter input: ");
        }
      }
    }
    
    // Handle Enter key in terminal input
    if (terminalInput) {
      terminalInput.addEventListener("keypress", async (event) => {
        if (event.key === "Enter" && isWaitingForInput) {
          const value = terminalInput.value;
          
          // Display what user typed (echo) on the same line as the prompt
          const currentText = terminalOutput.textContent;
          // Remove trailing space if present, add input value
          if (currentText.endsWith(" ")) {
            terminalOutput.textContent = currentText + value;
          } else {
            terminalOutput.textContent = currentText + value;
          }
          
          // Store the input
          userInputs.push(value);
          inputCount++;
          
          // Clear input field
          terminalInput.value = "";
          
          // Hide input line temporarily
          terminalInputLine.style.display = "none";
          isWaitingForInput = false;
          
          // Check if more inputs are needed
          const code = codeEditor.value.trim();
          const language_id = parseInt(languageSelect.value);
          const expectedInputs = countExpectedInputs(code, language_id);
          
          if (inputCount < expectedInputs) {
            // Show next prompt on new line
            terminalOutput.textContent += "\n";
            const nextPrompt = inputPrompts[inputCount] || "Enter input: ";
            showInputPrompt(nextPrompt);
          } else {
            // All inputs collected, run the code
            terminalOutput.textContent += "\n";
            const stdin = userInputs.join("\n");
            await runCodeWithInputs(code, language_id, stdin);
          }
        }
      });
    }
    
    // Show input prompt in terminal
    function showInputPrompt(prompt) {
      isWaitingForInput = true;
      
      // Add prompt to output with space (user will type on same line)
      const currentText = terminalOutput.textContent;
      // Add newline before prompt if there's already content
      if (currentText && !currentText.endsWith("\n")) {
        terminalOutput.textContent += "\n" + prompt + " ";
      } else {
        terminalOutput.textContent += prompt + " ";
      }
      
      // Show input field inline
      inputPrompt.textContent = "";
      terminalInputLine.style.display = "block";
      terminalInput.value = "";
      terminalInput.focus();
    }
    
    // Detect if code requires input
    function detectInputRequired(code, language_id) {
      const lowerCode = code.toLowerCase();
      
      // Python
      if (language_id === 71 && (lowerCode.includes("input(") || lowerCode.includes("raw_input("))) {
        return true;
      }
      // C/C++
      if ((language_id === 50 || language_id === 54) && 
          (lowerCode.includes("scanf(") || lowerCode.includes("cin >>") || lowerCode.includes("cin>>"))) {
        return true;
      }
      // Java
      if (language_id === 62 && (lowerCode.includes("scanner") || lowerCode.includes(".nextint(") || 
          lowerCode.includes(".nextline(") || lowerCode.includes(".next("))) {
        return true;
      }
      // JavaScript
      if (language_id === 63 && lowerCode.includes("readline(")) {
        return true;
      }
      
      return false;
    }
    
    // Count expected inputs from code
    function countExpectedInputs(code, language_id) {
      let count = 0;
      const lowerCode = code.toLowerCase();
      
      if (language_id === 71) { // Python
        count = (code.match(/input\(/g) || []).length;
      } else if (language_id === 50 || language_id === 54) { // C/C++
        count = (code.match(/scanf\(/g) || []).length + (code.match(/cin\s*>>/g) || []).length;
      } else if (language_id === 62) { // Java
        count = (code.match(/\.next\w*\(/g) || []).length;
      }
      
      return count;
    }
    
    // Run code with given stdin
    async function runCodeWithInputs(code, language_id, stdin) {
      try {
        const response = await fetch("/run", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ code, language_id, stdin })
        });

        const data = await response.json();
        console.log("Run response:", data);
        
        let output = data.output || "⚠️ No output returned.";
        
        // Filter out input prompts from the output (they're already shown interactively)
        if (inputPrompts.length > 0) {
          // Remove all the prompts that we already displayed for ANY language
          inputPrompts.forEach(prompt => {
            // Remove the prompt text from output (handle with and without trailing space)
            output = output.replace(new RegExp(prompt + '\\s*', 'g'), '');
          });
          
          // Clean up any extra whitespace or newlines at the start
          output = output.trim();
        }
        
        // Clear the "Running your code..." message before displaying output
        const currentText = terminalOutput.textContent;
        if (currentText.includes("⏳ Running your code...")) {
          terminalOutput.textContent = "";
        }
        
        // Check if output contains errors (MOVED UP - Must be declared before use)
        const hasError = output.includes("Error") || 
                        output.includes("Traceback") || 
                        output.includes("Exception") ||
                        output.includes("SyntaxError") ||
                        output.includes("NameError") ||
                        output.includes("TypeError") ||
                        output.includes("IndexError") ||
                        output.includes("ValueError");
        
        // Display the final output
        if (output) {
            // Enhanced error formatting
            if (hasError) {
              // Try to extract line number for Python errors
              let formatted = output;
              let lineMatch = formatted.match(/File ".*", line (\d+)/);
              let lineInfo = lineMatch ? ` (Line ${lineMatch[1]})` : "";

              // Highlight error type
              let errorTypeMatch = formatted.match(/(SyntaxError|NameError|TypeError|IndexError|ValueError|Exception|Traceback)/);
              let errorType = errorTypeMatch ? errorTypeMatch[1] : "Error";

              // Add suggestions for common errors
              let suggestion = "";
              if (errorType === "SyntaxError") suggestion = "Check for missing colons, parentheses, or indentation.";
              if (errorType === "NameError") suggestion = "Check for typos or undefined variables.";
              if (errorType === "TypeError") suggestion = "Check variable types and function arguments.";
              if (errorType === "IndexError") suggestion = "Check list/array indices.";
              if (errorType === "ValueError") suggestion = "Check value formats and conversions.";

              // Format output
              formatted = `❌ <b>${errorType}${lineInfo}</b>\n<pre style='color:#ff6b6b;background:#1a1a1a;padding:0.5em;border-radius:6px;'>${output}</pre>`;
              if (suggestion) {
                formatted += `\n💡 <b>Suggestion:</b> ${suggestion}`;
              }
              formatted += "\n\n💡 Tip: Click the 🪲 Debug button to analyze and fix these errors!";
              terminalOutput.innerHTML += formatted;
            } else {
              terminalOutput.textContent += output;
            }
        }
        
        if (hasError) {
          // Store the error for debugging
          localStorage.setItem("runtimeError", output);
          localStorage.setItem("errorCode", code);
          localStorage.setItem("errorLanguage", languageSelect.options[languageSelect.selectedIndex].text);
          
          // Show helpful message
          terminalOutput.textContent += "\n\n💡 Tip: Click the 🪲 Debug button to analyze and fix these errors!";
        } else {
          // Clear any previous errors
          localStorage.removeItem("runtimeError");
          localStorage.removeItem("errorCode");
          localStorage.removeItem("errorLanguage");
        }
        
        // Hide input line after code completes
        terminalInputLine.style.display = "none";
        
      } catch (err) {
        terminalOutput.textContent += "\n❌ Error: " + err.message;
        terminalInputLine.style.display = "none";
        
        // Store network/fetch error for debugging
        localStorage.setItem("runtimeError", err.message);
        localStorage.setItem("errorCode", code);
        localStorage.setItem("errorLanguage", languageSelect.options[languageSelect.selectedIndex].text);
      }
    }
  }

  // ---- EXPLAIN CODE ----
  // Format explanation in ChatGPT style
  function formatExplanation(text) {
    let html = '';
    const lines = text.split('\n');
    let inSection = false;
    let sectionContent = '';
    let sectionTitle = '';

    for (let line of lines) {
      // Section headers
      if (line.match(/^(Language:|Lines:|Imports|Classes|Functions|Top-level observations:|Quick recommendations:|Python hints:)/i)) {
        if (inSection && sectionContent) {
          html += createExplanationCard(sectionTitle, sectionContent);
          sectionContent = '';
        }
        sectionTitle = line;
        inSection = true;
      } else if (inSection) {
        sectionContent += line + '\n';
      } else {
        if (line.trim()) {
          html += `<div style="margin-bottom: 0.5rem; color: #ececf1;">${escapeHtml(line)}</div>`;
        }
      }
    }

    if (inSection && sectionContent) {
      html += createExplanationCard(sectionTitle, sectionContent);
    }

    // Wrap all cards in a grid container for more color and spacing
    return `<div class="explanation-grid">${html}</div>` || `<div style="padding: 1rem; color: #888;">${escapeHtml(text)}</div>`;
  }

  function createExplanationCard(title, content) {
    const iconMap = {
      'language': '🔤',
      'lines': '📝',
      'imports': '📦',
      'classes': '🏛️',
      'functions': '⚡',
      'observations': '🔍',
      'recommendations': '💡',
      'hints': '🎯'
    };

    const colorMap = {
      'language': '#6ad7ff',
      'lines': '#ffc107',
      'imports': '#a259ff',
      'classes': '#ff5459',
      'functions': '#10a37f',
      'observations': '#ffb86c',
      'recommendations': '#00c896',
      'hints': '#ffb300'
    };

    const emojiMap = {
      'language': '🌐',
      'lines': '📏',
      'imports': '📦',
      'classes': '🏛️',
      'functions': '🛠️',
      'observations': '👀',
      'recommendations': '✨',
      'hints': '🧠'
    };

    const lowerTitle = title.toLowerCase();
    let icon = '📌';
    let color = '#10a37f';
    let emoji = '💬';
    for (let key of Object.keys(iconMap)) {
      if (lowerTitle.includes(key)) {
        icon = iconMap[key];
        color = colorMap[key];
        emoji = emojiMap[key];
        break;
      }
    }

    let html = `<div class="explanation-card" style="background: linear-gradient(135deg, ${color}22 0%, #222 100%); border-left: 6px solid ${color}; box-shadow: 0 2px 8px ${color}33; margin: 1rem; padding: 1.2rem 1.5rem; border-radius: 12px; display: flex; flex-direction: column; gap: 0.5rem;">`;
    html += `<div class="explanation-title" style="font-size: 1.1rem; font-weight: 600; color: ${color}; margin-bottom: 0.5rem;">${emoji} ${escapeHtml(title)}</div>`;
    html += '<div class="explanation-content" style="color: #ececf1;">';

    const contentLines = content.split('\n').filter(l => l.trim());
    for (let line of contentLines) {
      line = line.trim();
      if (line.startsWith('-')) {
        html += `<div style="margin-left: 1rem; margin-bottom: 0.3rem;">🌈 ${escapeHtml(line.substring(1).trim())}</div>`;
      } else if (line.match(/^(def |function |class |import |#include)/)) {
        html += `<div class="explanation-code" style="background: #181818; color: #6ad7ff; border-radius: 6px; padding: 0.3rem 0.7rem; margin: 0.3rem 0; font-family: 'Consolas', monospace; font-size: 0.95rem;">${escapeHtml(line)}</div>`;
      } else if (line) {
        html += `<div style="margin-bottom: 0.5rem;">${escapeHtml(line)}</div>`;
      }
    }

    html += '</div></div>';
    return html;
  }
  
  function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }
  
  // Client-side explanation generator (lightweight heuristics)
  function generateExplanation(code, languageText) {
    const lines = code.split(/\r?\n/).map(l => l.replace(/\t/g, '    '));
    const totalLines = lines.length;

    const imports = [];
    const functions = [];
    const classes = [];
    let prints = 0;
    let loops = 0;
    let conditionals = 0;

    for (let i = 0; i < lines.length; i++) {
      const raw = lines[i];
      const l = raw.trim();
      if (!l) continue;

      // imports
      if (/^(import |from )/.test(l) || /#include\s*</.test(l)) {
        imports.push(l);
        continue;
      }

      // function signatures (Python / JS / C-like heuristics)
      if (/^def\s+\w+\s*\(/.test(l) || /^function\s+\w+\s*\(/.test(l) || /^[\w\*:]+\s+\w+\s*\([^)]*\)\s*\{?$/.test(l)) {
        // keep a short form of the signature
        functions.push(l.replace(/\s+/g, ' '));
        continue;
      }

      // classes
      if (/^class\s+\w+/.test(l) || /^struct\s+\w+/.test(l)) {
        classes.push(l);
        continue;
      }

      // prints / logs
      if (/\bprint\s*\(|\bconsole\.log\s*\(|\bprintf\s*\(/.test(l)) prints++;

      // loops
      if (/^for\b|\bfor\s*\(/.test(l) || /^while\b|\bwhile\s*\(/.test(l)) loops++;

      // conditionals
      if (/^if\b|\bif\s*\(/.test(l) || /^else\b/.test(l)) conditionals++;
    }

    let summary = `Language: ${languageText}\nLines: ${totalLines}\n`;
    if (imports.length) summary += `\nImports (${imports.length}):\n- ${imports.join('\n- ')}\n`;
    if (classes.length) summary += `\nClasses (${classes.length}):\n- ${classes.join('\n- ')}\n`;
    if (functions.length) summary += `\nFunctions (${functions.length}):\n- ${functions.join('\n- ')}\n`;

    summary += `\nTop-level observations:\n- print/log statements: ${prints}\n- loops: ${loops}\n- conditionals: ${conditionals}\n`;

    summary += `\nQuick recommendations:\n- Add docstrings/comments for functions and complex blocks.\n- Validate inputs and handle edge cases.\n- Avoid heavy work inside tight loops; cache results where possible.\n- Add tests for boundary cases.\n`;

    // Friendly extra hint for Python
    if (/python/i.test(languageText)) {
      summary += `\nPython hints:\n- Use list comprehensions for concise transformations.\n- Prefer enumerations over range(len(...)) when iterating with indexes.\n`;
    }

    return summary;
  }

  if (explainBtn && explanationSection && explanationBox) {
    console.log("Explain button listener attached successfully");
    
    // Close button handler
    const closeExplainBtn = document.getElementById("closeExplainBtn");
    const explainHeader = document.querySelector(".explain-header");
    
    // Function to close/hide the explanation section (minimize it to show header only)
    const closeExplanation = () => {
      explanationSection.classList.remove("show");
      explanationSection.classList.remove("hidden");
      explanationSection.classList.add("minimized");
    };
    
    // Function to open/show the explanation section
    const openExplanation = () => {
      explanationSection.classList.remove("hidden");
      explanationSection.classList.remove("minimized");
      setTimeout(() => {
        explanationSection.classList.add("show");
        // Scroll to explanation section smoothly
        explanationSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
      }, 10);
    };
    
    if (closeExplainBtn) {
      closeExplainBtn.addEventListener("click", (e) => {
        e.stopPropagation();
        closeExplanation();
      });
    }
    
    // Click header to toggle expand/collapse
    if (explainHeader) {
      explainHeader.addEventListener("click", () => {
        if (explanationSection) {
          if (explanationSection.classList.contains("show")) {
            closeExplanation(); // Collapse to minimized state
          } else if (explanationSection.classList.contains("minimized")) {
            openExplanation(); // Expand from minimized state
          }
        }
      });
    }
    
    explainBtn.addEventListener("click", async () => {
      console.log("Explain button clicked!");
      console.log("window.USER_LOGGED_IN =", window.USER_LOGGED_IN);
      console.log("typeof window.USER_LOGGED_IN =", typeof window.USER_LOGGED_IN);
      
      // Check if user is logged in
      if (!window.USER_LOGGED_IN) {
        console.log("User not logged in, redirecting...");
        Toast.warning("Please login to use the AI Explain feature. This is a premium feature available to registered users.");
        setTimeout(() => { window.location.href = "/login"; }, 1500);
        return;
      }
      
      console.log("User is logged in, proceeding with explain...");
      const code = codeEditor.value.trim();
      const languageText = languageSelect.options[languageSelect.selectedIndex].text || languageSelect.value;
      const languageValue = (languageText || "").toLowerCase();

      // Show the section with slide-up animation
      console.log("Opening explanation section with slide-up animation");
      openExplanation();

      if (!code) {
        explanationBox.innerHTML = `
          <div class="explain-placeholder" style="padding: 3rem 2rem; text-align: center;">
            <div style="font-size: 3rem; margin-bottom: 1rem; color: #ffa500;">⚠️</div>
            <p style="color: #ffa500; font-size: 1.1rem; font-weight: 500;">Please write some code to explain!</p>
            <p style="color: #666; font-size: 0.9rem; margin-top: 0.5rem;">Enter your code in the editor above and try again.</p>
          </div>
        `;
        return;
      }

      // Show loading state with animation
      const originalText = explainBtn.innerHTML;
      explainBtn.disabled = true;
      explainBtn.innerHTML = "⏳ Analyzing...";

      explanationBox.innerHTML = `
        <div class="explain-loading">
          <div class="explain-loading-icon">🤖</div>
          <p>Analyzing your code...</p>
          <p class="explain-loading-subtitle">AI is thinking... This may take a few seconds</p>
        </div>
      `;

      try {
        // Try the new colorful HTML endpoint first
        const resp = await fetch("/explain_html", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ code, language: languageValue })
        });

        if (!resp.ok) throw new Error(`Server returned ${resp.status}`);
        const data = await resp.json();

        // Display the beautiful colorful HTML
        if (data.html) {
          explanationBox.innerHTML = data.html;
        } else {
          throw new Error("No HTML returned from server");
        }
      } catch (err) {
        console.log("Colorful endpoint failed, trying fallback...", err);
        // Fallback to plain text endpoint
        try {
          const resp = await fetch("/explain", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ code, language: languageValue })
          });

          if (!resp.ok) throw new Error(`Server returned ${resp.status}`);
          const data = await resp.json();

          // If server reports that linter is missing, fall back to local generator
          if (data.explanation && /Linter tool not found|No linter configured/.test(data.explanation)) {
            const localExplanation = generateExplanation(code, languageText);
            explanationBox.innerHTML = formatExplanation(localExplanation) + 
              '<div class="explanation-card" style="border-left-color: #ffc107;"><div class="explanation-title">⚠️ Note</div><div class="explanation-content">' + 
              escapeHtml(data.explanation) + '</div></div>';
            return;
          }

          // Prefer server-provided explanation (structured + linter output)
          if (data.explanation) {
            explanationBox.innerHTML = formatExplanation(data.explanation);
          } else {
            const localExplanation = generateExplanation(code, languageText);
            explanationBox.innerHTML = formatExplanation(localExplanation);
          }
        } catch (err2) {
          // Final fallback: use local generator
          const localExplanation = generateExplanation(code, languageText);
          explanationBox.innerHTML = '<div class="explanation-card" style="border-left-color: #ff5459;"><div class="explanation-title">⚠️ Server Unavailable</div><div class="explanation-content">Using local explanation generator.</div></div>' + 
            formatExplanation(localExplanation);
        }
      } finally {
        // Re-enable button
        explainBtn.disabled = false;
        explainBtn.innerHTML = originalText;
      }
    });
  }

  // ---- DEBUG CODE ----
  // Send code to debug page via localStorage
  if (debugBtn) {
    debugBtn.addEventListener("click", () => {
      // Check if user is logged in
      if (!window.USER_LOGGED_IN) {
        Toast.warning("Please login to use the AI Debugger feature. This is a premium feature available to registered users.");
        setTimeout(() => { window.location.href = "/login"; }, 1500);
        return;
      }
      
      const code = codeEditor.value.trim();
      const languageText = languageSelect.options[languageSelect.selectedIndex].text || "Python";
      
      if (!code) {
        Toast.warning("Please write some code before debugging!");
        return;
      }

      // Check if there's a runtime error stored
      const runtimeError = localStorage.getItem("runtimeError");
      const errorCode = localStorage.getItem("errorCode");
      
      // Store code and language in localStorage
      localStorage.setItem("debugCode", code);
      localStorage.setItem("debugLanguage", languageText);
      
      // If there's no matching runtime error, clear old ones
      if (!runtimeError || errorCode !== code) {
        localStorage.removeItem("runtimeError");
        localStorage.removeItem("errorCode");
        localStorage.removeItem("errorLanguage");
      }
      
      // Navigate to debug page
      window.location.href = "/debugger";
    });
  }

  // ---- OPTIMIZE CODE ----
  // Send code to optimizer page via localStorage
  const optimizeBtn = document.getElementById("optimizeBtn");
  if (optimizeBtn) {
    optimizeBtn.addEventListener("click", () => {
      // Check if user is logged in
      if (!window.USER_LOGGED_IN) {
        Toast.warning("Please login to use the AI Optimizer feature. This is a premium feature available to registered users.");
        setTimeout(() => { window.location.href = "/login"; }, 1500);
        return;
      }
      
      const code = codeEditor.value.trim();
      const languageText = languageSelect.options[languageSelect.selectedIndex].text || "Python";
      
      if (!code) {
        Toast.warning("Please write some code before optimizing!");
        return;
      }

      // Store code and language in localStorage
      localStorage.setItem("optimizeCode", code);
      localStorage.setItem("optimizeLanguage", languageText);
      
      // Navigate to optimizer page (no need to disable button since we're leaving the page)
      window.location.href = "/optimizer";
    });
  }

  // ---- LINE NUMBERS UPDATE & SYNTAX HIGHLIGHTING ----
  const lineNumbers = document.getElementById("lineNumbers");
  const highlightedCode = document.getElementById("highlightedCode");
  const syntaxHighlight = document.getElementById("syntaxHighlight");
  
  // Map language IDs to language names (for Judge0 API)
  const judge0LanguageMap = {
    "71": "python",
    "50": "c",
    "54": "cpp",
    "63": "javascript",
    "62": "java"
  };
  
  // Compatibility stubs - CodeMirror handles these automatically
  function updateLineNumbers() {
    // No longer needed - CodeMirror handles line numbers
  }
  
  function updateSyntaxHighlight() {
    // No longer needed - CodeMirror handles syntax highlighting
  }
  
  function syncScroll() {
    // No longer needed - CodeMirror handles scrolling
  }

  // ============================================
  // AUTO-BRACKET & INDENTATION
  // ============================================
  // CodeMirror handles all of this automatically via:
  // - autoCloseBrackets option
  // - matchBrackets option
  // - Built-in indentation logic
  // No manual event listeners needed!
  
  // ============================================
  // LANGUAGE CHANGE HANDLER
  // ============================================
  if (languageSelect) {
    languageSelect.addEventListener('change', () => {
      const languageId = languageSelect.value;
      const mode = languageModeMap[languageId] || "python";
      
      // Update CodeMirror mode
      codeMirrorEditor.setOption("mode", mode);
      
      console.log(`✅ Language changed to: ${mode}`);
    });
  }

  // ---- COPY BUTTON ----
  const copyCodeBtn = document.getElementById("copyCodeBtn");
  
  if (copyCodeBtn && codeEditor) {
    copyCodeBtn.addEventListener("click", () => {
      const code = codeEditor.value;
      
      if (!code) {
        Toast.warning("No code to copy!");
        return;
      }

      // Copy to clipboard
      navigator.clipboard.writeText(code).then(() => {
        // Visual feedback
        const originalText = copyCodeBtn.textContent;
        copyCodeBtn.textContent = "✓ Copied!";
        copyCodeBtn.style.background = "#10b981";
        Toast.success("Code copied to clipboard!");
        
        setTimeout(() => {
          copyCodeBtn.textContent = originalText;
          copyCodeBtn.style.background = "";
        }, 2000);
      }).catch(err => {
        Toast.error("Failed to copy: " + err);
      });
    });
  }

  // ---- DOWNLOAD CODE BUTTON ----
  const downloadCodeBtn = document.getElementById("downloadCodeBtn");
  
  if (downloadCodeBtn && codeEditor && languageSelect) {
    downloadCodeBtn.addEventListener("click", () => {
      // Check if user is logged in
      if (!window.USER_LOGGED_IN) {
        Toast.warning("Please login to download your code. Create a free account to download and save your projects.");
        setTimeout(() => { window.location.href = "/login"; }, 1500);
        return;
      }
      
      const code = codeEditor.value;
      
      if (!code) {
        Toast.warning("No code to download!");
        return;
      }

      // Get file extension based on language
      const languageId = languageSelect.value;
      const extensions = {
        "71": ".py",   // Python
        "50": ".c",    // C
        "54": ".cpp",  // C++
        "63": ".js",   // JavaScript
        "62": ".java"  // Java
      };
      const extension = extensions[languageId] || ".txt";
      
      // Create filename
      const timestamp = new Date().toISOString().slice(0, 19).replace(/:/g, '-');
      const filename = `code_${timestamp}${extension}`;
      
      // Create blob and download
      const blob = new Blob([code], { type: 'text/plain' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      
      // Success notification
      Toast.success("Code downloaded as " + filename);
      
      // Visual feedback
      const originalText = downloadCodeBtn.textContent;
      downloadCodeBtn.textContent = "✓ Downloaded!";
      downloadCodeBtn.style.background = "#10b981";
      
      setTimeout(() => {
        downloadCodeBtn.textContent = originalText;
        downloadCodeBtn.style.background = "";
      }, 2000);
    });
  }

  // ---- HISTORY MANAGEMENT ----
  const historyList = document.getElementById("historyList");
  const searchBox = document.getElementById("searchBox");

  let allHistory = [];

  // Load history from server
  async function loadHistory() {
    try {
      const response = await fetch('/api/history?limit=100');
      const data = await response.json();
      
      if (data.error) {
        console.error('Error loading history:', data.error);
        return;
      }
      
      allHistory = data.history || [];
      displayHistory(allHistory);
    } catch (err) {
      console.error('Error loading history:', err);
    }
  }

  // Display history items
  function displayHistory(items) {
    if (!historyList) return;

    if (items.length === 0) {
      historyList.innerHTML = '<p style="font-size:0.85rem;color:#777;padding:1rem;">No history yet...</p>';
      return;
    }

    historyList.innerHTML = items.map(item => {
      const icon = {
        'run': '▶️',
        'debug': '🪲',
        'optimize': '⚙️',
        'explain': '💡'
      }[item.activity_type] || '📝';

      const date = new Date(item.created_at);
      const timeAgo = getTimeAgo(date);

      return `
        <div class="history-item" data-id="${item.id}">
          <div style="display:flex;justify-content:space-between;align-items:start;">
            <div style="flex:1;min-width:0;">
              <div style="display:flex;align-items:center;gap:0.5rem;margin-bottom:0.3rem;">
                <span>${icon}</span>
                <span style="font-weight:600;font-size:0.9rem;color:#fff;">${item.activity_type.toUpperCase()}</span>
                <span style="font-size:0.75rem;color:#888;">${item.language}</span>
              </div>
              <div style="font-size:0.85rem;color:#ececf1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">
                ${escapeHtml(item.title)}
              </div>
              <div style="font-size:0.75rem;color:#666;margin-top:0.2rem;">${timeAgo}</div>
            </div>
            <button onclick="deleteHistoryItem(${item.id})" 
                    style="background:transparent;border:none;color:#ff4444;cursor:pointer;padding:0.2rem 0.5rem;font-size:1.2rem;margin-left:0.5rem;"
                    title="Delete">×</button>
          </div>
        </div>
      `;
    }).join('');

    // Add click handlers to load history items
    document.querySelectorAll('.history-item').forEach(item => {
      item.addEventListener('click', (e) => {
        if (e.target.tagName === 'BUTTON') return; // Don't load if delete button clicked
        const id = item.dataset.id;
        loadHistoryItem(id);
      });
    });
  }

  // Load a specific history item
  async function loadHistoryItem(id) {
    try {
      const response = await fetch(`/api/history/${id}`);
      const data = await response.json();
      
      if (data.error) {
        alert('Error loading history item: ' + data.error);
        return;
      }

      // Load the code into editor
      codeEditor.value = data.code_snippet;
      
      // Set language
      const languageMap = {
        'Python': '71',
        'C': '50',
        'C++': '54',
        'Javascript': '63',
        'Java': '62'
      };
      languageSelect.value = languageMap[data.language] || '71';
      
      // Update UI
      updateLineNumbers();
      updateSyntaxHighlight();
      
      // Show output if available (use bottom sheet animation)
      if (data.output && resultBox && resultSection) {
        resultBox.textContent = data.output;
        openOutput();
      }

      // Scroll to top
      window.scrollTo({ top: 0, behavior: 'smooth' });
    } catch (err) {
      alert('Error loading history: ' + err.message);
    }
  }

  // Delete history item
  window.deleteHistoryItem = async function(id) {
    if (!confirm('Delete this history item?')) return;

    try {
      const response = await fetch(`/api/history/${id}`, {
        method: 'DELETE'
      });
      
      const data = await response.json();
      
      if (data.success) {
        // Reload history
        loadHistory();
      } else {
        alert('Error deleting: ' + data.error);
      }
    } catch (err) {
      alert('Error deleting history: ' + err.message);
    }
  };

  // Search history
  if (searchBox) {
    searchBox.addEventListener('input', (e) => {
      const query = e.target.value.toLowerCase();
      
      if (!query) {
        displayHistory(allHistory);
        return;
      }

      const filtered = allHistory.filter(item => 
        item.title.toLowerCase().includes(query) ||
        item.code_snippet.toLowerCase().includes(query) ||
        item.language.toLowerCase().includes(query) ||
        item.activity_type.toLowerCase().includes(query)
      );

      displayHistory(filtered);
    });
  }

  // Helper function for time ago
  function getTimeAgo(date) {
    const seconds = Math.floor((new Date() - date) / 1000);
    
    if (seconds < 60) return 'Just now';
    if (seconds < 3600) return Math.floor(seconds / 60) + 'm ago';
    if (seconds < 86400) return Math.floor(seconds / 3600) + 'h ago';
    if (seconds < 604800) return Math.floor(seconds / 86400) + 'd ago';
    
    return date.toLocaleDateString();
  }

  // Load history on page load
  loadHistory();

  // Refresh history every 30 seconds
  setInterval(loadHistory, 30000);

  // ---- KEYBOARD SHORTCUTS ----
  document.addEventListener('keydown', (e) => {
    // Ctrl+Enter or Cmd+Enter to run code
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
      e.preventDefault();
      if (runBtn && !runBtn.disabled) {
        console.log('⌨️ Keyboard shortcut: Ctrl+Enter -> Run code');
        runBtn.click();
      }
    }
    
    // Ctrl+S or Cmd+S to save code
    if ((e.ctrlKey || e.metaKey) && e.key === 's') {
      e.preventDefault();
      if (saveBtn && !saveBtn.disabled) {
        console.log('⌨️ Keyboard shortcut: Ctrl+S -> Save code');
        saveBtn.click();
      }
    }
    
    // Ctrl+E or Cmd+E to explain code
    if ((e.ctrlKey || e.metaKey) && e.key === 'e') {
      e.preventDefault();
      if (explainBtn && !explainBtn.disabled) {
        console.log('⌨️ Keyboard shortcut: Ctrl+E -> Explain code');
        explainBtn.click();
      }
    }
    
    // Ctrl+D or Cmd+D to debug code
    if ((e.ctrlKey || e.metaKey) && e.key === 'd') {
      e.preventDefault();
      if (debugBtn && !debugBtn.disabled) {
        console.log('⌨️ Keyboard shortcut: Ctrl+D -> Debug code');
        debugBtn.click();
      }
    }
  });
  
  // Load project if ?load=id parameter is present
  const urlParams = new URLSearchParams(window.location.search);
  const loadId = urlParams.get('load');
  
  if (loadId) {
    loadProject(loadId);
  }
  
  async function loadProject(id) {
    try {
      const response = await fetch(`/api/history/${id}`);
      const data = await response.json();
      
      if (data.code_snippet) {
        codeEditor.value = data.code_snippet;
        
        // Set the language
        const languageMap = {
          'Python': '71',
          'C': '50',
          'C++': '54',
          'JavaScript': '63',
          'Java': '62'
        };
        
        // Find language in the name (handles "JavaScript (Node.js...)")
        let languageId = '71'; // default to Python
        for (const [lang, id] of Object.entries(languageMap)) {
          if (data.language.includes(lang)) {
            languageId = id;
            break;
          }
        }
        
        languageSelect.value = languageId;
        
        // Update syntax highlighting and line numbers
        if (typeof updateSyntaxHighlight === 'function') {
          updateSyntaxHighlight();
        }
        if (typeof updateLineNumbers === 'function') {
          updateLineNumbers();
        }
        
        console.log('✅ Project loaded successfully:', data.title);
      } else {
        alert('❌ Failed to load project: ' + (data.error || 'Unknown error'));
      }
    } catch (err) {
      alert('❌ Error loading project: ' + err.message);
    }
  }

  // ============================================
  // MOBILE MENU TOGGLE
  // ============================================
  const mobileMenuToggle = document.getElementById('mobileMenuToggle');
  const sidebar = document.getElementById('sidebar');
  const sidebarOverlay = document.getElementById('sidebarOverlay');

  if (mobileMenuToggle && sidebar && sidebarOverlay) {
    // Toggle sidebar on button click
    mobileMenuToggle.addEventListener('click', () => {
      sidebar.classList.toggle('active');
      sidebarOverlay.classList.toggle('active');
      
      // Change icon
      if (sidebar.classList.contains('active')) {
        mobileMenuToggle.textContent = '✕';
      } else {
        mobileMenuToggle.textContent = '☰';
      }
    });

    // Close sidebar when overlay is clicked
    sidebarOverlay.addEventListener('click', () => {
      sidebar.classList.remove('active');
      sidebarOverlay.classList.remove('active');
      mobileMenuToggle.textContent = '☰';
    });

    // Close sidebar when a menu item is clicked (mobile)
    const sidebarButtons = sidebar.querySelectorAll('button, .menu-item');
    sidebarButtons.forEach(button => {
      button.addEventListener('click', () => {
        // Only close on mobile (screen width < 768px)
        if (window.innerWidth <= 768) {
          sidebar.classList.remove('active');
          sidebarOverlay.classList.remove('active');
          mobileMenuToggle.textContent = '☰';
        }
      });
    });
  }

  // ==================== KEYBOARD SHORTCUTS ====================
  console.log("⌨️ Setting up keyboard shortcuts...");
  
  // Keyboard shortcuts handler
  document.addEventListener('keydown', (e) => {
    // Ctrl+Enter or Cmd+Enter: Run code
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
      e.preventDefault();
      console.log("⌨️ Keyboard shortcut: Run code (Ctrl+Enter)");
      if (runBtn && !runBtn.disabled) {
        runBtn.click();
      }
      return;
    }

    // Ctrl+S or Cmd+S: Save code
    if ((e.ctrlKey || e.metaKey) && e.key === 's') {
      e.preventDefault();
      console.log("⌨️ Keyboard shortcut: Save code (Ctrl+S)");
      if (saveBtn && !saveBtn.disabled) {
        saveBtn.click();
      }
      return;
    }

    // Ctrl+Shift+E or Cmd+Shift+E: Explain code
    if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'E') {
      e.preventDefault();
      console.log("⌨️ Keyboard shortcut: Explain code (Ctrl+Shift+E)");
      if (explainBtn && !explainBtn.disabled) {
        explainBtn.click();
      }
      return;
    }

    // Ctrl+Shift+D or Cmd+Shift+D: Debug code
    if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'D') {
      e.preventDefault();
      console.log("⌨️ Keyboard shortcut: Debug code (Ctrl+Shift+D)");
      if (debugBtn && !debugBtn.disabled) {
        debugBtn.click();
      }
      return;
    }

    // Ctrl+Shift+O or Cmd+Shift+O: Optimize code
    if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'O') {
      e.preventDefault();
      console.log("⌨️ Keyboard shortcut: Optimize code (Ctrl+Shift+O)");
      if (optimizeBtn && !optimizeBtn.disabled) {
        optimizeBtn.click();
      }
      return;
    }

    // Ctrl+/ or Cmd+/: Show shortcuts help
    if ((e.ctrlKey || e.metaKey) && e.key === '/') {
      e.preventDefault();
      showShortcutsHelp();
      return;
    }
  });

  // Function to show keyboard shortcuts help (make it global)
  window.showShortcutsHelp = function() {
    const isMac = navigator.platform.toUpperCase().indexOf('MAC') >= 0;
    const modifier = isMac ? 'Cmd' : 'Ctrl';
    
    const helpMessage = `
⌨️ KEYBOARD SHORTCUTS:

${modifier} + Enter     - Run code
${modifier} + S         - Save code
${modifier} + Shift + E - Explain code (AI)
${modifier} + Shift + D - Debug code (AI)
${modifier} + Shift + O - Optimize code (AI)
${modifier} + /         - Show this help

💡 Tip: These shortcuts work anywhere on the page!
    `.trim();
    
    alert(helpMessage);
  };

  console.log("✅ Keyboard shortcuts enabled! Press Ctrl+/ for help");
});
