document.addEventListener("DOMContentLoaded", () => {
  console.log("🚀 Compiler.js loaded successfully!");
  
  const runBtn = document.getElementById("runBtn");
  const explainBtn = document.getElementById("explainBtn");
  const debugBtn = document.getElementById("debugBtn");
  const saveBtn = document.getElementById("saveBtn");
  const shareBtn = document.getElementById("shareBtn");
  const newCodeBtn = document.getElementById("newCodeBtn");

  const codeEditor = document.getElementById("codeEditor");
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

  // ---- OLD TAB CODE (DISABLED - NO LONGER USED) ----
  // Tabs functionality removed per user request

  // ---- LOAD SHARED CODE FROM SESSION STORAGE ----
  const sharedCode = sessionStorage.getItem('sharedCode');
  const sharedLanguage = sessionStorage.getItem('sharedLanguage');
  const sharedTitle = sessionStorage.getItem('sharedTitle');
  
  if (sharedCode) {
    codeEditor.value = sharedCode;
    // Clear session storage after loading
    sessionStorage.removeItem('sharedCode');
    sessionStorage.removeItem('sharedLanguage');
    sessionStorage.removeItem('sharedTitle');
    
    updateSyntaxHighlight();
    updateLineNumbers();
    
    alert(`✅ Loaded shared code: "${sharedTitle}"`);
  }

  // ---- NEW CODE BUTTON ----
  if (newCodeBtn) {
    newCodeBtn.addEventListener('click', () => {
      const currentCode = codeEditor.value.trim();
      
      // If there's code, ask for confirmation
      if (currentCode && !confirm("Clear current code? (Unsaved changes will be lost)")) {
        return;
      }
      
      // Clear the editor
      codeEditor.value = "";
      updateSyntaxHighlight();
      updateLineNumbers();
      
      // Hide result sections
      if (resultSection) resultSection.classList.add("hidden");
      if (explanationSection) explanationSection.classList.add("hidden");
      if (debugSection) debugSection.classList.add("hidden");
    });
  }

  // ---- SAVE & SHARE ----
  if (saveBtn) {
    saveBtn.addEventListener('click', async () => {
      const code = codeEditor.value.trim();
      const languageText = languageSelect.options[languageSelect.selectedIndex].text;
      
      if (!code) {
        alert("⚠️ Please write some code before saving!");
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
          alert("✅ " + data.message + "\n\nView your saved projects in 📁 My Code");
        } else {
          alert("❌ " + (data.error || "Failed to save"));
        }
      } catch (err) {
        alert("❌ Error: " + err.message);
      }
    });
  }

  if (shareBtn) {
    shareBtn.addEventListener('click', async () => {
      const code = codeEditor.value.trim();
      const languageText = languageSelect.options[languageSelect.selectedIndex].text;
      
      if (!code) {
        alert("⚠️ Please write some code before sharing!");
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
          alert("✅ " + data.message + "\n\nLink copied to clipboard:\n" + data.share_link);
        } else {
          alert("❌ " + (data.error || "Failed to create share link"));
        }
      } catch (err) {
        alert("❌ Error: " + err.message);
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
      
      resultSection.classList.remove("hidden");
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
        if (language_id === 71 && inputPrompts.length > 0) {
          // Remove all the prompts that we already displayed
          inputPrompts.forEach(prompt => {
            // Remove the prompt text from output
            output = output.replace(prompt, '');
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
    explainBtn.addEventListener("click", async () => {
      console.log("Explain button clicked!");
      const code = codeEditor.value.trim();
      const languageText = languageSelect.options[languageSelect.selectedIndex].text || languageSelect.value;
      const languageValue = (languageText || "").toLowerCase();

      explanationSection.classList.remove("hidden");

      if (!code) {
        explanationBox.innerHTML = '<div style="padding: 2rem; text-align: center; color: #ffa500;">⚠️ Please write some code to explain!</div>';
        return;
      }

      // Show loading state
      const originalText = explainBtn.innerHTML;
      explainBtn.disabled = true;
      explainBtn.innerHTML = "⏳ Analyzing...";

      explanationBox.innerHTML = '<div style="padding: 2rem; text-align: center; color: #10a37f;">💡 Analyzing your code...<br>⏳ Please wait...</div>';

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
      const code = codeEditor.value.trim();
      const languageText = languageSelect.options[languageSelect.selectedIndex].text || "Python";
      
      if (!code) {
        alert("⚠️ Please write some code before debugging!");
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
      const code = codeEditor.value.trim();
      const languageText = languageSelect.options[languageSelect.selectedIndex].text || "Python";
      
      if (!code) {
        alert("⚠️ Please write some code before optimizing!");
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
    if (!codeEditor || !highlightedCode) {
      console.log("Missing elements:", { codeEditor: !!codeEditor, highlightedCode: !!highlightedCode });
      return;
    }
    
    const code = codeEditor.value;
    const languageId = languageSelect.value;
    const language = languageMap[languageId] || "python";
    
    // Update language class
    highlightedCode.className = `language-${language}`;
    
    // Set text content (this makes text visible even without Prism)
    highlightedCode.textContent = code;
    
    // Apply Prism highlighting if available
    if (window.Prism) {
      try {
        Prism.highlightElement(highlightedCode);
      } catch (e) {
        console.error("Prism highlighting error:", e);
      }
    } else {
      console.log("Prism not loaded yet");
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

  // ---- DOWNLOAD CODE BUTTON ----
  const downloadCodeBtn = document.getElementById("downloadCodeBtn");
  
  if (downloadCodeBtn && codeEditor && languageSelect) {
    downloadCodeBtn.addEventListener("click", () => {
      const code = codeEditor.value;
      
      if (!code) {
        alert("⚠️ No code to download!");
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
      
      // Show output if available
      if (data.output && resultBox && resultSection) {
        resultBox.textContent = data.output;
        resultSection.classList.remove('hidden');
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
});
