# Contributing to SpareTools

Thank you for your interest in contributing to SpareTools! This guide will help you get started.

## 🚀 Quick Start

```bash
# Fork and clone
git clone https://github.com/YOUR_USERNAME/sparetools.git
cd sparetools

# Install dependencies
pip install conan==2.21.0 pytest pytest-cov ruff pylint mypy

# Build packages
conan create packages/sparetools-base --version=2.0.0
conan create packages/sparetools-openssl --version=3.3.2 --build=missing

# Run tests
pytest test/unit/ -v
conan test packages/sparetools-openssl/test_package sparetools-openssl/3.3.2
```

## 📋 Contribution Workflow

1. **Create a branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Follow existing code style
   - Add tests for new features
   - Update documentation

3. **Test your changes**
   ```bash
   # Run unit tests
   pytest test/unit/ -v --cov=packages

   # Validate conanfiles
   find packages -name "conanfile.py" -exec python -m py_compile {} \;

   # Run integration tests
   conan test packages/*/test_package/* --build=missing
   ```

4. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat: your feature description"
   ```

5. **Push and create PR**
   ```bash
   git push origin feature/your-feature-name
   gh pr create --title "feat: Your Feature" --body "Description..."
   ```

## 📝 Commit Message Format

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Adding tests
- `chore`: Maintenance tasks

**Examples:**
```
feat(openssl): add support for OpenSSL 3.6.0
fix(cpython): correct macOS build flags
docs(readme): update quick start guide
test(base): add unit tests for symlink helpers
```

## 🧪 Testing Requirements

### Unit Tests
- Add tests for new functionality
- Maintain >60% coverage
- Use pytest conventions

```python
# test/unit/test_your_feature.py
def test_your_function():
    result = your_function(input)
    assert result == expected
```

### Integration Tests
- Add test_package/ for new Conan packages
- Test against actual Conan workflow

```python
# packages/your-package/test_package/conanfile.py
class TestConan(ConanFile):
    def test(self):
        # Test package functionality
        pass
```

## 🎨 Code Style

### Python
```bash
# Format with ruff
ruff check packages/

# Type checking
mypy packages/

# Lint
pylint packages/
```

### Conanfile.py
- Use Conan 2.x API (`buildenv_info`, `runenv_info`)
- Follow existing package patterns
- Document options and configurations

```python
class YourPackageConan(ConanFile):
    name = "sparetools-your-package"
    version = "1.0.0"
    package_type = "python-require"  # or "library", "application"

    def package_info(self):
        # Use modern Conan 2.x API
        self.buildenv_info.append_path("PYTHONPATH", self.package_folder)
```

## 📦 Adding a New Package

1. **Create package directory**
   ```bash
   mkdir -p packages/sparetools-your-package
   cd packages/sparetools-your-package
   ```

2. **Add conanfile.py**
   ```python
   from conan import ConanFile

   class YourPackageConan(ConanFile):
       name = "sparetools-your-package"
       version = "1.0.0"
       # ... rest of conanfile
   ```

3. **Add README.md** (use template in `docs/PACKAGE-README-TEMPLATE.md`)

4. **Add test_package/**
   ```bash
   mkdir test_package
   # Add conanfile.py to test_package/
   ```

5. **Update root documentation**
   - Add to package table in README.md
   - Add to docs/PACKAGES.md
   - Update dependency graphs if needed

## 🔄 Pull Request Process

1. **Ensure CI passes**
   - All builds succeed (Linux GCC/Clang)
   - Security scans clear
   - Tests pass

2. **Update documentation**
   - README.md if user-facing changes
   - CHANGELOG.md for notable changes
   - Package READMEs if package-specific

3. **Request review**
   - Tag relevant maintainers
   - Respond to feedback
   - Update PR as needed

4. **Squash and merge**
   - Maintainers will squash commits
   - Ensure commit message follows conventions

## 🐛 Reporting Issues

Use [GitHub Issues](https://github.com/sparesparrow/sparetools/issues) with:

- **Bug reports**: Include steps to reproduce, expected vs actual behavior
- **Feature requests**: Describe use case and proposed solution
- **Questions**: Check docs first, then ask in [Discussions](https://github.com/sparesparrow/sparetools/discussions)

### Bug Report Template
```markdown
**Environment:**
- OS: Linux/macOS/Windows
- Conan version: 2.21.0
- Python version: 3.12.7
- Package version: 3.3.2

**Steps to reproduce:**
1. conan create ...
2. ...

**Expected behavior:**
...

**Actual behavior:**
...

**Logs:**
```
...
```
```

## 📚 Resources

- [Conan 2.x Documentation](https://docs.conan.io/2/)
- [GitHub Actions](https://docs.github.com/en/actions)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [Python Packaging Guide](https://packaging.python.org/)

## 🤝 Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow
- Follow project guidelines

## 📜 License

By contributing, you agree that your contributions will be licensed under the Apache License 2.0.

---

**Questions?** Open a [Discussion](https://github.com/sparesparrow/sparetools/discussions) or reach out in [Issues](https://github.com/sparesparrow/sparetools/issues).
