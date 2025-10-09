// AI Code Explainer Application Logic
class CodeExplainer {
    constructor() {
        this.currentLanguage = 'javascript';
        this.analysisTimeout = null;
        this.sampleCodes = {
            "javascript": "function calculateSum(a, b) {\n  let result = a + b\n  console.log('Sum is: ' + result\n  return result\n}",
            "python": "def calculate_average(numbers):\nif len(numbers) == 0:\n    return 0\n  total = sum(numbers)\n  return total / len(numbers)",
            "html": "<!DOCTYPE html>\n<html>\n<head>\n  <title>My Page</title>\n<body>\n  <h1>Welcome to My Site</h1>\n  <p>This is a paragraph.\n  <div class='content'>\n    <span>Content here</span>\n  </div>\n</body>\n</html>",
            "java": "public class Calculator {\n  public static void main(String[] args) {\n    int a = 10;\n    int b = 20\n    System.out.println(\"Sum: \" + (a + b);\n  }\n}",
            "cpp": "#include <iostream>\nusing namespace std;\n\nint main() {\n  int x = 5;\n  int y = 10\n  cout << \"Sum: \" << x + y << endl\n  return 0;\n"
        };
        
        this.errorPatterns = {
            javascript: [
                { pattern: /console\.log\([^)]*(?<!;)\s*$/m, message: "Missing semicolon after console.log statement", severity: "error" },
                { pattern: /\{[^}]*$/m, message: "Missing closing brace '}' ", severity: "error" },
                { pattern: /\([^)]*$/m, message: "Missing closing parenthesis ')'", severity: "error" },
                { pattern: /let\s+\w+\s*(?!\=)/m, message: "Variable declared but not initialized", severity: "warning" },
                { pattern: /function\s+\w+\([^)]*\)\s*\{[^}]*$/m, message: "Function missing closing brace", severity: "error" }
            ],
            python: [
                { pattern: /^\s*if\s+.*(?<!:)\s*$/m, message: "Missing colon ':' after if statement", severity: "error" },
                { pattern: /^\s*def\s+\w+\([^)]*\)(?<!:)\s*$/m, message: "Missing colon ':' after function definition", severity: "error" },
                { pattern: /^[a-zA-Z]/m, message: "Potential indentation error - Python requires proper indentation", severity: "error" },
                { pattern: /^\s*for\s+.*(?<!:)\s*$/m, message: "Missing colon ':' after for statement", severity: "error" }
            ],
            html: [
                { pattern: /<(p|div|span|h[1-6])[^>]*>(?![^<]*<\/\1>)/i, message: "Missing closing tag", severity: "error" },
                { pattern: /<\w+[^>]*(?<!\/|>)$/m, message: "Unclosed HTML tag", severity: "error" },
                { pattern: /<title[^>]*>(?![^<]*<\/title>)/i, message: "Missing closing </title> tag", severity: "warning" }
            ],
            java: [
                { pattern: /int\s+\w+\s*=\s*\d+(?!;)/m, message: "Missing semicolon after variable declaration", severity: "error" },
                { pattern: /System\.out\.println\([^)]*(?<!;)\s*$/m, message: "Missing semicolon after println statement", severity: "error" },
                { pattern: /\{[^}]*$/m, message: "Missing closing brace '}'", severity: "error" }
            ],
            cpp: [
                { pattern: /int\s+\w+\s*=\s*\d+(?!;)/m, message: "Missing semicolon after variable declaration", severity: "error" },
                { pattern: /cout\s*<<.*(?<!;)\s*$/m, message: "Missing semicolon after cout statement", severity: "error" },
                { pattern: /#include\s*<[^>]*(?<!>)/m, message: "Missing closing bracket '>' in include statement", severity: "error" }
            ]
        };
        
