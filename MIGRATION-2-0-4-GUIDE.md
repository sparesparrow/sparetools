# SpareTools Package Split - Migration Guide (v2.0.4 + v1.0.0)

## 📋 Overview

SpareTools has been refactored into two focused packages for better separation of concerns:

| Package | Type | Purpose | Usage |
|---------|------|---------|-------|
| **sparetools-base/2.0.4** | `python-require` | Recipe helpers (SpareToolsSecurityMixin, SpareToolsVersions) | Conan recipes via `python_requires` |
| **sparetools-python-scripts/1.0.0** | `application` | Runtime utilities (fs, proc, net, scm, logging, security, gui, util) | Build-time scripting via `tool_requires` |

## 🔄 What Changed

### Before (sparetools-base/2.0.3)
```
sparetools-base/
├── Recipe helpers (SpareToolsSecurityMixin)
├── Runtime modules (fs, proc, net, scm, etc.)  ← Mixed responsibilities
├── Test environment (test_env/)
└── 1500+ Python files (~15MB package)
```

**Problems:**
- Mixed concerns (recipe helpers + runtime utilities)
- PYTHONPATH only in buildenv
- Runtime imports unreliable with bundled cpython
- Large package size

### After (Split)
```
sparetools-base/2.0.4              sparetools-python-scripts/1.0.0
├── SpareToolsSecurityMixin        ├── fs/
├── SpareToolsVersions             ├── proc/
└── 2 files (~10KB package)        ├── net/
                                   ├── scm/
                                   ├── logging/
                                   ├── security/
                                   ├── gui/
                                   ├── util/
                                   └── 22 Python files (~100KB package)
```

**Benefits:**
- ✅ Clean separation of concerns
- ✅ Reliable PYTHONPATH (buildenv + runenv)
- ✅ Smaller base package (1500+ files → 2 files)
- ✅ Better for build-time scripting with bundled cpython
- ✅ Independent versioning of recipe helpers

## 🔧 Migration Steps

### For Consumer Packages

1. **Update python_requires version**
   ```python
   # OLD
   python_requires = "sparetools-base/2.0.3"

   # NEW
   python_requires = "sparetools-base/2.0.4"
   ```

2. **Add python-scripts if you use runtime imports**
   ```python
   def build_requirements(self):
       # Add this line
       self.tool_requires("sparetools-python-scripts/1.0.0")
   ```

3. **Keep existing python_requires_extend pattern**
   ```python
   # This stays the same
   python_requires_extend = "sparetools-base.SpareToolsSecurityMixin"
   ```

4. **Test locally**
   ```bash
   conan create . --version=<your-version>
   ```

### Complete Conanfile Example

```python
from conan import ConanFile
from pathlib import Path

class ExampleConan(ConanFile):
    name = "example-package"
    version = "2.0.1"

    # Recipe helpers (for security gates, SBOM, versioning)
    python_requires = "sparetools-base/2.0.4"
    python_requires_extend = "sparetools-base.SpareToolsSecurityMixin"

    def build_requirements(self):
        # Bundled Python interpreter
        self.tool_requires("sparetools-cpython/3.12.8")

        # Runtime utility modules (NEW - needed for imports below)
        self.tool_requires("sparetools-python-scripts/1.0.0")

    def generate(self):
        # Use recipe helper methods
        self.apply_security_gates()
        self.generate_sbom()

        # Use runtime utilities (now work reliably!)
        from sparetools.util.execute_command import execute_command
        from sparetools.fs import find_file, create_zero_copy_environment

        # Example: Find and run a script
        python_exe = self._get_bundled_python()
        script = find_file("processing_script.py", start=self.source_folder)
        exit_code, output = execute_command([str(python_exe), str(script)])

        if exit_code != 0:
            raise RuntimeError(f"Script execution failed: {output}")

    def _get_bundled_python(self):
        """Helper to locate bundled CPython executable"""
        for dep in self.dependencies.build.values():
            if "cpython" in dep.ref.name:
                return Path(dep.package_folder) / "bin" / "python3.12"
        raise RuntimeError("sparetools-cpython not found in build requirements")
```

## 📦 Consumer Packages to Update

The following packages depend on sparetools and should be updated:

**Critical (actively used):**
- [ ] sparetools-mia
- [ ] sparetools-mcp-orchestrator
- [ ] Lennox packages (if used)

**Optional (use as-is if no runtime imports needed):**
- [ ] sparetools-nucleus
- [ ] sparetools-test-framework
- [ ] Other MCP packages

## 🧪 Verification Checklist

After migration:

- [ ] `conan create .` completes without errors
- [ ] All runtime imports work: `from sparetools.util import ...`
- [ ] Recipe helper methods accessible: `self.apply_security_gates()`
- [ ] Local testing passes
- [ ] CI/CD pipeline succeeds

## 📚 Additional Resources

- **sparetools-python-scripts README**: `packages/foundation/sparetools-python-scripts/README.md`
- **Package architecture**: `packages/foundation/sparetools-base/` and `sparetools-python-scripts/`
- **Example usage**: See updated conanfiles in this repository

## ⏰ Deprecation Timeline

- **v2.0.4**: Current (new split architecture)
- **v2.0.3**: Deprecated (use v2.0.4)
- **v2.0.3 removal**: 30 days from now

## ❓ Troubleshooting

### Error: `ModuleNotFoundError: No module named 'sparetools'`
**Cause:** Missing `tool_requires("sparetools-python-scripts/1.0.0")`
```python
def build_requirements(self):
    self.tool_requires("sparetools-python-scripts/1.0.0")  # Add this
```

### Error: `SpareToolsSecurityMixin` not found
**Cause:** Missing `python_requires_extend`
```python
python_requires = "sparetools-base/2.0.4"
python_requires_extend = "sparetools-base.SpareToolsSecurityMixin"  # Add this
```

### Error: Old version still cached
**Solution:** Clear local Conan cache
```bash
conan remove "sparetools-*" -c
```

### Error: Package not found in remote
**Cause:** Packages not yet published
**Solution:** Check Cloudsmith: https://cloudsmith.io/~sparesparrow-conan/repos/sparetools/packages/

## 📝 Version Information

| Package | Old Version | New Version | Status |
|---------|------------|-------------|--------|
| sparetools-base | 2.0.3 | 2.0.4 | ✅ Ready |
| sparetools-python-scripts | N/A | 1.0.0 | ✅ New |

## 🤝 Support

For questions or issues:
1. Check this migration guide
2. Review sparetools-python-scripts/README.md for module docs
3. Open an issue in the sparetools repository
4. Ask in the team Slack/Discord

---

**Last Updated:** 2026-01-11
**Committed:** [7bfc45b](https://github.com/sparesparrow/sparetools/commit/7bfc45b)
**CI/CD Status:** Waiting for automated publishing (check GitHub Actions)
