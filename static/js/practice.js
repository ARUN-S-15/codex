// ============================================
// PRACTICE PAGE - SIMPLE CUSTOM INTERFACE
// - Lightweight replacement for the heavy LeetCode-style script
// - Provides: CodeMirror editor, Load problem, Run (visible tests), Submit (all tests), Reward banner
// - Uses existing backend endpoints: /submit-code (POST) and /get-result?token= (GET)
// ============================================

document.addEventListener('DOMContentLoaded', () => {
  // Minimal CodeMirror setup
  const textarea = document.getElementById('codeEditor');
  const languageSelect = document.getElementById('languageSelect');
  const runBtn = document.getElementById('runBtn');
  const submitBtn = document.getElementById('submitBtn');
  const consoleOutput = document.getElementById('consoleOutput');

  const languageModeMap = {
    'Python': 'python',
    'C': 'text/x-csrc',
    'C++': 'text/x-c++src',
    'Java': 'text/x-java'
  };

  const languageMap = {
    'Python': { id: 71, ext: 'python' },
    'C': { id: 50, ext: 'c' },
    'C++': { id: 54, ext: 'cpp' },
    'Java': { id: 62, ext: 'java' }
  };

  const editor = CodeMirror.fromTextArea(textarea, {
    mode: 'python',
    theme: 'monokai',
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
      
      // Run shortcuts
      "F9": (cm) => { 
        if (runBtn && !runBtn.disabled) { 
          runBtn.click(); 
          return false; 
        } 
      },
      "Ctrl-Enter": (cm) => { 
        if (runBtn && !runBtn.disabled) { 
          runBtn.click(); 
        }
        return false; 
      },
      
      // Submit shortcut
      "Ctrl-S": (cm) => { 
        if (submitBtn && !submitBtn.disabled) { 
          submitBtn.click(); 
        }
        return false; 
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
      
      // Find
      "Ctrl-F": "find",
      "Cmd-F": "find",
      
      // Replace
      "Ctrl-H": "replace",
      "Cmd-Alt-F": "replace"
    }
  });

  // Lightweight problems dataset (copied from backup, trimmed where appropriate)
  const problems = {
    1: {
      title: 'Two Sum',
      desc: 'Given an array of integers and a target sum, return indices of two numbers that add up to the target.',
      difficulty: 'easy',
      example: 'Input: nums = [2, 7, 11, 15], target = 9\nOutput: [0, 1]',
      constraints: ['2 ≤ nums.length ≤ 10^4', 'Each input has exactly one solution'],
      testCases: [
        { input: '2 7 11 15\n9', output: '0 1', hidden: false },
        { input: '3 2 4\n6', output: '1 2', hidden: false },
        { input: '3 3\n6', output: '0 1', hidden: false },
        { input: '-1 -2 -3 -4 -5\n-8', output: '2 4', hidden: true }
      ],
      starterCode: {
        python: '# Enter your code here\nnums = list(map(int, input().split()))\ntarget = int(input())\n\n# Your solution here\n',
        c: '#include <stdio.h>\nint main() {\n    // Your code here\n    return 0;\n}',
        cpp: '#include <iostream>\nusing namespace std;\nint main() {\n    // Your code here\n    return 0;\n}',
        java: 'import java.util.*;\npublic class Solution {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        // Your code here\n    }\n}'
      }
    },
    2: {
      title: 'Reverse String',
      desc: 'Write a function that reverses a given string.',
      difficulty: 'easy',
      example: 'Input: "hello"\nOutput: "olleh"',
      constraints: ['1 ≤ string length ≤ 1000'],
      testCases: [
        { input: 'hello', output: 'olleh', hidden: false },
        { input: 'world', output: 'dlrow', hidden: false },
        { input: 'racecar', output: 'racecar', hidden: false },
        { input: 'Python Programming', output: 'gnimmargorP nohtyP', hidden: true }
      ],
      starterCode: {
        python: '# Enter your code here\ns = input()\n# Reverse the string and print\n',
        c: '#include <stdio.h>\n#include <string.h>\nint main() {\n    char s[1001];\n    scanf("%[^\\n]", s);\n    // Your code here\n    return 0;\n}',
        cpp: '#include <iostream>\n#include <string>\nusing namespace std;\nint main() {\n    string s;\n    getline(cin, s);\n    // Your code here\n    return 0;\n}',
        java: 'import java.util.*;\npublic class Solution {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        String s = sc.nextLine();\n        // Your code here\n    }\n}'
      }
    },
    3: {
      title: 'Fibonacci Sequence',
      desc: 'Generate the first n Fibonacci numbers.',
      difficulty: 'easy',
      example: 'Input: 5\nOutput: 0 1 1 2 3',
      constraints: ['1 ≤ n ≤ 50'],
      testCases: [
        { input: '5', output: '0 1 1 2 3', hidden: false },
        { input: '8', output: '0 1 1 2 3 5 8 13', hidden: false },
        { input: '1', output: '0', hidden: false },
        { input: '10', output: '0 1 1 2 3 5 8 13 21 34', hidden: true }
      ],
      starterCode: {
        python: '# Enter your code here\nn = int(input())\n# Generate and print first n Fibonacci numbers\n',
        c: '#include <stdio.h>\nint main() {\n    int n;\n    scanf("%d", &n);\n    // Your code here\n    return 0;\n}',
        cpp: '#include <iostream>\nusing namespace std;\nint main() {\n    int n;\n    cin >> n;\n    // Your code here\n    return 0;\n}',
        java: 'import java.util.*;\npublic class Solution {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        int n = sc.nextInt();\n        // Your code here\n    }\n}'
      }
    },
    4: {
      title: 'Palindrome Check',
      desc: 'Check if a given string is a palindrome (reads same forwards and backwards).',
      difficulty: 'easy',
      example: 'Input: "racecar"\nOutput: true',
      constraints: ['Case insensitive', 'Ignore spaces and punctuation'],
      testCases: [
        { input: 'racecar', output: 'true', hidden: false },
        { input: 'hello', output: 'false', hidden: false },
        { input: 'A man a plan a canal Panama', output: 'true', hidden: false },
        { input: 'Was it a car or a cat I saw', output: 'true', hidden: true }
      ],
      starterCode: {
        python: '# Enter your code here\ns = input()\n# Check if palindrome and print true/false\n',
        c: '#include <stdio.h>\n#include <string.h>\n#include <ctype.h>\nint main() {\n    char s[1001];\n    scanf("%[^\\n]", s);\n    // Your code here\n    return 0;\n}',
        cpp: '#include <iostream>\n#include <string>\n#include <algorithm>\nusing namespace std;\nint main() {\n    string s;\n    getline(cin, s);\n    // Your code here\n    return 0;\n}',
        java: 'import java.util.*;\npublic class Solution {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        String s = sc.nextLine();\n        // Your code here\n    }\n}'
      }
    },
    5: {
      title: 'Binary Search',
      desc: 'Implement binary search algorithm on a sorted array. Return the index of target element or -1 if not found.',
      difficulty: 'medium',
      example: 'Input: arr = [1, 3, 5, 7, 9], target = 5\nOutput: 2',
      constraints: ['Array is sorted in ascending order', 'Return -1 if not found', '1 ≤ array length ≤ 10^4'],
      testCases: [
        { input: '1 3 5 7 9\n5', output: '2', hidden: false },
        { input: '1 3 5 7 9\n6', output: '-1', hidden: false },
        { input: '2 4 6 8 10 12\n12', output: '5', hidden: false },
        { input: '10 20 30 40 50\n10', output: '0', hidden: true }
      ],
      starterCode: {
        python: '# Enter your code here\narr = list(map(int, input().split()))\ntarget = int(input())\n# Implement binary search\n',
        c: '#include <stdio.h>\nint main() {\n    int arr[10000], n = 0, target;\n    while(scanf("%d", &arr[n]) == 1) n++;\n    n--; target = arr[n];\n    // Your code here\n    return 0;\n}',
        cpp: '#include <iostream>\n#include <vector>\nusing namespace std;\nint main() {\n    vector<int> arr;\n    int x, target;\n    while(cin >> x) arr.push_back(x);\n    target = arr.back(); arr.pop_back();\n    // Your code here\n    return 0;\n}',
        java: 'import java.util.*;\npublic class Solution {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        String[] nums = sc.nextLine().split(" ");\n        int target = sc.nextInt();\n        // Your code here\n    }\n}'
      }
    },
    6: {
      title: 'Merge Sorted Arrays',
      desc: 'Merge two sorted arrays into one sorted array.',
      difficulty: 'medium',
      example: 'Input: arr1 = [1, 3, 5], arr2 = [2, 4, 6]\nOutput: [1, 2, 3, 4, 5, 6]',
      constraints: ['Both arrays are sorted', 'Handle empty arrays', '0 ≤ array length ≤ 1000'],
      testCases: [
        { input: '1 3 5\n2 4 6', output: '1 2 3 4 5 6', hidden: false },
        { input: '1 2 3\n4 5 6', output: '1 2 3 4 5 6', hidden: false },
        { input: '5\n1 2 3', output: '1 2 3 5', hidden: false },
        { input: '\n1 2 3', output: '1 2 3', hidden: true }
      ],
      starterCode: {
        python: '# Enter your code here\narr1_input = input()\narr1 = list(map(int, arr1_input.split())) if arr1_input else []\narr2 = list(map(int, input().split()))\n# Merge arrays\n',
        c: '#include <stdio.h>\nint main() {\n    // Your code here\n    return 0;\n}',
        cpp: '#include <iostream>\n#include <vector>\nusing namespace std;\nint main() {\n    // Your code here\n    return 0;\n}',
        java: 'import java.util.*;\npublic class Solution {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        // Your code here\n    }\n}'
      }
    },
    7: {
      title: 'Valid Parentheses',
      desc: 'Check if a string has valid matching parentheses, brackets, and braces.',
      difficulty: 'medium',
      example: 'Input: "({[]})"\nOutput: true',
      constraints: ['Only (), {}, [] characters', 'Must close in correct order'],
      testCases: [
        { input: '()', output: 'true', hidden: false },
        { input: '({[]})', output: 'true', hidden: false },
        { input: '(]', output: 'false', hidden: false },
        { input: '([)]', output: 'false', hidden: true }
      ],
      starterCode: {
        python: '# Enter your code here\ns = input()\n# Check if valid parentheses\n',
        c: '#include <stdio.h>\n#include <string.h>\nint main() {\n    char s[1001];\n    scanf("%s", s);\n    // Your code here\n    return 0;\n}',
        cpp: '#include <iostream>\n#include <string>\n#include <stack>\nusing namespace std;\nint main() {\n    string s;\n    cin >> s;\n    // Your code here\n    return 0;\n}',
        java: 'import java.util.*;\npublic class Solution {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        String s = sc.next();\n        // Your code here\n    }\n}'
      }
    },
    8: {
      title: 'Longest Substring',
      desc: 'Find the length of the longest substring without repeating characters.',
      difficulty: 'medium',
      example: 'Input: "abcabcbb"\nOutput: 3\nExplanation: "abc" has length 3',
      constraints: ['0 ≤ string length ≤ 10^5', 'ASCII characters only'],
      testCases: [
        { input: 'abcabcbb', output: '3', hidden: false },
        { input: 'bbbbb', output: '1', hidden: false },
        { input: 'pwwkew', output: '3', hidden: false },
        { input: '', output: '0', hidden: true }
      ],
      starterCode: {
        python: '# Enter your code here\ns = input()\n# Find longest substring length\n',
        c: '#include <stdio.h>\n#include <string.h>\nint main() {\n    char s[100001];\n    scanf("%s", s);\n    // Your code here\n    return 0;\n}',
        cpp: '#include <iostream>\n#include <string>\n#include <unordered_set>\nusing namespace std;\nint main() {\n    string s;\n    cin >> s;\n    // Your code here\n    return 0;\n}',
        java: 'import java.util.*;\npublic class Solution {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        String s = sc.next();\n        // Your code here\n    }\n}'
      }
    },
    9: {
      title: 'Matrix Rotation',
      desc: 'Rotate a square matrix 90 degrees clockwise.',
      difficulty: 'hard',
      example: 'Input: 2 2\n1 2\n3 4\nOutput:\n3 1\n4 2',
      constraints: ['Square matrix only', 'Modify in-place if possible', '1 ≤ n ≤ 20'],
      testCases: [
        { input: '2 2\n1 2\n3 4', output: '3 1\n4 2', hidden: false },
        { input: '3 3\n1 2 3\n4 5 6\n7 8 9', output: '7 4 1\n8 5 2\n9 6 3', hidden: false }
      ],
      starterCode: {
        python: '# Enter your code here\nrows, cols = map(int, input().split())\nmatrix = [list(map(int, input().split())) for _ in range(rows)]\n# Rotate matrix\n',
        c: '#include <stdio.h>\nint main() {\n    // Your code here\n    return 0;\n}',
        cpp: '#include <iostream>\n#include <vector>\nusing namespace std;\nint main() {\n    // Your code here\n    return 0;\n}',
        java: 'import java.util.*;\npublic class Solution {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        // Your code here\n    }\n}'
      }
    },
    10: {
      title: 'Graph Traversal (BFS)',
      desc: 'Implement Breadth-First Search on a graph and return traversal order.',
      difficulty: 'hard',
      example: 'Input: 5 4\n0 1\n0 2\n1 3\n2 4\n0\nOutput: 0 1 2 3 4',
      constraints: ['Handle disconnected components', 'No duplicate visits'],
      testCases: [
        { input: '5 4\n0 1\n0 2\n1 3\n2 4\n0', output: '0 1 2 3 4', hidden: false }
      ],
      starterCode: {
        python: '# Enter your code here\nfrom collections import deque\nn, m = map(int, input().split())\n# Build graph and implement BFS\n',
        c: '#include <stdio.h>\nint main() {\n    // Your code here\n    return 0;\n}',
        cpp: '#include <iostream>\n#include <queue>\n#include <vector>\nusing namespace std;\nint main() {\n    // Your code here\n    return 0;\n}',
        java: 'import java.util.*;\npublic class Solution {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        // Your code here\n    }\n}'
      }
    },
    11: {
      title: '0/1 Knapsack Problem',
      desc: 'Solve the classic 0/1 Knapsack problem using dynamic programming.',
      difficulty: 'hard',
      example: 'Input: n=3, capacity=6\nweights: 1 2 3\nvalues: 10 15 40\nOutput: 55',
      constraints: ['Optimize time and space', '1 ≤ n ≤ 100', '1 ≤ capacity ≤ 1000'],
      testCases: [
        { input: '3 6\n1 2 3\n10 15 40', output: '55', hidden: false }
      ],
      starterCode: {
        python: '# Enter your code here\nn, capacity = map(int, input().split())\nweights = list(map(int, input().split()))\nvalues = list(map(int, input().split()))\n# Solve knapsack\n',
        c: '#include <stdio.h>\nint main() {\n    // Your code here\n    return 0;\n}',
        cpp: '#include <iostream>\n#include <vector>\nusing namespace std;\nint main() {\n    // Your code here\n    return 0;\n}',
        java: 'import java.util.*;\npublic class Solution {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        // Your code here\n    }\n}'
      }
    },
    12: {
      title: 'N-Queens Problem',
      desc: 'Place N queens on an N×N chessboard so no two queens attack each other. Return number of solutions.',
      difficulty: 'hard',
      example: 'Input: 4\nOutput: 2',
      constraints: ['No two queens in same row/column/diagonal', '1 ≤ N ≤ 10'],
      testCases: [
        { input: '4', output: '2', hidden: false },
        { input: '8', output: '92', hidden: false }
      ],
      starterCode: {
        python: '# Enter your code here\nn = int(input())\n# Solve N-Queens\n',
        c: '#include <stdio.h>\nint main() {\n    // Your code here\n    return 0;\n}',
        cpp: '#include <iostream>\nusing namespace std;\nint main() {\n    // Your code here\n    return 0;\n}',
        java: 'import java.util.*;\npublic class Solution {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        // Your code here\n    }\n}'
      }
    }
  };

  // Get problem id from URL
  const urlParams = new URLSearchParams(window.location.search);
  const problemId = parseInt(urlParams.get('id')) || 1;
  const currentProblem = problems[problemId];

  if (!currentProblem) {
    consoleOutput.innerHTML = `<div style="color: #e06c75;">Problem #${problemId} not found.</div>`;
    return;
  }

  // Render problem description area
  function renderProblem() {
    const content = document.getElementById('problemContent');
    content.innerHTML = `
      <div class="problem-title">
        <h2>${problemId}. ${currentProblem.title}</h2>
        <span class="difficulty-badge ${currentProblem.difficulty}">${currentProblem.difficulty}</span>
      </div>
      <div class="problem-description">${currentProblem.desc}</div>
      <div class="section">
        <h4>Example</h4>
        <pre>${currentProblem.example}</pre>
      </div>
      <div class="section constraints">
        <h4>Constraints</h4>
        <ul>${currentProblem.constraints.map(c => `<li>${c}</li>`).join('')}</ul>
      </div>
    `;
  }

  // Load starter code for the selected language
  function loadStarterCode() {
    const lang = languageSelect.value;
    const ext = languageMap[lang].ext;
    const code = currentProblem.starterCode[ext] || '// Write your code here';
    editor.setValue(code);
    editor.setOption('mode', languageModeMap[lang]);
  }

  languageSelect.addEventListener('change', loadStarterCode);

  // Simple HTML escape
  function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  // Execute code via backend Judge0 endpoints
  async function executeCode(code, languageId, stdin) {
    try {
      const res = await fetch('/run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          code: code,
          language_id: languageId,
          stdin: stdin || ''
        })
      });

      const data = await res.json();
      
      if (data.output) {
        // Check if output contains error indicators
        if (data.output.includes('Error:') || data.output.includes('[stderr]') || data.output.includes('[compile_output]')) {
          return { success: false, error: data.output };
        }
        return { success: true, output: data.output };
      } else {
        return { success: false, error: 'No output received' };
      }
    } catch (err) {
      return { success: false, error: err.message };
    }
  }

  // Run: visible tests only
  runBtn.addEventListener('click', async () => {
    const code = editor.getValue().trim();
    if (!code) { consoleOutput.innerHTML = '<div style="color: #e06c75;">Please write some code first.</div>'; return; }
    runBtn.disabled = true;
    consoleOutput.innerHTML = '<div style="color: #8b949e;">Running visible test cases...</div>';

    const lang = languageSelect.value;
    const languageId = languageMap[lang].id;
    const visible = currentProblem.testCases.filter(t => !t.hidden);

    let passed = 0, failed = 0;
    const parts = [];

    for (let i = 0; i < visible.length; i++) {
      const tc = visible[i];
      try {
        const res = await executeCode(code, languageId, tc.input);
        if (res.success) {
          const actual = res.output.trim();
          const expect = tc.output.trim();
          if (actual === expect) {
            passed++; parts.push(`<div class="test-result passed">Test ${i+1}: ✓</div>`);
          } else {
            failed++; parts.push(`<div class="test-result failed">Test ${i+1}: ✗<div><strong>Expected:</strong> ${escapeHtml(expect)}</div><div><strong>Got:</strong> ${escapeHtml(actual)}</div></div>`);
          }
        } else {
          failed++; parts.push(`<div class="test-result failed">Test ${i+1}: ✗<div><strong>Error:</strong> ${escapeHtml(res.error)}</div></div>`);
        }
      } catch (e) {
        failed++; parts.push(`<div class="test-result failed">Test ${i+1}: ✗<div><strong>Exception:</strong> ${escapeHtml(e.message)}</div></div>`);
      }
    }

    const summary = `<div style="margin-bottom:8px;"><strong>Passed:</strong> ${passed} &nbsp; <strong>Failed:</strong> ${failed} &nbsp; <strong>Total:</strong> ${visible.length}</div>`;
    consoleOutput.innerHTML = summary + parts.join('');
    runBtn.disabled = false;
  });

  // Submit: all tests including hidden
  submitBtn.addEventListener('click', async () => {
    const code = editor.getValue().trim();
    if (!code) { consoleOutput.innerHTML = '<div style="color: #e06c75;">Please write some code first.</div>'; return; }
    submitBtn.disabled = true;
    consoleOutput.innerHTML = '<div style="color: #8b949e;">Submitting solution (running all tests)...</div>';

    const lang = languageSelect.value;
    const languageId = languageMap[lang].id;
    const all = currentProblem.testCases;

    let passed = 0, failed = 0;
    const parts = [];

    for (let i = 0; i < all.length; i++) {
      const tc = all[i];
      try {
        const res = await executeCode(code, languageId, tc.input);
        if (res.success) {
          const actual = res.output.trim();
          const expect = tc.output.trim();
          if (actual === expect) {
            passed++; parts.push(`<div class="test-result passed">${tc.hidden ? 'Hidden ' : ''}Test ${i+1}: ✓</div>`);
          } else {
            failed++; parts.push(`<div class="test-result failed">${tc.hidden ? 'Hidden ' : ''}Test ${i+1}: ✗</div>`);
          }
        } else {
          failed++; parts.push(`<div class="test-result failed">${tc.hidden ? 'Hidden ' : ''}Test ${i+1}: ✗<div><strong>Error:</strong> ${escapeHtml(res.error)}</div></div>`);
        }
      } catch (e) {
        failed++; parts.push(`<div class="test-result failed">${tc.hidden ? 'Hidden ' : ''}Test ${i+1}: ✗<div><strong>Exception:</strong> ${escapeHtml(e.message)}</div></div>`);
      }
    }

    const allPassed = failed === 0;
    let banner = '';
    if (allPassed) {
      banner = `<div class="success-banner">🎉 Accepted! All tests passed.</div>`;
    }

    const summary = `<div style="margin-bottom:8px;"><strong>Passed:</strong> ${passed}/${all.length} &nbsp; <strong>Failed:</strong> ${failed}/${all.length}</div>`;
    consoleOutput.innerHTML = banner + summary + parts.join('');
    submitBtn.disabled = false;
  });

  // Initialize
  renderProblem();
  loadStarterCode();
});
// ============================================
// PRACTICE PAGE - LEETCODE-STYLE INTERFACE
// ============================================

