# GitHub Actions Workflows

This directory contains automated CI/CD workflows for the Local RAG project.

## Available Workflows

### 🧪 Tests (`tests.yml`)
**Purpose**: Run all unit tests with coverage reporting

**Triggers**:
- Every push to any branch
- Every pull request

**What it does**:
1. Sets up Python 3.11
2. Installs all dependencies
3. Runs 100 unit tests
4. Generates coverage report
5. Uploads results to Codecov (optional)
6. Archives test results for 30 days

**Duration**: ~30 seconds

**Badge**:
```markdown
![Tests](https://github.com/YOUR_USERNAME/local-rag/workflows/Tests/badge.svg)
```

---

### 🔍 Code Quality (`code-quality.yml`)
**Purpose**: Check code formatting and style

**Triggers**:
- Every push to any branch
- Every pull request

**What it does**:
1. Checks code formatting with Black
2. Runs Flake8 for style issues
3. Runs Pylint for code quality
4. Reports issues (doesn't fail the build)

**Duration**: ~20 seconds

**Badge**:
```markdown
![Code Quality](https://github.com/YOUR_USERNAME/local-rag/workflows/Code%20Quality/badge.svg)
```

---

## Quick Start

### 1. View Workflow Runs
Go to the **Actions** tab in your GitHub repository:
```
https://github.com/YOUR_USERNAME/local-rag/actions
```

### 2. Check Status
- ✅ Green checkmark = All tests passed
- ❌ Red X = Some tests failed
- 🟡 Yellow circle = Tests are running

### 3. View Details
Click on any workflow run to see:
- Which tests passed/failed
- Coverage percentage
- Full test output
- Downloadable artifacts

---

## Workflow Status

Current test results:
- **100 tests** passing
- **100% pass rate**
- **26.56% overall coverage**
- **100% coverage** on csv_processor.py and models_config.py

---

## Customization

### Run on Specific Branches Only

Edit `tests.yml`:
```yaml
on:
  push:
    branches:
      - main
      - develop
```

### Add More Python Versions

Edit `tests.yml`:
```yaml
strategy:
  matrix:
    python-version: ['3.9', '3.10', '3.11']
```

### Skip CI for Commits

Add `[skip ci]` to commit message:
```bash
git commit -m "Update docs [skip ci]"
```

---

## Secrets Configuration

### Required Secrets: NONE ✅
The workflows run without any secrets.

### Optional Secrets

#### `CODECOV_TOKEN` (for coverage badges)
1. Go to [codecov.io](https://codecov.io)
2. Sign in with GitHub
3. Add your repository
4. Copy the token
5. Add to GitHub: Settings → Secrets → Actions
6. Name: `CODECOV_TOKEN`
7. Value: [your token]

---

## Troubleshooting

### Tests Pass Locally but Fail on GitHub

**Common Issues**:

1. **Missing dependencies**
   - Make sure both `requirements.txt` and `requirements-test.txt` are installed

2. **Python version mismatch**
   - Check local version: `python --version`
   - Workflow uses Python 3.11

3. **Environment differences**
   - GitHub runs on Ubuntu Linux
   - Test locally in similar environment

### Workflow Not Triggering

**Checklist**:
- ✅ File is in `.github/workflows/` directory
- ✅ File extension is `.yml` or `.yaml`
- ✅ YAML syntax is valid (use a validator)
- ✅ File is committed and pushed

### Coverage Upload Fails

This is OK! The workflow is configured with `fail_ci_if_error: false`, so:
- Tests still pass ✅
- You can add Codecov token later
- Coverage is still calculated and shown

---

## Files in this Directory

```
.github/workflows/
├── tests.yml           # Main test workflow
├── code-quality.yml    # Code quality checks
└── README.md          # This file
```

---

## Workflow Architecture

```
Push to GitHub
     ↓
GitHub Actions Detects Push
     ↓
Parallel Execution:
     ├── Run Tests (tests.yml)
     │   ├── Setup Python
     │   ├── Install Dependencies
     │   ├── Run Pytest
     │   └── Upload Coverage
     │
     └── Check Code Quality (code-quality.yml)
         ├── Check Formatting
         ├── Run Flake8
         └── Run Pylint
     ↓
Results Posted to PR/Commit
```

---

## Best Practices

1. **Always check workflow results**
   - Don't ignore failed tests
   - Review the logs

2. **Keep workflows fast**
   - Current: ~30 seconds ✅
   - Target: < 2 minutes

3. **Use branch protection**
   - Require tests to pass
   - Settings → Branches → Add rule

4. **Monitor workflow usage**
   - GitHub provides 2,000 free minutes/month
   - Each run uses ~0.5 minutes

---

## Next Steps

### Immediate
- ✅ Workflows are configured and ready
- ✅ They run automatically on push

### Soon
- [ ] Set up Codecov for coverage badges
- [ ] Add branch protection rules
- [ ] Configure notification preferences

### Future
- [ ] Add deployment workflows
- [ ] Add Docker build workflows
- [ ] Add automatic versioning

---

## Documentation

- **Main Guide**: [`CI_CD_SETUP.md`](../CI_CD_SETUP.md) - Complete beginner guide
- **Test Guide**: [`TEST_GUIDE.md`](../TEST_GUIDE.md) - Running tests locally
- **Test Docs**: [`tests/README.md`](../tests/README.md) - Test suite documentation

---

## Support

**Questions?**
- Check the [CI/CD Setup Guide](../CI_CD_SETUP.md)
- View [GitHub Actions Documentation](https://docs.github.com/en/actions)
- Open an issue in the repository

---

**Status**: ✅ Workflows Active and Ready
**Last Updated**: December 5, 2025
