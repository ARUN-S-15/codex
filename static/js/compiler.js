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
          body: JSON.stringify({ code, language_id })
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
  if (explainBtn && explanationSection && explanationBox) {
    explainBtn.addEventListener("click", async () => {
      const code = codeEditor.value.trim();
      const language = languageSelect.value;

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
        console.log("Explain response:", data);
        explanationBox.textContent = data.explanation || "⚠️ No explanation returned.";
      } catch (err) {
        explanationBox.textContent = "❌ Error: " + err.message;
      }
    });
  }

  // ---- DEBUG CODE ----
  if (debugBtn && debugSection && debugBox) {
    debugBtn.addEventListener("click", async () => {
      const code = codeEditor.value.trim();
      const language = languageSelect.value;

      debugSection.classList.remove("hidden");

      debugBox.textContent = "🪲 Debugging your code...";
      try {
        const response = await fetch("/debug", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ code, language })
        });

        const data = await response.json();
        console.log("Debug response:", data);
        debugBox.textContent = data.debug || "✅ No syntax errors found!";
      } catch (err) {
        debugBox.textContent = "❌ Error: " + err.message;
      }
    });
  }
});