document.addEventListener("DOMContentLoaded", () => {
  console.log("🚀 LeetCode-style Practice.js loaded!");

  // ============================================
  // CODEMIRROR INITIALIZATION
  // ============================================
  const codeEditorTextarea = document.getElementById("codeEditor");
  
  const languageModeMap = {
    "Python": "python",
    "C": "text/x-csrc",
    "C++": "text/x-c++src",
    "Java": "text/x-java"
  };
  
  const codeMirrorEditor = CodeMirror.fromTextArea(codeEditorTextarea, {
    mode: "python",
    theme: "monokai",
    lineNumbers: true,
    autofocus: true,
    indentUnit: 4,
    tabSize: 4,
    lineWrapping: true,
    autoCloseBrackets: true,
    matchBrackets: true,
    styleActiveLine: true
  });

  // ============================================
  // RESIZABLE CONSOLE PANEL
  // ============================================
  const resizer = document.getElementById('resizer');
  const editorWrapper = document.querySelector('.editor-wrapper');
  const consolePanel = document.querySelector('.console-panel');
  const editorConsoleSplit = document.querySelector('.editor-console-split');
  
  let isResizing = false;
  
  resizer.addEventListener('mousedown', (e) => {
    isResizing = true;
    document.body.style.cursor = 'ns-resize';
  });
  
  document.addEventListener('mousemove', (e) => {
    if (!isResizing) return;
    
    const containerRect = editorConsoleSplit.getBoundingClientRect();
    const newConsoleHeight = containerRect.bottom - e.clientY;
    
    if (newConsoleHeight >= 100 && newConsoleHeight <= containerRect.height - 200) {
      consolePanel.style.height = newConsoleHeight + 'px';
    }
  });
  
  document.addEventListener('mouseup', () => {
    isResizing = false;
    document.body.style.cursor = 'default';
  });

  // ============================================
  // PROBLEM DATA WITH TEST CASES
  // ============================================
  const problems = {
    1: {
      title: "Two Sum",
      desc: "Given an array of integers and a target sum, return indices of two numbers that add up to the target.",
      difficulty: "easy",
      example: 'Input: nums = [2, 7, 11, 15], target = 9\nOutput: [0, 1]\nExplanation: nums[0] + nums[1] = 2 + 7 = 9',
      constraints: ['2 ≤ nums.length ≤ 10^4', 'Each input has exactly one solution', '-10^9 ≤ nums[i] ≤ 10^9'],
      testCases: [
        { input: '2 7 11 15\n9', output: '0 1', hidden: false },
        { input: '3 2 4\n6', output: '1 2', hidden: false },
        { input: '3 3\n6', output: '0 1', hidden: false },
        { input: '-1 -2 -3 -4 -5\n-8', output: '2 4', hidden: true }
      ],
      starterCode: {
        python: '# Enter your code here\nnums = list(map(int, input().split()))\ntarget = int(input())\n\n# Your solution here\n',
        c: '#include <stdio.h>\nint main() {\n    // Your code here\n    return 0;\n}',
        cpp: '#include <iostream>\nusing namespace std;\nint main() {\n    // Your code here\n    return 0;\n}',
        java: 'import java.util.*;\npublic class Solution {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        // Your code here\n    }\n}'
      }
    },
    2: {
      title: "Reverse String",
      desc: "Write a function that reverses a given string.",
      difficulty: "easy",
      example: 'Input: "hello"\nOutput: "olleh"',
      constraints: ['1 ≤ string length ≤ 1000', 'String consists of printable ASCII characters'],
      testCases: [
        { input: 'hello', output: 'olleh', hidden: false },
        { input: 'world', output: 'dlrow', hidden: false },
        { input: 'racecar', output: 'racecar', hidden: false },
        { input: 'Python Programming', output: 'gnimmargorP nohtyP', hidden: true }
      ],
      starterCode: {
        python: '# Enter your code here\ns = input()\n# Reverse the string and print\n',
        c: '#include <stdio.h>\n#include <string.h>\nint main() {\n    char s[1001];\n    scanf("%[^\\n]", s);\n    // Your code here\n    return 0;\n}',
        cpp: '#include <iostream>\n#include <string>\nusing namespace std;\nint main() {\n    string s;\n    getline(cin, s);\n    // Your code here\n    return 0;\n}',
        java: 'import java.util.*;\npublic class Solution {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        String s = sc.nextLine();\n        // Your code here\n    }\n}'
      }
    },
    3: {
      title: "Fibonacci Sequence",
      desc: "Generate the first n Fibonacci numbers.",
      difficulty: "easy",
      example: 'Input: 5\nOutput: 0 1 1 2 3',
      constraints: ['1 ≤ n ≤ 50'],
      testCases: [
        { input: '5', output: '0 1 1 2 3', hidden: false },
        { input: '8', output: '0 1 1 2 3 5 8 13', hidden: false },
        { input: '1', output: '0', hidden: false },
        { input: '10', output: '0 1 1 2 3 5 8 13 21 34', hidden: true }
      ],
      starterCode: {
        python: '# Enter your code here\nn = int(input())\n# Generate and print first n Fibonacci numbers\n',
        c: '#include <stdio.h>\nint main() {\n    int n;\n    scanf("%d", &n);\n    // Your code here\n    return 0;\n}',
        cpp: '#include <iostream>\nusing namespace std;\nint main() {\n    int n;\n    cin >> n;\n    // Your code here\n    return 0;\n}',
        java: 'import java.util.*;\npublic class Solution {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        int n = sc.nextInt();\n        // Your code here\n    }\n}'
      }
    },
    4: {
      title: "Palindrome Check",
      desc: "Check if a given string is a palindrome (reads same forwards and backwards).",
      difficulty: "easy",
      example: 'Input: "racecar"\nOutput: true',
      constraints: ['Case insensitive', 'Ignore spaces and punctuation'],
      testCases: [
        { input: 'racecar', output: 'true', hidden: false },
        { input: 'hello', output: 'false', hidden: false },
        { input: 'A man a plan a canal Panama', output: 'true', hidden: false },
        { input: 'Was it a car or a cat I saw', output: 'true', hidden: true }
      ],
      starterCode: {
        python: '# Enter your code here\ns = input()\n# Check if palindrome and print true/false\n',
        c: '#include <stdio.h>\n#include <string.h>\n#include <ctype.h>\nint main() {\n    char s[1001];\n    scanf("%[^\\n]", s);\n    // Your code here\n    return 0;\n}',
        cpp: '#include <iostream>\n#include <string>\n#include <algorithm>\nusing namespace std;\nint main() {\n    string s;\n    getline(cin, s);\n    // Your code here\n    return 0;\n}',
        java: 'import java.util.*;\npublic class Solution {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        String s = sc.nextLine();\n        // Your code here\n    }\n}'
      }
    },
    5: {
      title: "Binary Search",
      desc: "Implement binary search algorithm on a sorted array. Return the index of target element or -1 if not found.",
      difficulty: "medium",
      example: 'Input: arr = [1, 3, 5, 7, 9], target = 5\nOutput: 2',
      constraints: ['Array is sorted in ascending order', 'Return -1 if not found', '1 ≤ array length ≤ 10^4'],
      testCases: [
        { input: '1 3 5 7 9\n5', output: '2', hidden: false },
        { input: '1 3 5 7 9\n6', output: '-1', hidden: false },
        { input: '2 4 6 8 10 12\n12', output: '5', hidden: false },
        { input: '10 20 30 40 50\n10', output: '0', hidden: true }
      ],
      starterCode: {
        python: '# Enter your code here\narr = list(map(int, input().split()))\ntarget = int(input())\n# Implement binary search\n',
        c: '#include <stdio.h>\nint main() {\n    int arr[10000], n = 0, target;\n    while(scanf("%d", &arr[n]) == 1) n++;\n    n--; target = arr[n];\n    // Your code here\n    return 0;\n}',
        cpp: '#include <iostream>\n#include <vector>\nusing namespace std;\nint main() {\n    vector<int> arr;\n    int x, target;\n    while(cin >> x) arr.push_back(x);\n    target = arr.back(); arr.pop_back();\n    // Your code here\n    return 0;\n}',
        java: 'import java.util.*;\npublic class Solution {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        String[] nums = sc.nextLine().split(" ");\n        int target = sc.nextInt();\n        // Your code here\n    }\n}'
      }
    },
    6: {
      title: "Merge Sorted Arrays",
      desc: "Merge two sorted arrays into one sorted array.",
      difficulty: "medium",
      example: 'Input: arr1 = [1, 3, 5], arr2 = [2, 4, 6]\nOutput: [1, 2, 3, 4, 5, 6]',
      constraints: ['Both arrays are sorted', 'Handle empty arrays', '0 ≤ array length ≤ 1000'],
      testCases: [
        { input: '1 3 5\n2 4 6', output: '1 2 3 4 5 6', hidden: false },
        { input: '1 2 3\n4 5 6', output: '1 2 3 4 5 6', hidden: false },
        { input: '5\n1 2 3', output: '1 2 3 5', hidden: false },
        { input: '\n1 2 3', output: '1 2 3', hidden: true }
      ],
      starterCode: {
        python: '# Enter your code here\narr1 = list(map(int, input().split())) if input() else []\narr2 = list(map(int, input().split()))\n# Merge arrays\n',
        c: '#include <stdio.h>\nint main() {\n    // Your code here\n    return 0;\n}',
        cpp: '#include <iostream>\n#include <vector>\nusing namespace std;\nint main() {\n    // Your code here\n    return 0;\n}',
        java: 'import java.util.*;\npublic class Solution {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        // Your code here\n    }\n}'
      }
    },
    7: {
      title: "Valid Parentheses",
      desc: "Check if a string has valid matching parentheses, brackets, and braces.",
      difficulty: "medium",
      example: 'Input: "({[]})"\nOutput: true',
      constraints: ['Only (), {}, [] characters', 'Must close in correct order'],
      testCases: [
        { input: '()', output: 'true', hidden: false },
        { input: '({[]})', output: 'true', hidden: false },
        { input: '(]', output: 'false', hidden: false },
        { input: '([)]', output: 'false', hidden: true }
      ],
      starterCode: {
        python: '# Enter your code here\ns = input()\n# Check if valid parentheses\n',
        c: '#include <stdio.h>\n#include <string.h>\nint main() {\n    char s[1001];\n    scanf("%s", s);\n    // Your code here\n    return 0;\n}',
        cpp: '#include <iostream>\n#include <string>\n#include <stack>\nusing namespace std;\nint main() {\n    string s;\n    cin >> s;\n    // Your code here\n    return 0;\n}',
        java: 'import java.util.*;\npublic class Solution {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        String s = sc.next();\n        // Your code here\n    }\n}'
      }
    },
    8: {
      title: "Longest Substring",
      desc: "Find the length of the longest substring without repeating characters.",
      difficulty: "medium",
      example: 'Input: "abcabcbb"\nOutput: 3\nExplanation: "abc" has length 3',
      constraints: ['0 ≤ string length ≤ 10^5', 'ASCII characters only'],
      testCases: [
        { input: 'abcabcbb', output: '3', hidden: false },
        { input: 'bbbbb', output: '1', hidden: false },
        { input: 'pwwkew', output: '3', hidden: false },
        { input: '', output: '0', hidden: true }
      ],
      starterCode: {
        python: '# Enter your code here\ns = input()\n# Find longest substring length\n',
        c: '#include <stdio.h>\n#include <string.h>\nint main() {\n    char s[100001];\n    scanf("%s", s);\n    // Your code here\n    return 0;\n}',
        cpp: '#include <iostream>\n#include <string>\n#include <unordered_set>\nusing namespace std;\nint main() {\n    string s;\n    cin >> s;\n    // Your code here\n    return 0;\n}',
        java: 'import java.util.*;\npublic class Solution {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        String s = sc.next();\n        // Your code here\n    }\n}'
      }
    },
    9: {
      title: "Matrix Rotation",
      desc: "Rotate a square matrix 90 degrees clockwise.",
      difficulty: "hard",
      example: 'Input: 2 2\n1 2\n3 4\nOutput:\n3 1\n4 2',
      constraints: ['Square matrix only', 'Modify in-place if possible', '1 ≤ n ≤ 20'],
      testCases: [
        { input: '2 2\n1 2\n3 4', output: '3 1\n4 2', hidden: false },
        { input: '3 3\n1 2 3\n4 5 6\n7 8 9', output: '7 4 1\n8 5 2\n9 6 3', hidden: false }
      ],
      starterCode: {
        python: '# Enter your code here\nrows, cols = map(int, input().split())\nmatrix = [list(map(int, input().split())) for _ in range(rows)]\n# Rotate matrix\n',
        c: '#include <stdio.h>\nint main() {\n    // Your code here\n    return 0;\n}',
        cpp: '#include <iostream>\n#include <vector>\nusing namespace std;\nint main() {\n    // Your code here\n    return 0;\n}',
        java: 'import java.util.*;\npublic class Solution {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        // Your code here\n    }\n}'
      }
    },
    10: {
      title: "Graph Traversal (BFS)",
      desc: "Implement Breadth-First Search on a graph and return traversal order.",
      difficulty: "hard",
      example: 'Input: 5 4\n0 1\n0 2\n1 3\n2 4\n0\nOutput: 0 1 2 3 4',
      constraints: ['Handle disconnected components', 'No duplicate visits'],
      testCases: [
        { input: '5 4\n0 1\n0 2\n1 3\n2 4\n0', output: '0 1 2 3 4', hidden: false }
      ],
      starterCode: {
        python: '# Enter your code here\nfrom collections import deque\nn, m = map(int, input().split())\n# Build graph and implement BFS\n',
        c: '#include <stdio.h>\nint main() {\n    // Your code here\n    return 0;\n}',
        cpp: '#include <iostream>\n#include <queue>\n#include <vector>\nusing namespace std;\nint main() {\n    // Your code here\n    return 0;\n}',
        java: 'import java.util.*;\npublic class Solution {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        // Your code here\n    }\n}'
      }
    },
    11: {
      title: "0/1 Knapsack Problem",
      desc: "Solve the classic 0/1 Knapsack problem using dynamic programming.",
      difficulty: "hard",
      example: 'Input: n=3, capacity=6\nweights: 1 2 3\nvalues: 10 15 40\nOutput: 55',
      constraints: ['Optimize time and space', '1 ≤ n ≤ 100', '1 ≤ capacity ≤ 1000'],
      testCases: [
        { input: '3 6\n1 2 3\n10 15 40', output: '55', hidden: false }
      ],
      starterCode: {
        python: '# Enter your code here\nn, capacity = map(int, input().split())\nweights = list(map(int, input().split()))\nvalues = list(map(int, input().split()))\n# Solve knapsack\n',
        c: '#include <stdio.h>\nint main() {\n    // Your code here\n    return 0;\n}',
        cpp: '#include <iostream>\n#include <vector>\nusing namespace std;\nint main() {\n    // Your code here\n    return 0;\n}',
        java: 'import java.util.*;\npublic class Solution {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        // Your code here\n    }\n}'
      }
    },
    12: {
      title: "N-Queens Problem",
      desc: "Place N queens on an N×N chessboard so no two queens attack each other. Return number of solutions.",
      difficulty: "hard",
      example: 'Input: 4\nOutput: 2',
      constraints: ['No two queens in same row/column/diagonal', '1 ≤ N ≤ 10'],
      testCases: [
        { input: '4', output: '2', hidden: false },
        { input: '8', output: '92', hidden: false }
      ],
      starterCode: {
        python: '# Enter your code here\nn = int(input())\n# Solve N-Queens\n',
        c: '#include <stdio.h>\nint main() {\n    // Your code here\n    return 0;\n}',
        cpp: '#include <iostream>\nusing namespace std;\nint main() {\n    // Your code here\n    return 0;\n}',
        java: 'import java.util.*;\npublic class Solution {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        // Your code here\n    }\n}'
      }
    }
  };


  // ============================================
  // TAB FUNCTIONALITY
  // ============================================
  const tabs = document.querySelectorAll('.tab');
  tabs.forEach(tab => {
    tab.addEventListener('click', () => {
      tabs.forEach(t => t.classList.remove('active'));
      tab.classList.add('active');
      
      // You can add different content for each tab here
      const tabType = tab.dataset.tab;
      if (tabType === 'solutions') {
        document.getElementById('problemContent').innerHTML = `
          <div style="padding: 2rem; text-align: center; color: var(--text-secondary);">
            <h3>Solutions</h3>
            <p>Community solutions will appear here</p>
          </div>
        `;
      } else if (tabType === 'submissions') {
        document.getElementById('problemContent').innerHTML = `
          <div style="padding: 2rem; text-align: center; color: var(--text-secondary);">
            <h3>Submissions</h3>
            <p>Your submission history will appear here</p>
          </div>
        `;
      } else {
        loadProblemDescription();
      }
    });
  });

  // Console tabs
  const consoleTabs = document.querySelectorAll('.console-tab');
  consoleTabs.forEach(tab => {
    tab.addEventListener('click', () => {
      consoleTabs.forEach(t => t.classList.remove('active'));
      tab.classList.add('active');
    });
  });

  // ============================================
  // LANGUAGE MAPPING
  // ============================================
  const languageMap = {
    'Python': { id: 71, ext: 'python' },
    'C': { id: 50, ext: 'c' },
    'C++': { id: 54, ext: 'cpp' },
    'Java': { id: 62, ext: 'java' }
  };

  // ============================================
  // DOM ELEMENTS
  // ============================================
  const consoleOutput = document.getElementById("consoleOutput");
  const runBtn = document.getElementById("runBtn");
  const submitBtn = document.getElementById("submitBtn");
  const languageSelect = document.getElementById("languageSelect");

  // ============================================
  // GET CURRENT PROBLEM
  // ============================================
  const urlParams = new URLSearchParams(window.location.search);
  const problemId = parseInt(urlParams.get('id')) || 1;
  const currentProblem = problems[problemId];

  if (!currentProblem) {
    consoleOutput.innerHTML = `<div style="color: var(--accent-red);">❌ Problem #${problemId} not found!</div>`;
    return;
  }

  // ============================================
  // LOAD PROBLEM DESCRIPTION
  // ============================================
  function loadProblemDescription() {
    const content = document.getElementById('problemContent');
    content.innerHTML = `
      <div class="problem-title">
        <h2>${problemId}. ${currentProblem.title}</h2>
        <span class="difficulty-badge ${currentProblem.difficulty}">${currentProblem.difficulty}</span>
      </div>

      <div class="problem-description">
        ${currentProblem.desc}
      </div>

      <div class="section">
        <h3>Example 1:</h3>
        <div class="example-box">
          <pre>${currentProblem.example}</pre>
        </div>
      </div>

      <div class="section constraints">
        <h3>Constraints:</h3>
        <ul>
          ${currentProblem.constraints.map(c => `<li>${c}</li>`).join('')}
        </ul>
      </div>
    `;
  }

  // ============================================
  // LOAD STARTER CODE
  // ============================================
  function loadStarterCode() {
    const lang = languageSelect.value;
    const langKey = languageMap[lang].ext;
    const code = currentProblem.starterCode[langKey] || '// Write your code here';
    
    codeMirrorEditor.setValue(code);
    codeMirrorEditor.setOption('mode', languageModeMap[lang]);
  }

  languageSelect.addEventListener('change', loadStarterCode);


  // ============================================
  // RUN CODE (Test with Sample Cases)
  // ============================================
  runBtn.addEventListener("click", async () => {
    const code = codeMirrorEditor.getValue().trim();
    if (!code) {
      consoleOutput.innerHTML = '<div style="color: var(--accent-red);">❌ Please write some code first!</div>';
      return;
    }

    consoleOutput.innerHTML = '<div style="color: var(--text-secondary);"><span class="spinner"></span> Running test cases...</div>';
    runBtn.disabled = true;

    const lang = languageSelect.value;
    const languageId = languageMap[lang].id;

    // Run only visible test cases
    const visibleTests = currentProblem.testCases.filter(t => !t.hidden);
    let passed = 0;
    let failed = 0;
    let results = [];

    for (let i = 0; i < visibleTests.length; i++) {
      const testCase = visibleTests[i];
      try {
        const result = await executeCode(code, languageId, testCase.input);
        
        if (result.success) {
          const actualOutput = result.output.trim();
          const expectedOutput = testCase.output.trim();
          
          if (actualOutput === expectedOutput) {
            passed++;
            results.push(`
              <div class="test-result passed">
                <div class="test-result-header">
                  <span class="pass-icon">✓</span>
                  <span>Test Case ${i + 1}</span>
                </div>
                <div class="test-result-body">
                  <div><strong>Input:</strong> ${escapeHtml(testCase.input)}</div>
                  <div><strong>Output:</strong> ${escapeHtml(actualOutput)}</div>
                  <div style="color: var(--accent-green);"><strong>Expected:</strong> ${escapeHtml(expectedOutput)}</div>
                </div>
              </div>
            `);
          } else {
            failed++;
            results.push(`
              <div class="test-result failed">
                <div class="test-result-header">
                  <span class="fail-icon">✗</span>
                  <span>Test Case ${i + 1}</span>
                </div>
                <div class="test-result-body">
                  <div><strong>Input:</strong> ${escapeHtml(testCase.input)}</div>
                  <div style="color: var(--accent-red);"><strong>Output:</strong> ${escapeHtml(actualOutput)}</div>
                  <div style="color: var(--accent-green);"><strong>Expected:</strong> ${escapeHtml(expectedOutput)}</div>
                </div>
              </div>
            `);
          }
        } else {
          failed++;
          results.push(`
            <div class="test-result failed">
              <div class="test-result-header">
                <span class="fail-icon">✗</span>
                <span>Test Case ${i + 1}</span>
              </div>
              <div class="test-result-body">
                <div style="color: var(--accent-red);"><strong>Error:</strong> ${escapeHtml(result.error)}</div>
              </div>
            </div>
          `);
        }
      } catch (error) {
        failed++;
        results.push(`
          <div class="test-result failed">
            <div class="test-result-header">
              <span class="fail-icon">✗</span>
              <span>Test Case ${i + 1}</span>
            </div>
            <div class="test-result-body">
              <div style="color: var(--accent-red);"><strong>Exception:</strong> ${escapeHtml(error.message)}</div>
            </div>
          </div>
        `);
      }
    }

    const summary = `
      <div style="margin-bottom: 1.5rem; padding: 1rem; background: var(--bg-tertiary); border-radius: 8px;">
        <div style="font-size: 1.125rem; font-weight: 600; margin-bottom: 0.5rem;">Test Results</div>
        <div style="display: flex; gap: 1.5rem;">
          <div><span style="color: var(--accent-green);">✓ Passed:</span> <strong>${passed}</strong></div>
          <div><span style="color: var(--accent-red);">✗ Failed:</span> <strong>${failed}</strong></div>
          <div><span style="color: var(--text-secondary);">Total:</span> <strong>${visibleTests.length}</strong></div>
        </div>
      </div>
    `;

    consoleOutput.innerHTML = summary + results.join('');
    runBtn.disabled = false;
    
    // Switch to result tab
    document.querySelectorAll('.console-tab').forEach(t => t.classList.remove('active'));
    document.querySelector('[data-console="result"]').classList.add('active');
  });


  // ============================================
  // SUBMIT CODE (Test with ALL Cases)
  // ============================================
  submitBtn.addEventListener("click", async () => {
    const code = codeMirrorEditor.getValue().trim();
    if (!code) {
      consoleOutput.innerHTML = '<div style="color: var(--accent-red);">❌ Please write some code first!</div>';
      return;
    }

    consoleOutput.innerHTML = '<div style="color: var(--text-secondary);"><span class="spinner"></span> Submitting solution...</div>';
    submitBtn.disabled = true;

    const lang = languageSelect.value;
    const languageId = languageMap[lang].id;

    // Run ALL test cases
    const allTests = currentProblem.testCases;
    let passed = 0;
    let failed = 0;
    let results = [];

    for (let i = 0; i < allTests.length; i++) {
      const testCase = allTests[i];
      const isHidden = testCase.hidden;
      
      try {
        const result = await executeCode(code, languageId, testCase.input);
        
        if (result.success) {
          const actualOutput = result.output.trim();
          const expectedOutput = testCase.output.trim();
          
          if (actualOutput === expectedOutput) {
            passed++;
            if (isHidden) {
              results.push(`
                <div class="test-result passed">
                  <div class="test-result-header">
                    <span class="pass-icon">✓</span>
                    <span>Hidden Test Case ${i + 1}</span>
                  </div>
                  <div class="test-result-body">
                    <div style="color: var(--accent-green);">Passed ✓</div>
                  </div>
                </div>
              `);
            } else {
              results.push(`
                <div class="test-result passed">
                  <div class="test-result-header">
                    <span class="pass-icon">✓</span>
                    <span>Test Case ${i + 1}</span>
                  </div>
                  <div class="test-result-body">
                    <div><strong>Input:</strong> ${escapeHtml(testCase.input)}</div>
                    <div><strong>Output:</strong> ${escapeHtml(actualOutput)}</div>
                    <div style="color: var(--accent-green);"><strong>Expected:</strong> ${escapeHtml(expectedOutput)}</div>
                  </div>
                </div>
              `);
            }
          } else {
            failed++;
            if (isHidden) {
              results.push(`
                <div class="test-result failed">
                  <div class="test-result-header">
                    <span class="fail-icon">✗</span>
                    <span>Hidden Test Case ${i + 1}</span>
                  </div>
                  <div class="test-result-body">
                    <div style="color: var(--accent-red);">Failed ✗</div>
                  </div>
                </div>
              `);
            } else {
              results.push(`
                <div class="test-result failed">
                  <div class="test-result-header">
                    <span class="fail-icon">✗</span>
                    <span>Test Case ${i + 1}</span>
                  </div>
                  <div class="test-result-body">
                    <div><strong>Input:</strong> ${escapeHtml(testCase.input)}</div>
                    <div style="color: var(--accent-red);"><strong>Output:</strong> ${escapeHtml(actualOutput)}</div>
                    <div style="color: var(--accent-green);"><strong>Expected:</strong> ${escapeHtml(expectedOutput)}</div>
                  </div>
                </div>
              `);
            }
          }
        } else {
          failed++;
          results.push(`
            <div class="test-result failed">
              <div class="test-result-header">
                <span class="fail-icon">✗</span>
                <span>Test Case ${i + 1}${isHidden ? ' (Hidden)' : ''}</span>
              </div>
              <div class="test-result-body">
                <div style="color: var(--accent-red);"><strong>Error:</strong> ${escapeHtml(result.error)}</div>
              </div>
            </div>
          `);
        }
      } catch (error) {
        failed++;
        results.push(`
          <div class="test-result failed">
            <div class="test-result-header">
              <span class="fail-icon">✗</span>
              <span>Test Case ${i + 1}${isHidden ? ' (Hidden)' : ''}</span>
            </div>
            <div class="test-result-body">
              <div style="color: var(--accent-red);"><strong>Exception:</strong> ${escapeHtml(error.message)}</div>
            </div>
          </div>
        `);
      }
    }

    const allPassed = failed === 0;
    let output = '';
    
    if (allPassed) {
      output = `
        <div class="success-banner">
          <h3>🎉 Accepted! 🎉</h3>
          <p style="color: var(--text-secondary); margin-top: 0.5rem;">
            Your submission passed all test cases!
          </p>
        </div>
      `;
    }
    
    output += `
      <div style="margin-bottom: 1.5rem; padding: 1rem; background: var(--bg-tertiary); border-radius: 8px;">
        <div style="font-size: 1.125rem; font-weight: 600; margin-bottom: 0.5rem;">Submission Results</div>
        <div style="display: flex; gap: 1.5rem;">
          <div><span style="color: var(--accent-green);">✓ Passed:</span> <strong>${passed}/${allTests.length}</strong></div>
          <div><span style="color: var(--accent-red);">✗ Failed:</span> <strong>${failed}/${allTests.length}</strong></div>
        </div>
      </div>
    `;

    consoleOutput.innerHTML = output + results.join('');
    submitBtn.disabled = false;
    
    // Switch to result tab
    document.querySelectorAll('.console-tab').forEach(t => t.classList.remove('active'));
    document.querySelector('[data-console="result"]').classList.add('active');
  });


  // ============================================
  // HELPER FUNCTIONS
  // ============================================
  function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  // ============================================
  // EXECUTE CODE VIA JUDGE0
  // ============================================
  async function executeCode(code, languageId, stdin) {
    try {
      // Submit code to Judge0
      const submitResponse = await fetch('/submit-code', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          source_code: btoa(unescape(encodeURIComponent(code))),
          language_id: languageId,
          stdin: btoa(unescape(encodeURIComponent(stdin)))
        })
      });

      const submitData = await submitResponse.json();
      
      if (!submitData.token) {
        return { success: false, error: 'Failed to submit code' };
      }

      // Poll for results
      let attempts = 0;
      const maxAttempts = 20;
      
      while (attempts < maxAttempts) {
        await new Promise(resolve => setTimeout(resolve, 500));
        
        const resultResponse = await fetch(`/get-result?token=${submitData.token}`);
        const resultData = await resultResponse.json();
        
        if (resultData.status && resultData.status.id <= 2) {
          // Still processing
          attempts++;
          continue;
        }

        // Execution complete
        if (resultData.status && resultData.status.id === 3) {
          // Success
          const output = resultData.stdout ? atob(resultData.stdout) : '';
          return { success: true, output };
        } else {
          // Error
          const error = resultData.stderr ? atob(resultData.stderr) : 
                       resultData.compile_output ? atob(resultData.compile_output) :
                       'Unknown error';
          return { success: false, error };
        }
      }

      return { success: false, error: 'Execution timeout' };

    } catch (error) {
      console.error('Execution error:', error);
      return { success: false, error: error.message };
    }
  }

  // ============================================
  // INITIALIZE
  // ============================================
  loadProblemDescription();
  loadStarterCode();
  console.log("✅ LeetCode-style practice page ready!");
});
