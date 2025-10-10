document.addEventListener("DOMContentLoaded", () => {
  const optimizeCode = localStorage.getItem("optimizeCode");
  const optimizeLanguage = localStorage.getItem("optimizeLanguage") || "python";

  const codeTextarea = document.getElementById("code");
  const languageSelect = document.getElementById("language");
  const optimizeBtn = document.getElementById("optimizeBtn");
  const copyBtn = document.getElementById("copyBtn");
  const copyOutputBtn = document.getElementById("copyOutputBtn");
  const outputBox = document.getElementById("output");

  if (languageSelect && optimizeLanguage) {
    languageSelect.value = optimizeLanguage;
  }

  if (codeTextarea && optimizeCode) {
    codeTextarea.value = optimizeCode;
    localStorage.removeItem("optimizeCode");
    localStorage.removeItem("optimizeLanguage");
  }

  if (optimizeBtn) {
    optimizeBtn.addEventListener("click", async () => {
      const code = codeTextarea.value;
      const language = languageSelect.value;
      if (!code.trim()) {
        outputBox.textContent = "⚠️ Please enter some code first.";
        return;
      }

      outputBox.textContent = "⏳ Optimizing your code...";

      try {
        const response = await fetch("/optimize", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ code, language })
        });
        const result = await response.json();
        const { optimized_code, suggestions, metrics } = result;

        const metricsText = metrics
          ? `Original lines: ${metrics.original_lines || '-'}\nOptimized lines: ${metrics.optimized_lines || '-'}\nReduction: ${metrics.reduction || 0}\n`
          : "";

        outputBox.textContent = [
          "// Optimization Summary",
          metricsText,
          suggestions || "",
          "\n// Optimized Code\n",
          optimized_code || code
        ].join("\n");
      } catch (error) {
        outputBox.textContent = "❌ Error optimizing code: " + error.message;
      }
    });
  }

  if (copyBtn) {
    copyBtn.addEventListener("click", () => {
      const code = codeTextarea.value;
      if (!code.trim()) return;
      navigator.clipboard.writeText(code).then(() => {
        copyBtn.textContent = "Copied!";
        setTimeout(() => (copyBtn.textContent = "Copy"), 1500);
      });
    });
  }

  if (copyOutputBtn) {
    copyOutputBtn.addEventListener("click", () => {
      const output = outputBox.textContent;
      if (!output.trim()) return;
      navigator.clipboard.writeText(output).then(() => {
        copyOutputBtn.textContent = "Copied!";
        setTimeout(() => (copyOutputBtn.textContent = "Copy"), 1500);
      });
    });
  }
});// static/js/script.js

document.addEventListener("DOMContentLoaded", () => {
  console.log("🌐 Main script loaded!");

  // Example: Smooth scroll for navigation links
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener("click", function (e) {
      e.preventDefault();
      document.querySelector(this.getAttribute("href")).scrollIntoView({
        behavior: "smooth"
      });
    });
  });

  // Example: Navbar animation
  const navbar = document.querySelector("nav");
  window.addEventListener("scroll", () => {
    if (window.scrollY > 50) {
      navbar.classList.add("scrolled");
    } else {
      navbar.classList.remove("scrolled");
    }
  });
});