        this.init();
    }
    
    init() {
        this.bindEvents();
        this.updateLineNumbers();
        this.updateLanguageIndicator();
    }
    
    bindEvents() {
        // DOM Elements
        this.codeEditor = document.getElementById('codeEditor');
        this.languageSelect = document.getElementById('languageSelect');
        this.analyzeBtn = document.getElementById('analyzeBtn');
        this.clearBtn = document.getElementById('clearBtn');
        this.loadSampleBtn = document.getElementById('loadSampleBtn');
        this.copyBtn = document.getElementById('copyBtn');
        this.exportBtn = document.getElementById('exportBtn');
        this.lineNumbers = document.getElementById('lineNumbers');
        this.languageIndicator = document.getElementById('languageIndicator');
        
        // Tab elements
        this.tabButtons = document.querySelectorAll('.tab-button');
        this.tabPanels = document.querySelectorAll('.tab-panel');
        
        // Event listeners
        this.codeEditor.addEventListener('input', () => {
            this.updateLineNumbers();
            this.debouncedAnalysis();
        });
        
        this.codeEditor.addEventListener('scroll', () => {
            this.lineNumbers.scrollTop = this.codeEditor.scrollTop;
        });
        
        this.languageSelect.addEventListener('change', (e) => {
            this.currentLanguage = e.target.value;
            this.updateLanguageIndicator();
        });
        
        this.analyzeBtn.addEventListener('click', () => {
            this.analyzeCode();
        });
        
        this.clearBtn.addEventListener('click', () => {
            this.clearEditor();
        });
        
        this.loadSampleBtn.addEventListener('click', () => {
            this.loadSampleCode();
        });
        
        this.copyBtn.addEventListener('click', () => {
            this.copyCode();
        });
        
        this.exportBtn.addEventListener('click', () => {
            this.exportReport();
        });
        
        // Tab switching
        this.tabButtons.forEach(button => {
            button.addEventListener('click', () => {
                this.switchTab(button.dataset.tab);
            });
        });
        
        // Notification close
        const notificationClose = document.getElementById('notificationClose');
        if (notificationClose) {
            notificationClose.addEventListener('click', () => {
                this.hideNotification();
            });
        }
    }
    
    updateLineNumbers() {
        const lines = this.codeEditor.value.split('\n');
        const lineNumbersArray = [];
        for (let i = 1; i <= lines.length; i++) {
            lineNumbersArray.push(i);
        }
        this.lineNumbers.textContent = lineNumbersArray.join('\n');
    }
    
    updateLanguageIndicator() {
        if (this.languageIndicator) {
            const languageNames = {
                javascript: 'JavaScript',
                python: 'Python',
                html: 'HTML/CSS',
                java: 'Java',
                cpp: 'C++'
            };
            this.languageIndicator.textContent = languageNames[this.currentLanguage] || 'JavaScript';
        }
    }
    
    debouncedAnalysis() {
        clearTimeout(this.analysisTimeout);
        this.analysisTimeout = setTimeout(() => {
            this.analyzeCode(false);
        }, 1000);
    }
    
    analyzeCode(showNotification = true) {
        const code = this.codeEditor.value.trim();
        if (!code) {
            this.clearAnalysis();
            return;
        }
        
        const errors = this.detectErrors(code);
        const explanations = this.generateExplanations(code);
        const suggestions = this.generateSuggestions(code, errors);
        const output = this.simulateOutput(code);
        
        this.displayErrors(errors);
        this.displayExplanations(explanations);
        this.displaySuggestions(suggestions);
        this.displayOutput(output);
        
        if (showNotification) {
            this.showNotification('Code analysis completed!');
        }
    }
    
    detectErrors(code) {
        const errors = [];
        const lines = code.split('\n');
        const patterns = this.errorPatterns[this.currentLanguage] || [];
        
        patterns.forEach(({ pattern, message, severity }) => {
            const matches = code.matchAll(new RegExp(pattern.source, pattern.flags + 'g'));
            for (const match of matches) {
                const lineIndex = code.substring(0, match.index).split('\n').length - 1;
                errors.push({
                    line: lineIndex + 1,
                    message,
                    severity,
                    code: lines[lineIndex] || '',
                    index: match.index
                });
            }
        });
        
        return errors;
    }
    
    generateExplanations(code) {
        const lines = code.split('\n');
        const explanations = [];
        
        lines.forEach((line, index) => {
            const trimmedLine = line.trim();
            if (!trimmedLine) return;
            
            let explanation = this.explainLine(trimmedLine, this.currentLanguage);
            if (explanation) {
                explanations.push({
                    line: index + 1,
                    code: line,
                    explanation
                });
            }
        });
        
        return explanations;
    }
    
    explainLine(line, language) {
        const explanations = {
            javascript: [
                { pattern: /function\s+(\w+)/, explanation: "Defines a function named '$1' that can be called with parameters" },
                { pattern: /let\s+(\w+)/, explanation: "Declares a variable '$1' with block scope" },
                { pattern: /const\s+(\w+)/, explanation: "Declares a constant '$1' that cannot be reassigned" },
                { pattern: /console\.log/, explanation: "Outputs data to the browser console for debugging" },
                { pattern: /return\s+/, explanation: "Returns a value from the function and exits the function" },
                { pattern: /if\s*\(/, explanation: "Conditional statement that executes code based on a condition" },
                { pattern: /for\s*\(/, explanation: "Loop that repeats code for a specified number of iterations" }
            ],
            python: [
                { pattern: /def\s+(\w+)/, explanation: "Defines a function named '$1' that can accept parameters" },
                { pattern: /if\s+/, explanation: "Conditional statement that executes code if the condition is true" },
                { pattern: /print\(/, explanation: "Outputs data to the console or terminal" },
                { pattern: /return\s+/, explanation: "Returns a value from the function" },
                { pattern: /len\(/, explanation: "Returns the number of items in a sequence or collection" },
                { pattern: /sum\(/, explanation: "Returns the sum of all numeric values in an iterable" }
            ],
            html: [
                { pattern: /<!DOCTYPE html>/, explanation: "Declares this document as HTML5" },
                { pattern: /<html>/, explanation: "Root element of the HTML document" },
                { pattern: /<head>/, explanation: "Contains metadata about the HTML document" },
                { pattern: /<body>/, explanation: "Contains the visible content of the HTML document" },
                { pattern: /<title>/, explanation: "Sets the title displayed in the browser tab" },
                { pattern: /<h[1-6]>/, explanation: "Creates a heading element for structuring content" },
                { pattern: /<p>/, explanation: "Creates a paragraph of text" },
                { pattern: /<div>/, explanation: "Creates a generic container for grouping elements" }
            ],
            java: [
                { pattern: /public\s+class/, explanation: "Declares a public class accessible from other packages" },
                { pattern: /public\s+static\s+void\s+main/, explanation: "Main method - entry point of the Java program" },
                { pattern: /int\s+(\w+)/, explanation: "Declares an integer variable named '$1'" },
                { pattern: /System\.out\.println/, explanation: "Prints text to the console followed by a new line" },
                { pattern: /String\[\]\s+args/, explanation: "Command line arguments passed to the program" }
            ],
            cpp: [
                { pattern: /#include\s*<iostream>/, explanation: "Includes input/output stream functionality" },
                { pattern: /using\s+namespace\s+std/, explanation: "Allows use of standard library functions without std:: prefix" },
                { pattern: /int\s+main\(\)/, explanation: "Main function - entry point of the C++ program" },
                { pattern: /int\s+(\w+)/, explanation: "Declares an integer variable named '$1'" },
                { pattern: /cout\s*<</, explanation: "Outputs data to the console" },
                { pattern: /endl/, explanation: "Inserts a new line and flushes the output buffer" }
            ]
        };
        
        const langExplanations = explanations[language] || [];
        for (const { pattern, explanation } of langExplanations) {
            const match = line.match(pattern);
            if (match) {
                return explanation.replace(/\$(\d+)/g, (_, num) => match[parseInt(num)] || '');
            }
        }
        
        return "Code statement performing an operation";
    }
    
    generateSuggestions(code, errors) {
        const suggestions = [];
        
        // General suggestions based on errors
        if (errors.some(e => e.message.includes('semicolon'))) {
            suggestions.push({
                title: "Add Missing Semicolons",
                description: "Always end statements with semicolons to avoid syntax errors and improve code readability.",
                code: "// Good practice:\nlet x = 5;\nconsole.log(x);"
            });
        }
        
        if (errors.some(e => e.message.includes('brace') || e.message.includes('parenthesis'))) {
            suggestions.push({
                title: "Check Bracket Matching",
                description: "Ensure all opening brackets, braces, and parentheses have corresponding closing ones.",
                code: "// Make sure brackets match:\nif (condition) {\n    // code here\n}"
            });
        }
        
        // Language-specific suggestions
        if (this.currentLanguage === 'javascript') {
            if (code.includes('var ')) {
                suggestions.push({
                    title: "Use 'let' or 'const' instead of 'var'",
                    description: "Modern JavaScript prefers 'let' for variables and 'const' for constants to avoid scope issues.",
                    code: "// Better:\nconst PI = 3.14159;\nlet counter = 0;"
                });
            }
        }
        
        if (this.currentLanguage === 'python') {
            if (code.includes('    ') === false && code.includes('\t') === false) {
                suggestions.push({
                    title: "Use Proper Indentation",
                    description: "Python requires consistent indentation (4 spaces recommended) to define code blocks.",
                    code: "def example():\n    if True:\n        print('Properly indented')"
                });
            }
        }
        
        // Add general code quality suggestions
        suggestions.push({
            title: "Add Comments",
            description: "Include comments to explain complex logic and improve code maintainability.",
            code: "// This function calculates the area of a circle\nfunction calculateArea(radius) {\n    return Math.PI * radius * radius;\n}"
        });
        
        return suggestions;
    }
    
    simulateOutput(code) {
        const outputs = {
            javascript: {
                success: "Code compiled successfully!\n\nExpected Output:\nSum is: 30\n30\n\nExecution completed in 0.045ms",
                error: "Compilation Error:\nSyntaxError: Unexpected token\n    at line 3:25\n\nPlease fix the syntax errors and try again."
            },
            python: {
                success: "Code executed successfully!\n\nExpected Output:\n6.666666666666667\n\nExecution completed in 0.023ms",
                error: "IndentationError: expected an indented block\n    at line 2\n\nPlease fix the indentation and try again."
            },
            html: {
                success: "HTML validated successfully!\n\nDocument Structure:\n- DOCTYPE declaration: ✓\n- HTML tags: ✓\n- Head section: ✓\n- Body content: ✓",
                error: "HTML Validation Error:\nUnclosed tag detected\n    at line 8\n\nPlease close all HTML tags properly."
            },
            java: {
                success: "Compilation successful!\n\nExpected Output:\nSum: 30\n\nProgram executed successfully.",
                error: "Compilation Error:\nError: ';' expected\n    at line 4\n\nPlease add missing semicolons."
            },
            cpp: {
                success: "Compilation successful!\n\nExpected Output:\nSum: 15\n\nProgram terminated with exit code 0",
                error: "Compilation Error:\nError: expected ';' before 'cout'\n    at line 6\n\nPlease fix syntax errors."
            }
        };
        
        const errors = this.detectErrors(code);
        const hasErrors = errors.some(e => e.severity === 'error');
        const langOutput = outputs[this.currentLanguage] || outputs.javascript;
        
        return {
            success: !hasErrors,
            content: hasErrors ? langOutput.error : langOutput.success
        };
    }
    
    displayErrors(errors) {
        const errorsTab = document.getElementById('errorsTab');
        if (errors.length === 0) {
            errorsTab.innerHTML = `
                <div class="analysis-placeholder">
                    <div class="placeholder-icon">✅</div>
                    <p>No errors detected in your code!</p>
                </div>
            `;
            return;
        }
        
        const errorsHtml = errors.map(error => `
            <div class="error-item" data-line="${error.line}">
                <div class="error-header">
                    <span class="error-icon">❌</span>
                    <span class="error-line">Line ${error.line}</span>
                    <span class="error-title">${error.message}</span>
                </div>
                <div class="error-description">
                    <code>${error.code.trim()}</code>
                </div>
            </div>
        `).join('');
        
        errorsTab.innerHTML = errorsHtml;
        
        // Add click handlers for error highlighting
        errorsTab.querySelectorAll('.error-item').forEach(item => {
            item.addEventListener('click', () => {
                this.highlightLine(parseInt(item.dataset.line));
            });
        });
    }
    
    displayExplanations(explanations) {
        const explanationTab = document.getElementById('explanationTab');
        if (explanations.length === 0) {
            explanationTab.innerHTML = `
                <div class="analysis-placeholder">
                    <div class="placeholder-icon">📖</div>
                    <p>No code to explain. Add some code to get detailed explanations.</p>
                </div>
            `;
            return;
        }
        
        const explanationsHtml = explanations.map(exp => `
            <div class="explanation-item">
                <div class="explanation-line">Line ${exp.line}</div>
                <div class="explanation-code">${exp.code.trim()}</div>
                <div class="explanation-text">${exp.explanation}</div>
            </div>
        `).join('');
        
        explanationTab.innerHTML = explanationsHtml;
    }
    
    displaySuggestions(suggestions) {
        const suggestionsTab = document.getElementById('suggestionsTab');
        if (suggestions.length === 0) {
            suggestionsTab.innerHTML = `
                <div class="analysis-placeholder">
                    <div class="placeholder-icon">💡</div>
                    <p>No suggestions available. Your code looks good!</p>
                </div>
            `;
            return;
        }
        
        const suggestionsHtml = suggestions.map(suggestion => `
            <div class="suggestion-item">
                <div class="suggestion-header">
                    <span class="suggestion-icon">💡</span>
                    <span class="suggestion-title">${suggestion.title}</span>
                </div>
                <div class="suggestion-description">${suggestion.description}</div>
                <div class="suggestion-code">${suggestion.code}</div>
            </div>
        `).join('');
        
        suggestionsTab.innerHTML = suggestionsHtml;
    }
    
    displayOutput(output) {
        const outputTab = document.getElementById('outputTab');
        const statusClass = output.success ? 'success' : 'error';
        const icon = output.success ? '✅' : '❌';
        const title = output.success ? 'Execution Result' : 'Compilation Error';
        
        outputTab.innerHTML = `
            <div class="output-section">
                <div class="output-header">
                    <span class="output-icon">${icon}</span>
                    <span class="output-title">${title}</span>
                </div>
                <div class="output-content">${output.content}</div>
            </div>
        `;
    }
    
    clearAnalysis() {
        document.getElementById('errorsTab').innerHTML = `
            <div class="analysis-placeholder">
                <div class="placeholder-icon">🔍</div>
                <p>Click "Analyze Code" to detect errors and issues in your code</p>
            </div>
        `;
        document.getElementById('explanationTab').innerHTML = `
            <div class="analysis-placeholder">
                <div class="placeholder-icon">📖</div>
                <p>Code explanation will appear here after analysis</p>
            </div>
        `;
        document.getElementById('suggestionsTab').innerHTML = `
            <div class="analysis-placeholder">
                <div class="placeholder-icon">💡</div>
                <p>Code suggestions and improvements will be shown here</p>
            </div>
        `;
        document.getElementById('outputTab').innerHTML = `
            <div class="analysis-placeholder">
                <div class="placeholder-icon">▶️</div>
                <p>Simulated compilation and execution results will appear here</p>
            </div>
        `;
    }
    
    switchTab(tabName) {
        // Update tab buttons
        this.tabButtons.forEach(btn => {
            btn.classList.toggle('active', btn.dataset.tab === tabName);
        });
        
        // Update tab panels
        this.tabPanels.forEach(panel => {
            panel.classList.toggle('active', panel.id === tabName + 'Tab');
        });
    }
    
    highlightLine(lineNumber) {
        const lines = this.codeEditor.value.split('\n');
        const start = lines.slice(0, lineNumber - 1).reduce((acc, line) => acc + line.length + 1, 0);
        const end = start + lines[lineNumber - 1].length;
        
        this.codeEditor.focus();
        this.codeEditor.setSelectionRange(start, end);
    }
    
    loadSampleCode() {
        const sampleCode = this.sampleCodes[this.currentLanguage];
        this.codeEditor.value = sampleCode;
        this.updateLineNumbers();
        this.showNotification(`Sample ${this.currentLanguage} code loaded!`);
    }
    
    clearEditor() {
        this.codeEditor.value = '';
        this.updateLineNumbers();
        this.clearAnalysis();
        this.showNotification('Editor cleared!');
    }
    
    copyCode() {
        if (!this.codeEditor.value.trim()) {
            this.showNotification('No code to copy!', 'warning');
            return;
        }
        
        navigator.clipboard.writeText(this.codeEditor.value).then(() => {
            this.showNotification('Code copied to clipboard!');
        }).catch(() => {
            this.showNotification('Failed to copy code', 'error');
        });
    }
    
    exportReport() {
        const code = this.codeEditor.value.trim();
        if (!code) {
            this.showNotification('No code to export!', 'warning');
            return;
        }
        
        const errors = this.detectErrors(code);
        const timestamp = new Date().toISOString();
        
        const report = `
AI Code Explainer Analysis Report
Generated: ${timestamp}
Language: ${this.currentLanguage.toUpperCase()}

CODE:
${'-'.repeat(50)}
${code}
${'-'.repeat(50)}

ANALYSIS RESULTS:
${errors.length === 0 ? 'No errors detected! ✅' : `${errors.length} issue(s) found:`}
${errors.map(e => `- Line ${e.line}: ${e.message}`).join('\n')}

END OF REPORT
        `.trim();
        
        const blob = new Blob([report], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `code-analysis-${this.currentLanguage}-${Date.now()}.txt`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        this.showNotification('Analysis report exported!');
    }
    
    showNotification(message, type = 'success') {
        const notification = document.getElementById('notification');
        const notificationText = document.getElementById('notificationText');
        
        notificationText.textContent = message;
        notification.className = `notification ${type}`;
        
        setTimeout(() => {
            this.hideNotification();
        }, 3000);
    }
    
    hideNotification() {
        const notification = document.getElementById('notification');
        notification.classList.add('hidden');
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new CodeExplainer();
});