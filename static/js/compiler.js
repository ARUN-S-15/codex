document.addEventListener("DOMContentLoaded", () => {
  const languageSelect = document.getElementById("language");
  const codeInput = document.getElementById("code");
  const runBtn = document.getElementById("runBtn");
  const explainBtn = document.getElementById("explainBtn");
  const debugBtn = document.getElementById("debugBtn");
  const optimizeBtn = document.getElementById("optimizeBtn");
  const practiceBtn = document.getElementById("practiceBtn");
  const copyBtn = document.getElementById("copyBtn");
  const clearBtn = document.getElementById("clearBtn");
  const outputSection = document.getElementById("outputSection");
  const outputTitle = document.getElementById("outputTitle");
  const outputBox = document.getElementById("outputBox");
  const historyList = document.getElementById("historyList");
  const historyKey = "compilerHistory";

  function getHistory() {
    try {
      return JSON.parse(localStorage.getItem(historyKey)) || [];
    } catch (err) {
      return [];
    }
  }

  function saveHistory(entries) {
    localStorage.setItem(historyKey, JSON.stringify(entries.slice(0, 20)));
  }

  function renderHistory() {
    const entries = getHistory();
    historyList.innerHTML = "";
    if (!entries.length) {
      const li = document.createElement("li");
      li.className = "empty";
      li.textContent = "No history yet...";
      historyList.appendChild(li);
      return;
    }

    entries.forEach((item, index) => {
      const li = document.createElement("li");
      li.innerHTML = `
        <button class="history-item" data-index="${index}">
          <span>${item.language.toUpperCase()}</span>
          <small>${item.time}</small>
          <p>${item.code.slice(0, 120) || "(Empty)"}</p>
        </button>`;
      historyList.appendChild(li);
    });
  }

  function addToHistory(code, language) {
    if (!code.trim()) return;
    const entries = getHistory();
    entries.unshift({
      code,
      language,
      time: new Date().toLocaleTimeString()
    });
    saveHistory(entries);
    renderHistory();
  }

  historyList.addEventListener("click", (event) => {
    const target = event.target.closest(".history-item");
    if (!target) return;
    const index = parseInt(target.dataset.index, 10);
    const entries = getHistory();
    if (!entries[index]) return;
    codeInput.value = entries[index].code;
    languageSelect.value = entries[index].language;
  });

  function showOutput(title, content) {
    outputTitle.textContent = title;
    outputBox.textContent = content;
    outputSection.classList.add("visible");
  }

  async function postJSON(url, payload) {
    const response = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    if (!response.ok) {
      throw new Error(`${response.status} ${response.statusText}`);
    }
    return response.json();
  }

  const languageIdMap = {
    python: 71,
    javascript: 63,
    cpp: 54,
    c: 50,
    java: 62,
  };

  runBtn.addEventListener("click", async () => {
    const code = codeInput.value;
    const language = languageSelect.value;
    if (!code.trim()) {
      showOutput("Run", "⚠️ Please enter some code before running.");
      return;
    }

    showOutput("Run", "⏳ Submitting code to Judge0...");
    try {
      const result = await postJSON("/run", {
        code,
        language_id: languageIdMap[language] || 71,
      });
      showOutput("Run", result.output || "⚠️ No output returned.");
      addToHistory(code, language);
    } catch (err) {
      showOutput("Run", `❌ Error executing code:\n${err.message}`);
    }
  });

  explainBtn.addEventListener("click", async () => {
    const code = codeInput.value;
    if (!code.trim()) {
      showOutput("Explain", "⚠️ Please enter some code before requesting an explanation.");
      return;
    }

    showOutput("Explain", "🧠 Analyzing your code...");
    try {
      const result = await postJSON("/explain", {
        code,
        language: languageSelect.value,
      });
      showOutput("Explain", result.explanation || "⚠️ No explanation available.");
    } catch (err) {
      showOutput("Explain", `❌ Error explaining code:\n${err.message}`);
    }
  });

  debugBtn.addEventListener("click", async () => {
    const code = codeInput.value;
    if (!code.trim()) {
      showOutput("Debug", "⚠️ Please enter some code before debugging.");
      return;
    }
    showOutput("Debug", "🔍 Running static analysis...");
    try {
      const result = await postJSON("/debug", {
        code,
        language: languageSelect.value,
      });
      showOutput("Debug", result.debug || "✅ No issues found!");
      if (result.fixed_code) {
        localStorage.setItem("fixedCode", result.fixed_code);
      }
    } catch (err) {
      showOutput("Debug", `❌ Error debugging code:\n${err.message}`);
    }
  });

  optimizeBtn.addEventListener("click", () => {
    const code = codeInput.value;
    const language = languageSelect.value;
    if (!code.trim()) {
      alert("⚠️ Please enter some code before optimizing.");
      return;
    }
    localStorage.setItem("optimizeCode", code);
    localStorage.setItem("optimizeLanguage", language);
    window.location.href = "/optimizer";
  });

  practiceBtn.addEventListener("click", () => {
    const code = codeInput.value;
    const language = languageSelect.value;
    if (!code.trim()) {
      alert("⚠️ Please enter some code before sending to practice.");
      return;
    }
    localStorage.setItem("practiceCode", code);
    localStorage.setItem("practiceLanguage", language);
    window.location.href = "/practice";
  });

  copyBtn.addEventListener("click", () => {
    const code = codeInput.value;
    if (!code.trim()) return;
    navigator.clipboard.writeText(code).then(() => {
      copyBtn.textContent = "Copied!";
      setTimeout(() => (copyBtn.textContent = "Copy"), 1500);
    });
  });

  clearBtn.addEventListener("click", () => {
    codeInput.value = "";
    outputSection.classList.remove("visible");
  });

  document.getElementById("copyOutputBtn").addEventListener("click", () => {
    const text = outputBox.textContent;
    if (!text.trim()) return;
    navigator.clipboard.writeText(text).then(() => {
      const btn = document.getElementById("copyOutputBtn");
      btn.textContent = "Copied!";
      setTimeout(() => (btn.textContent = "Copy Output"), 1500);
    });
  });

  document.getElementById("clearHistoryBtn").addEventListener("click", () => {
    if (!confirm("Clear compiler history?")) return;
    localStorage.removeItem(historyKey);
    renderHistory();
  });

  (function preload() {
    const fixedCode = localStorage.getItem("fixedCode");
    if (fixedCode) {
      codeInput.value = fixedCode;
      localStorage.removeItem("fixedCode");
    }

    const incoming = localStorage.getItem("optimizeCode");
    if (incoming) {
      codeInput.value = incoming;
      const lang = localStorage.getItem("optimizeLanguage") || "python";
      languageSelect.value = lang;
      localStorage.removeItem("optimizeCode");
      localStorage.removeItem("optimizeLanguage");
    }

    const savedLanguage = localStorage.getItem("compilerLanguage");
    if (savedLanguage) {
      languageSelect.value = savedLanguage;
    }

    renderHistory();
  })();

  languageSelect.addEventListener("change", () => {
    localStorage.setItem("compilerLanguage", languageSelect.value);
  });
});document.addEventListener("DOMContentLoaded", () => {
  const runBtn = document.getElementById("runBtn");
  const explainBtn = document.getElementById("explainBtn");
  const debugBtn = document.getElementById("debugBtn");
  const optimizeBtn = document.getElementById("optimizeBtn");

  const codeEditor = document.getElementById("codeEditor");
  const languageSelect = document.getElementById("languageSelect");

  const resultBox = document.getElementById("resultBox");
  const explanationBox = document.getElementById("explanationBox");

  const resultSection = document.getElementById("resultSection");
  const explanationSection = document.getElementById("explanationSection");

  const languageMap = {
    "71": "python",
    "50": "c",
    "54": "cpp",
    "63": "javascript",
    "62": "java"
  };

  const modeMap = {
    "71": "python",
    "50": "text/x-csrc",
    "54": "text/x-c++src",
    "63": "javascript",
    "62": "text/x-java"
  };

  const editor = codeEditor
    ? CodeMirror.fromTextArea(codeEditor, {
        lineNumbers: true,
        mode: "python",
        theme: "dracula",
        indentUnit: 4,
        tabSize: 4,
        lineWrapping: true
      })
    : null;

  const getCurrentCode = () => (editor ? editor.getValue() : codeEditor.value || "");

  const applyEditorMode = () => {
    if (!editor || !languageSelect) return;
    const mode = modeMap[languageSelect.value] || "python";
    editor.setOption("mode", mode);
  };

  if (languageSelect) {
    applyEditorMode();
    languageSelect.addEventListener("change", applyEditorMode);
  }

  // ---- OPTIMIZE (navigate to optimizer with current code) ----
  if (optimizeBtn) {
    optimizeBtn.addEventListener("click", () => {
      const code = getCurrentCode().trim();
      const language_id = languageSelect.value;
      const language = languageMap[language_id] || "python";

      if (!code) {
        alert("⚠️ Please write some code before optimizing!");
        return;
      }

      // Save to localStorage so optimizer page can pick it up
      localStorage.setItem("optimizeCode", code);
      localStorage.setItem("optimizeLanguage", language);

      // Navigate to optimizer page
      window.location.href = "/optimizer";
    });
  }

  // ---- RUN CODE ----
  if (runBtn && resultSection && resultBox) {
    runBtn.addEventListener("click", async () => {
      const code = getCurrentCode().trim();
      const language_id = languageSelect.value;

      resultSection.classList.remove("hidden");

      if (!code) {
        resultBox.textContent = "⚠️ Please write some code before running!";
        return;
      }

      resultBox.textContent = "⏳ Running your code...";
      try {
        const response = await fetch("/run", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ code, language_id: parseInt(language_id) })
        });

        const data = await response.json();
        resultBox.textContent = data.output || "⚠️ No output returned.";
      } catch (err) {
        resultBox.textContent = "❌ Error: " + err.message;
      }
    });
  }

  // ---- EXPLAIN CODE ----
  if (explainBtn && explanationSection && explanationBox) {
    explainBtn.addEventListener("click", async () => {
      const code = getCurrentCode().trim();
      const language_id = languageSelect.value;
      const language = languageMap[language_id] || "python";

      explanationSection.classList.remove("hidden");

      if (!code) {
        explanationBox.textContent = "⚠️ Please write some code to explain!";
        return;
      }

      explanationBox.textContent = "💡 Analyzing your code...";
      try {
        const response = await fetch("/explain", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ code, language })
        });

        const data = await response.json();
        explanationBox.textContent = data.explanation || "⚠️ No explanation returned.";
      } catch (err) {
        explanationBox.textContent = "❌ Error: " + err.message;
      }
    });
  }

