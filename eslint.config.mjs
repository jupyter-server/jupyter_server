export default [
    {
        "languageOptions": {
            "parserOptions": {
                "ecmaVersion": 6,
                "sourceType": "module"
            }
        },
        "rules": {
            "semi": 1,
            "no-cond-assign": 2,
            "no-debugger": 2,
            "comma-dangle": 0,
            "no-unreachable": 2
        },
        "ignores":  [
            "*.min.js",
            "*components*",
            "*node_modules*",
            "*built*",
            "*build*"
        ]
    }
];
