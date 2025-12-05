# CI/CD Setup Guide for Beginners

## What is CI/CD? 🤔

**CI/CD** stands for **Continuous Integration / Continuous Deployment**.

Think of it like having a robot assistant that:
- 🤖 Automatically runs your tests whenever you push code
- ✅ Checks if your code has any errors
- 📊 Creates coverage reports
- 🚨 Alerts you if something breaks

**No more forgetting to run tests before pushing!**

---

## What We've Set Up

Your repository now has **3 automated workflows**:

### 1. **Tests Workflow** (`tests.yml`)
- ✅ Runs all 100 tests automatically
- 📊 Generates coverage reports
- 🏃 Runs on every push and pull request
- ⏱️ Takes ~30 seconds to run

### 2. **Code Quality Workflow** (`code-quality.yml`)
- 🔍 Checks code formatting
- 🐛 Finds potential bugs
- 📏 Checks code style
- 💡 Suggests improvements

### 3. **Coverage Badge** (Optional)
- 📈 Shows test coverage percentage
- 🎨 Displays on your README
- 🔄 Updates automatically

---

## How It Works (Simple Explanation)

```
You push code to GitHub
         ↓
GitHub sees the .github/workflows/ files
         ↓
GitHub runs tests automatically
         ↓
You get a ✅ or ❌ result
         ↓
View results on GitHub
```

---

## Quick Start (3 Steps)

### Step 1: The Files Are Already Created! ✅

Your repository now has:
```
.github/workflows/
├── tests.yml           # Runs your tests
└── code-quality.yml    # Checks code quality
```

### Step 2: Push to GitHub

```bash
# Commit and push the workflow files
git add .github/workflows/
git commit -m "Add CI/CD workflows"
git push
```

### Step 3: Watch It Run!

1. Go to your GitHub repository
2. Click the **"Actions"** tab at the top
3. You'll see your workflows running! 🎉

---

## Understanding the Test Workflow

Let's break down what happens in `tests.yml`:

```yaml
name: Tests                    # Name shown in GitHub Actions

on:
  push:                       # Run on every push
    branches: ['*']          # To any branch
  pull_request:              # Also run on pull requests
    branches: ['*']

jobs:
  test:                       # Define a "test" job
    runs-on: ubuntu-latest   # Run on Ubuntu Linux

    steps:
      - Check out your code      # Step 1: Get the code
      - Set up Python           # Step 2: Install Python 3.11
      - Install dependencies    # Step 3: Install packages
      - Run tests              # Step 4: Run pytest
      - Upload coverage        # Step 5: Save coverage report
```

**In plain English:**
1. GitHub creates a fresh Ubuntu computer
2. Downloads your code
3. Installs Python and your dependencies
4. Runs `pytest` with coverage
5. Saves the results

---

## Viewing Test Results

### On GitHub:

1. **Go to Actions tab**
   ```
   https://github.com/YOUR_USERNAME/local-rag/actions
   ```

2. **See all workflow runs**
   - Green ✅ = Tests passed
   - Red ❌ = Tests failed

3. **Click on any run to see details**
   - Which tests passed/failed
   - Coverage percentage
   - Full test output

### Example Screenshot:
```
✅ Tests - #42 (main)
   Run tests
   ├── ✅ Check out repository
   ├── ✅ Set up Python 3.11
   ├── ✅ Install dependencies
   ├── ✅ Run tests (100 passed)
   └── ✅ Upload coverage

   Duration: 1m 23s
```

---

## What Happens on Each Push?

**Before** (Manual Testing):
```bash
# You had to remember to:
git add .
pytest                    # ← Easy to forget!
git commit -m "changes"
git push
```

**After** (Automatic Testing):
```bash
# Just push:
git add .
git commit -m "changes"
git push

# GitHub automatically runs pytest for you! 🎉
```

---

## Setting Up Coverage Badge (Optional)

A **coverage badge** shows your test coverage on your README:

