// ESLint v9 configuration file for CodeX debugging system
export default [
    {
        // Ignore patterns - allow temp files from any location
        ignores: [],
        
        rules: {
            "semi": ["error", "always"],
            "quotes": ["warn", "double"],
            "no-unused-vars": "warn",
            "no-undef": "warn",
            "no-console": "off",
            "no-var": "warn"
        },
        
        languageOptions: {
            ecmaVersion: "latest",
            sourceType: "script",  // Changed to script to support more code patterns
            globals: {
                console: "readonly",
                process: "readonly",
                __dirname: "readonly",
                __filename: "readonly",
                Buffer: "readonly",
                module: "readonly",
                require: "readonly",
                window: "readonly",
                document: "readonly"
            }
        }
    }
];
