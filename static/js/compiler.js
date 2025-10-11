document.addEventListener("DOMContentLoaded", () => {
  const runBtn = document.getElementById("runBtn");
  const explainBtn = document.getElementById("explainBtn");
  const debugBtn = document.getElementById("debugBtn");

  const codeEditor = document.getElementById("codeEditor");
  const languageSelect = document.getElementById("languageSelect");

  const resultBox = document.getElementById("resultBox");
  const explanationBox = document.getElementById("explanationBox");

  const resultSection = document.getElementById("resultSection");
  const explanationSection = document.getElementById("explanationSection");

  const debugSection = document.getElementById("debugSection"); // might not exist
  const debugBox = document.getElementById("debugOutput"); // might not exist

  // ---- RUN CODE ----
  if (runBtn && resultSection && resultBox) {
    runBtn.addEventListener("click", async () => {
      const code = codeEditor.value.trim();
      const language_id = parseInt(languageSelect.value);
      const inputBox = document.getElementById("inputBox");
      const stdin = inputBox ? inputBox.value : "";

      resultSection.classList.remove("hidden"); // show output section

      if (!code) {
        resultBox.textContent = "⚠️ Please write some code before running!";
        return;
      }

      resultBox.textContent = "⏳ Running your code...";
      try {
        const response = await fetch("/run", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ code, language_id, stdin })
        });

        const data = await response.json();
        console.log("Run response:", data);
        resultBox.textContent = data.output || "⚠️ No output returned.";
      } catch (err) {
        resultBox.textContent = "❌ Error: " + err.message;
      }
    });
  }

  // ---- EXPLAIN CODE ----
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
    explainBtn.addEventListener("click", async () => {
      const code = codeEditor.value.trim();
      const languageText = languageSelect.options[languageSelect.selectedIndex].text || languageSelect.value;
      const languageValue = (languageText || "").toLowerCase();

      explanationSection.classList.remove("hidden");

      if (!code) {
        explanationBox.textContent = "⚠️ Please write some code to explain!";
        return;
      }

      explanationBox.textContent = "💡 Contacting server for linted explanation...";

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
          explanationBox.textContent = generateExplanation(code, languageText) + "\n\n" + data.explanation;
          return;
        }

        // Prefer server-provided explanation (structured + linter output)
        if (data.explanation) {
          explanationBox.textContent = data.explanation;
        } else {
          explanationBox.textContent = generateExplanation(code, languageText);
        }
      } catch (err) {
        // Fallback: use local generator
        explanationBox.textContent = "⚠️ Server unavailable, using local explanation.\n\n" + generateExplanation(code, languageText);
      }
    });
  }

  // ---- DEBUG CODE ----
  // Send code to debug page via localStorage
  if (debugBtn) {
    debugBtn.addEventListener("click", () => {
      const code = codeEditor.value.trim();
      const languageText = languageSelect.options[languageSelect.selectedIndex].text || "Python";
      
      if (!code) {
        alert("⚠️ Please write some code before debugging!");
        return;
      }

      // Store code and language in localStorage
      localStorage.setItem("debugCode", code);
      localStorage.setItem("debugLanguage", languageText);
      
      // Navigate to debug page
      window.location.href = "/debugger";
    });
  }

  // ---- LINE NUMBERS UPDATE & SYNTAX HIGHLIGHTING ----
  const lineNumbers = document.getElementById("lineNumbers");
  const highlightedCode = document.getElementById("highlightedCode");
  const syntaxHighlight = document.getElementById("syntaxHighlight");
  
  // Map language IDs to Prism language classes
  const languageMap = {
    "71": "python",
    "50": "c",
    "54": "cpp",
    "63": "javascript",
    "62": "java"
  };
  
  function updateLineNumbers() {
    if (!codeEditor || !lineNumbers) return;
    
    const lines = codeEditor.value.split('\n');
    const lineCount = lines.length;
    
    // Generate line numbers
    let numbersHTML = '';
    for (let i = 1; i <= lineCount; i++) {
      numbersHTML += i + '\n';
    }
    lineNumbers.textContent = numbersHTML;
  }
  
  function updateSyntaxHighlight() {
    if (!codeEditor || !highlightedCode) return;
    
    const code = codeEditor.value;
    const languageId = languageSelect.value;
    const language = languageMap[languageId] || "python";
    
    // Update language class
    highlightedCode.className = `language-${language}`;
    
    // Escape HTML and highlight
    highlightedCode.textContent = code;
    
    // Apply Prism highlighting
    if (window.Prism) {
      Prism.highlightElement(highlightedCode);
    }
  }
  
  function syncScroll() {
    if (syntaxHighlight && codeEditor) {
      syntaxHighlight.scrollTop = codeEditor.scrollTop;
      syntaxHighlight.scrollLeft = codeEditor.scrollLeft;
    }
    if (lineNumbers && codeEditor) {
      lineNumbers.scrollTop = codeEditor.scrollTop;
    }
  }

  // ---- AUTO-COMPLETION FOR BRACKETS, QUOTES ----
  if (codeEditor) {
    codeEditor.addEventListener('keydown', (e) => {
      const start = codeEditor.selectionStart;
      const end = codeEditor.selectionEnd;
      const value = codeEditor.value;
      
      // Auto-close brackets, quotes, etc.
      const pairs = {
        '(': ')',
        '[': ']',
        '{': '}',
        '"': '"',
        "'": "'",
        '`': '`'
      };
      
      if (pairs[e.key]) {
        e.preventDefault();
        const closingChar = pairs[e.key];
        
        // Insert opening and closing characters
        const newValue = value.substring(0, start) + e.key + closingChar + value.substring(end);
        codeEditor.value = newValue;
        
        // Move cursor between the pair
        codeEditor.selectionStart = codeEditor.selectionEnd = start + 1;
        
        // Update UI
        updateLineNumbers();
        updateSyntaxHighlight();
        return;
      }
      
      // Handle Enter key for auto-indentation
      if (e.key === 'Enter') {
        e.preventDefault();
        
        const lines = value.substring(0, start).split('\n');
        const currentLine = lines[lines.length - 1];
        
        // Calculate current indentation
        const indent = currentLine.match(/^\s*/)[0];
        
        // Check if current line ends with characters that require extra indent
        const trimmedLine = currentLine.trim();
        const needsExtraIndent = /[\(\[\{:]$/.test(trimmedLine);
        
        // Determine new indentation
        let newIndent = indent;
        if (needsExtraIndent) {
          newIndent = indent + '    '; // Add 4 spaces (1 tab)
        }
        
        // Insert newline with indentation
        const newValue = value.substring(0, start) + '\n' + newIndent + value.substring(end);
        codeEditor.value = newValue;
        
        // Move cursor to end of indentation
        codeEditor.selectionStart = codeEditor.selectionEnd = start + 1 + newIndent.length;
        
        // Update UI
        updateLineNumbers();
        updateSyntaxHighlight();
        return;
      }
      
      // Handle Tab key for indentation
      if (e.key === 'Tab') {
        e.preventDefault();
        
        // Insert 4 spaces
        const newValue = value.substring(0, start) + '    ' + value.substring(end);
        codeEditor.value = newValue;
        
        // Move cursor after the tab
        codeEditor.selectionStart = codeEditor.selectionEnd = start + 4;
        
        // Update UI
        updateLineNumbers();
        updateSyntaxHighlight();
        return;
      }
      
      // Handle Backspace to delete matching closing bracket/quote
      if (e.key === 'Backspace') {
        const charBefore = value.charAt(start - 1);
        const charAfter = value.charAt(start);
        
        // Check if we're deleting an opening bracket/quote with matching closing one
        if (pairs[charBefore] && pairs[charBefore] === charAfter && start === end) {
          e.preventDefault();
          
          // Delete both characters
          const newValue = value.substring(0, start - 1) + value.substring(start + 1);
          codeEditor.value = newValue;
          
          // Move cursor back
          codeEditor.selectionStart = codeEditor.selectionEnd = start - 1;
          
          // Update UI
          updateLineNumbers();
          updateSyntaxHighlight();
          return;
        }
      }
    });
  }

  // Update on input and language change
  if (codeEditor) {
    codeEditor.addEventListener('input', () => {
      updateLineNumbers();
      updateSyntaxHighlight();
    });
    
    codeEditor.addEventListener('scroll', syncScroll);
    
    // Initial update
    updateLineNumbers();
    updateSyntaxHighlight();
  }
  
  if (languageSelect) {
    languageSelect.addEventListener('change', updateSyntaxHighlight);
  }

  // ---- COPY BUTTON ----
  const copyCodeBtn = document.getElementById("copyCodeBtn");
  
  if (copyCodeBtn && codeEditor) {
    copyCodeBtn.addEventListener("click", () => {
      const code = codeEditor.value;
      
      if (!code) {
        alert("⚠️ No code to copy!");
        return;
      }

      // Copy to clipboard
      navigator.clipboard.writeText(code).then(() => {
        // Visual feedback
        const originalText = copyCodeBtn.textContent;
        copyCodeBtn.textContent = "✓ Copied!";
        copyCodeBtn.style.background = "#10b981";
        
        setTimeout(() => {
          copyCodeBtn.textContent = originalText;
          copyCodeBtn.style.background = "";
        }, 2000);
      }).catch(err => {
        alert("Failed to copy: " + err);
      });
    });
  }
});
