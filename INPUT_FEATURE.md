# User Input Feature - Examples

## Feature Added
Added an **Input textarea** in the compiler page that allows users to provide input for programs that require it (like `input()`, `scanf()`, `Scanner`, etc.).

## How It Works
1. **Frontend**: Added an input textarea below the code editor
2. **JavaScript**: Sends `stdin` parameter along with code and language_id
3. **Backend**: Passes `stdin` to Judge0 API which provides it to the running program

## Example Programs to Test

### Python - Getting User Input
```python
name = input("Enter your name: ")
age = int(input("Enter your age: "))
print(f"Hello {name}, you are {age} years old!")
```

**Input Box:**
```
John
25
```

**Expected Output:**
```
Enter your name: Enter your age: Hello John, you are 25 years old!
```

---

### C - scanf Example
```c
#include <stdio.h>

int main() {
    char name[50];
    int age;
    
    printf("Enter your name: ");
    scanf("%s", name);
    
    printf("Enter your age: ");
    scanf("%d", &age);
    
    printf("Hello %s, you are %d years old!\n", name, age);
    
    return 0;
}
```

**Input Box:**
```
John
25
```

**Expected Output:**
```
Enter your name: Enter your age: Hello John, you are 25 years old!
```

---

### Java - Scanner Example
```java
import java.util.Scanner;

public class Main {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        
        System.out.print("Enter your name: ");
        String name = scanner.nextLine();
        
        System.out.print("Enter your age: ");
        int age = scanner.nextInt();
        
        System.out.println("Hello " + name + ", you are " + age + " years old!");
    }
}
```

**Input Box:**
```
John
25
```

**Expected Output:**
```
Enter your name: Enter your age: Hello John, you are 25 years old!
```

---

### JavaScript - readline (if supported)
```javascript
const readline = require('readline');
const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
});

console.log("Enter a number:");
rl.on('line', (input) => {
    const num = parseInt(input);
    console.log(`You entered: ${num}`);
    console.log(`Double of ${num} is ${num * 2}`);
    rl.close();
});
```

**Input Box:**
```
42
```

---

### Python - Multiple Inputs Example
```python
# Read multiple test cases
n = int(input())  # Number of test cases

for i in range(n):
    a, b = map(int, input().split())
    print(f"Sum of {a} and {b} is {a + b}")
```

**Input Box:**
```
3
10 20
5 15
100 200
```

**Expected Output:**
```
Sum of 10 and 20 is 30
Sum of 5 and 15 is 20
Sum of 100 and 200 is 300
```

---

### C - Array Input Example
```c
#include <stdio.h>

int main() {
    int n;
    printf("Enter number of elements: ");
    scanf("%d", &n);
    
    int arr[100];
    printf("Enter %d numbers:\n", n);
    for(int i = 0; i < n; i++) {
        scanf("%d", &arr[i]);
    }
    
    int sum = 0;
    for(int i = 0; i < n; i++) {
        sum += arr[i];
    }
    
    printf("Sum = %d\n", sum);
    return 0;
}
```

**Input Box:**
```
5
10
20
30
40
50
```

**Expected Output:**
```
Enter number of elements: Enter 5 numbers:
Sum = 150
```

---

## UI Changes Made

### compiler.html
- Added input textarea below code editor
- Label: "📝 Input (for programs that need user input...)"
- Placeholder with example
- Monospace font for better readability
- Resizable textarea

### compiler.js
- Get value from `inputBox`
- Send `stdin` parameter to `/run` endpoint

### app.py
- Updated `run_judge0()` to accept `stdin` parameter
- Updated `/run` endpoint to extract `stdin` from request
- Pass `stdin` to Judge0 API

## Testing Steps

1. **Start the server:**
   ```bash
   python app.py
   ```

2. **Go to:** http://127.0.0.1:5000/compiler

3. **Write a program** that requires input (e.g., Python `input()`)

4. **Enter input values** in the new "Input" textarea (one per line)

5. **Click "▶ Run Code"**

6. **See output** with your input values used

## Files Modified
- `templates/compiler.html` - Added input textarea
- `static/js/compiler.js` - Added stdin to request payload
- `app.py` - Updated run_judge0() and /run endpoint to handle stdin

## Status
✅ **Input feature implemented and ready to test!**
