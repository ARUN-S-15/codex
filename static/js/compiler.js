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
    console.log("Run button listener attached successfully");
    runBtn.addEventListener("click", async () => {
      console.log("Run button clicked!");
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

      explanationBox.innerHTML = '<div style="padding: 2rem; text-align: center; color: #10a37f;">💡 Analyzing your code...<br>⏳ Please wait...</div>';

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
      } catch (err) {
        // Fallback: use local generator
        const localExplanation = generateExplanation(code, languageText);
        explanationBox.innerHTML = '<div class="explanation-card" style="border-left-color: #ff5459;"><div class="explanation-title">⚠️ Server Unavailable</div><div class="explanation-content">Using local explanation generator.</div></div>' + 
          formatExplanation(localExplanation);
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
      
      // Navigate to optimizer page
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
