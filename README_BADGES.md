# README Badge Templates

Add these badges to the top of your `README.md` to show the status of your CI/CD pipelines.

## Quick Copy-Paste

**Replace `YOUR_USERNAME` with your GitHub username**

```markdown
# Local RAG Application

![Tests](https://github.com/YOUR_USERNAME/local-rag/workflows/Tests/badge.svg)
![Code Quality](https://github.com/YOUR_USERNAME/local-rag/workflows/Code%20Quality/badge.svg)
![Python](https://img.shields.io/badge/python-3.11-blue.svg)
![Coverage](https://img.shields.io/badge/coverage-100%25-brightgreen.svg)

Your README content here...
```

---

## Available Badges

### Test Status Badge
Shows if tests are passing or failing

```markdown
![Tests](https://github.com/YOUR_USERNAME/local-rag/workflows/Tests/badge.svg)
```

**Result**: ![Tests](https://github.com/YOUR_USERNAME/local-rag/workflows/Tests/badge.svg)

---

### Code Quality Badge
Shows code quality check status

```markdown
![Code Quality](https://github.com/YOUR_USERNAME/local-rag/workflows/Code%20Quality/badge.svg)
```

**Result**: ![Code Quality](https://github.com/YOUR_USERNAME/local-rag/workflows/Code%20Quality/badge.svg)

---

### Python Version Badge
Shows which Python version you're using

```markdown
![Python](https://img.shields.io/badge/python-3.11-blue.svg)
```

**Result**: ![Python](https://img.shields.io/badge/python-3.11-blue.svg)

---

### Coverage Badge (Static)
Manual coverage percentage

```markdown
![Coverage](https://img.shields.io/badge/coverage-100%25-brightgreen.svg)
```

**Result**: ![Coverage](https://img.shields.io/badge/coverage-100%25-brightgreen.svg)

**Colors**:
- 🟢 `brightgreen` - 80-100%
- 🟡 `yellow` - 60-79%
- 🟠 `orange` - 40-59%
- 🔴 `red` - 0-39%

---

### Codecov Badge (Dynamic)
Automatic coverage from Codecov (requires setup)

```markdown
[![codecov](https://codecov.io/gh/YOUR_USERNAME/local-rag/branch/main/graph/badge.svg)](https://codecov.io/gh/YOUR_USERNAME/local-rag)
```

**Setup Required**: See [CI_CD_SETUP.md](CI_CD_SETUP.md#option-2-using-codecov-recommended)

---

## Full Badge Collection

Here's a complete badge section you can use:

```markdown
# Local RAG Application

[![Tests](https://github.com/YOUR_USERNAME/local-rag/workflows/Tests/badge.svg)](https://github.com/YOUR_USERNAME/local-rag/actions)
[![Code Quality](https://github.com/YOUR_USERNAME/local-rag/workflows/Code%20Quality/badge.svg)](https://github.com/YOUR_USERNAME/local-rag/actions)
[![codecov](https://codecov.io/gh/YOUR_USERNAME/local-rag/branch/main/graph/badge.svg)](https://codecov.io/gh/YOUR_USERNAME/local-rag)
[![Python](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

> A Retrieval-Augmented Generation application for PDF and CSV documents
```

---

## Badge Examples by Project Type

### Minimal (Just Status)
```markdown
![Tests](https://github.com/YOUR_USERNAME/local-rag/workflows/Tests/badge.svg)
![Python](https://img.shields.io/badge/python-3.11-blue.svg)
```

### Standard (Status + Coverage)
```markdown
![Tests](https://github.com/YOUR_USERNAME/local-rag/workflows/Tests/badge.svg)
![Coverage](https://img.shields.io/badge/coverage-100%25-brightgreen.svg)
![Python](https://img.shields.io/badge/python-3.11-blue.svg)
```

### Professional (All Badges)
```markdown
[![Tests](https://github.com/YOUR_USERNAME/local-rag/workflows/Tests/badge.svg)](https://github.com/YOUR_USERNAME/local-rag/actions)
[![Code Quality](https://github.com/YOUR_USERNAME/local-rag/workflows/Code%20Quality/badge.svg)](https://github.com/YOUR_USERNAME/local-rag/actions)
[![codecov](https://codecov.io/gh/YOUR_USERNAME/local-rag/branch/main/graph/badge.svg)](https://codecov.io/gh/YOUR_USERNAME/local-rag)
[![Python](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)
```

---

## Custom Shields.io Badges

You can create custom badges at [shields.io](https://shields.io):

### Test Count Badge
```markdown
![Tests](https://img.shields.io/badge/tests-100%20passing-brightgreen.svg)
```

### Phase Badge
```markdown
![Phase](https://img.shields.io/badge/phase-1%20complete-blue.svg)
```

### Status Badge
```markdown
![Status](https://img.shields.io/badge/status-stable-green.svg)
```

---

## Updating README.md

### Step 1: Open Your README
```bash
vim README.md
# or
nano README.md
```

### Step 2: Add Badges at the Top
Place badges right after the title:

```markdown
# Document Q&A Assistant

![Tests](https://github.com/YOUR_USERNAME/local-rag/workflows/Tests/badge.svg)
![Python](https://img.shields.io/badge/python-3.11-blue.svg)
![Coverage](https://img.shields.io/badge/coverage-100%25-brightgreen.svg)

A Streamlit application that allows you to upload PDF and Markdown documents...
```

### Step 3: Commit and Push
```bash
git add README.md
git commit -m "Add CI/CD status badges"
git push
```

### Step 4: View Your Badges!
Go to your GitHub repository to see the badges in action.

---

## Badge States

### Passing ✅
```
![Tests](badge.svg)
```
Shows: ![Tests Passing](https://img.shields.io/badge/tests-passing-brightgreen.svg)

### Failing ❌
Shows: ![Tests Failing](https://img.shields.io/badge/tests-failing-red.svg)

### Running 🔄
Shows: ![Tests Running](https://img.shields.io/badge/tests-running-yellow.svg)

---

## Tips

1. **Keep it simple** - Don't add too many badges
2. **Make them clickable** - Link to Actions page
3. **Update coverage manually** - Or use Codecov for automatic updates
4. **Group related badges** - Tests, quality, meta-info

---

## Links to Add

Make badges clickable by wrapping them in links:

```markdown
[![Tests](https://github.com/YOUR_USERNAME/local-rag/workflows/Tests/badge.svg)](https://github.com/YOUR_USERNAME/local-rag/actions)
```

Now clicking the badge takes users to your Actions page!

---

## Example README Header

Here's a complete, polished README header:

```markdown
# 📄 Local RAG - Document Q&A Assistant

[![Tests](https://github.com/YOUR_USERNAME/local-rag/workflows/Tests/badge.svg)](https://github.com/YOUR_USERNAME/local-rag/actions)
[![codecov](https://codecov.io/gh/YOUR_USERNAME/local-rag/branch/main/graph/badge.svg)](https://codecov.io/gh/YOUR_USERNAME/local-rag)
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> 🤖 AI-powered document analysis with RAG (Retrieval-Augmented Generation)

A Streamlit application that allows you to upload PDF and Markdown documents and ask questions about their content using RAG (Retrieval-Augmented Generation).

## ✨ Features

- Upload PDF and Markdown documents through a web interface
- Ask questions about your documents using natural language
- Powered by Ollama (local) or Claude (cloud) LLMs
- Persistent storage with ChromaDB
- 100% test coverage on core functionality

## 🚀 Quick Start

...
```

---

## Remember!

**Don't forget to replace:**
- `YOUR_USERNAME` with your actual GitHub username
- `main` with your main branch name (if different)
- Coverage percentage with your actual coverage

**Example**:
```markdown
![Tests](https://github.com/alexb2611/local-rag/workflows/Tests/badge.svg)
```

---

**Ready to add badges? Just copy, replace YOUR_USERNAME, and paste into your README!**