![Coverage](https://img.shields.io/badge/coverage-100%25-brightgreen)

### Option 1: Using GitHub Actions Badge

Add this to your `README.md`:

```markdown
![Tests](https://github.com/YOUR_USERNAME/local-rag/workflows/Tests/badge.svg)
```

Replace `YOUR_USERNAME` with your actual GitHub username.

### Option 2: Using Codecov (Recommended)

**Codecov** is a free service that provides detailed coverage reports and badges.

#### Setup Steps:

1. **Go to [Codecov.io](https://codecov.io)**
   - Sign in with GitHub

2. **Add your repository**
   - Click "+ Add Repository"
   - Find "local-rag"
   - Copy your upload token

3. **Add token to GitHub Secrets**
   - Go to your repo: Settings → Secrets → Actions
   - Click "New repository secret"
   - Name: `CODECOV_TOKEN`
   - Value: [paste your token]
   - Click "Add secret"

4. **Push your code**
   - Codecov will automatically receive coverage reports
   - Get your badge link from Codecov dashboard

5. **Add badge to README**
   ```markdown
   [![codecov](https://codecov.io/gh/YOUR_USERNAME/local-rag/branch/main/graph/badge.svg)](https://codecov.io/gh/YOUR_USERNAME/local-rag)
   ```

---

## Customizing the Workflows

### Change When Tests Run

**Current**: Tests run on every push to any branch

**Run only on specific branches:**
```yaml
on:
  push:
    branches:
      - main
      - develop
```

**Run on schedule (daily at 9 AM):**
```yaml
on:
  schedule:
    - cron: '0 9 * * *'  # Daily at 9 AM UTC
```

### Add More Python Versions

Test on multiple Python versions:

```yaml
strategy:
  matrix:
    python-version: ['3.9', '3.10', '3.11']
```

This runs tests 3 times, once for each Python version.

### Skip CI for Certain Commits

Add `[skip ci]` to your commit message:

```bash
git commit -m "Update README [skip ci]"
```

Tests won't run for this commit.

---

## Troubleshooting

### ❌ Tests Fail on GitHub but Pass Locally

**Common causes:**

1. **Missing dependencies**
   ```yaml
   # Make sure you install ALL dependencies:
   - pip install -r requirements.txt
   - pip install -r requirements-test.txt
   ```

2. **Different Python version**
   - Check your local Python: `python --version`
   - Update workflow to match

3. **Environment variables**
   - Add secrets in GitHub: Settings → Secrets → Actions

### ❌ Workflow File Not Running

**Check:**
1. File is in `.github/workflows/` directory
2. File ends with `.yml` or `.yaml`
3. YAML syntax is correct (proper indentation)
4. You pushed the file to GitHub

### ❌ Coverage Upload Fails

This is OK! The `fail_ci_if_error: false` setting means:
- Tests will still pass ✅
- Coverage upload is optional
- You can add Codecov token later

---

## Best Practices

### 1. Always Check Test Results
- Click on the ✅ or ❌ in your commits
- Review failed tests before merging

### 2. Don't Skip Failing Tests
- If tests fail, fix them!
- Don't use `[skip ci]` to avoid failures

### 3. Keep Workflows Fast
- Current workflow: ~30 seconds ✅
- If it gets slower, optimize or split workflows

### 4. Use Branch Protection
- Require tests to pass before merging
- Settings → Branches → Add rule
- Check "Require status checks to pass"

---

## Advanced: Branch Protection Rules

**Prevent merging code with failing tests:**

1. Go to **Settings** → **Branches**
2. Click **"Add rule"**
3. Branch name pattern: `main`
4. Check these boxes:
   - ✅ Require a pull request before merging
   - ✅ Require status checks to pass before merging
   - ✅ Require branches to be up to date before merging
5. Select status checks: **Tests**
6. Click **"Create"**

Now you **cannot** merge to main if tests fail! 🛡️

---

## Understanding the Output

### Successful Run ✅
```
====== test session starts ======
platform linux -- Python 3.11.14
collected 100 items

tests/unit/test_csv_processor.py::test_basic... PASSED [  1%]
tests/unit/test_csv_processor.py::test_date... PASSED [  2%]
...
tests/unit/test_models_config.py::test_all... PASSED [100%]

====== 100 passed in 10.26s ======

Coverage: 26.56%
```

### Failed Run ❌
```
====== test session starts ======
...
tests/unit/test_csv_processor.py::test_empty... FAILED

=== FAILURES ===
___ test_empty_csv_handling ___
    def test_empty_csv_handling(self):
        chunks = create_time_based_chunks(str(csv_path))
>       assert chunks == []
E       AssertionError: chunks is None

====== 1 failed, 99 passed in 9.12s ======
```

---

## Cost

**GitHub Actions is FREE for public repositories!** 🎉

For private repositories:
- Free: 2,000 minutes/month
- Your workflow uses ~0.5 minutes per run
- That's ~4,000 runs per month for free!

---

## Quick Reference Commands

```bash
# View workflow status locally
gh run list                    # List recent runs

# View specific run
gh run view <run-id>          # View details

# Watch a workflow run
gh run watch                   # Watch in real-time

# Download artifacts
gh run download <run-id>       # Download test results
```

*Note: Requires [GitHub CLI](https://cli.github.com/) installed*

---

## What's Next?

### Immediate:
1. ✅ Push the workflow files
2. ✅ Check the Actions tab
3. ✅ Watch your first automated test run!

### Soon:
4. 📊 Set up Codecov for coverage badges
5. 🛡️ Add branch protection rules
6. 📧 Configure email notifications

### Future:
7. 🚀 Add deployment workflows
8. 🐳 Add Docker build workflows
9. 📝 Add automatic documentation generation

---

## Getting Help

### GitHub Actions Documentation
- [Getting Started](https://docs.github.com/en/actions/quickstart)
- [Workflow Syntax](https://docs.github.com/en/actions/reference/workflow-syntax-for-github-actions)

### Your Workflow Files
- `.github/workflows/tests.yml` - Test automation
- `.github/workflows/code-quality.yml` - Code checks

### Test Your Changes Locally First
```bash
# Always run tests before pushing:
pytest tests/ -v

# Check if your workflow file is valid:
yamllint .github/workflows/tests.yml
```

---

## Summary

You now have:
- ✅ Automated testing on every push
- ✅ Code quality checks
- ✅ Coverage reporting
- ✅ Professional CI/CD setup

**Your code is automatically tested before it reaches production!** 🎉

The workflows are already configured and ready to use. Just push your code and watch them run!

---

## Example: Full Workflow

Here's what happens when you push code:

```bash
# 1. Make changes
vim csv_processor.py

# 2. Commit and push
git add csv_processor.py
git commit -m "Fix empty CSV handling"
git push origin feature-branch

# 3. GitHub Actions automatically:
#    - Checks out your code
#    - Installs dependencies
#    - Runs 100 tests
#    - Generates coverage report
#    - Shows you the results

# 4. You see the results:
#    ✅ Tests passed!
#    📊 Coverage: 26.56%
#    ⏱️ Duration: 1m 15s

# 5. Create pull request
gh pr create

# 6. Tests run again on PR
#    ✅ All checks passed
#    → Safe to merge!
```

**Welcome to the world of automated testing!** 🚀

---

**Need help?** Check the GitHub Actions tab or open an issue in your repository.
