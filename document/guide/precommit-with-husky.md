# Pre-Commit hook with husky Guide

<aside>
💡 이 내용은 Mac 을 기준으로 작성되었습니다.

</aside>

---

### 생성

1. Install husky

```bash
$ npm install --save-dev husky
$ npx husky install
```

2. Set up husky

```json
// Edit package.json
{
    ...,
    "scripts": {
        ...
        "prepare": "husky install"
    },
    ...
}
```

3. Add lint-staged (To apply pre-commit hook only for changed file)

```json
{
    ...
  "scripts": {
    ...
  },
    ...
  "lint-staged": {
    "{PYTHON_PROJECT_DIR}/**/*.py":  [
      "yarn precommit:{PROJECT_NAME}/py"
    ]
  }
}
```

4. Add hook

```bash
$ npx husky add .husky/pre-commit "npx lint-staged"
```

5. Add pre-commit script to package.json

```json
{
    ...
  "scripts": {
    "precommit:{PROJECT_NAME}/py": "cd ./{PROJECT_NAME} && yarn precommit:py",
    "prepare": "husky install"
  },
    ...
}
```


### 적용

```bash
$ yarn install
```

### 참고 자료

[https://blog.pumpkin-raccoon.com/85](https://blog.pumpkin-raccoon.com/85)