debugBtn.addEventListener("click", () => {
  const code = getCurrentCode().trim();
    const language_id = languageSelect.value;
    const language = languageMap[language_id] || "python"; // ✅ map numeric ID to language name

    if (!code) {
        alert("⚠️ Please write some code before debugging!");
        return;
    }

    // Store code and language in localStorage
    localStorage.setItem("debugCode", code);
    localStorage.setItem("debugLanguage", language);

    // Redirect to debugger page
    window.location.href = "/debugger";
});

  // ---- COPY CODE BUTTON ----
  const copyCodeBtn = document.getElementById("copyCodeBtn");
  if (copyCodeBtn) {
    copyCodeBtn.addEventListener("click", () => {
      const code = getCurrentCode().trim();
      
      if (!code) {
        alert("⚠️ No code to copy!");
        return;
      }

      // Copy to clipboard
      navigator.clipboard.writeText(code).then(() => {
        // Change button text temporarily
        const originalText = copyCodeBtn.textContent;
        copyCodeBtn.textContent = "✓ Copied!";
        copyCodeBtn.style.background = "#10a37f";
        
        setTimeout(() => {
          copyCodeBtn.textContent = originalText;
          copyCodeBtn.style.background = "transparent";
        }, 2000);
      }).catch((err) => {
        alert("❌ Failed to copy code: " + err.message);
      });
    });
  }

})