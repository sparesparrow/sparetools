# Consumer Repository Migration Tasks

This document tracks which consumer repositories need updates for the SpareTools v2.0.4 split.

## Repositories to Update

### High Priority (Critical Path)

#### 1. sparetools-mia
**Status:** Needs update
**Changes Required:**
- [ ] Update `python_requires` from "sparetools-base/2.0.3" to "sparetools-base/2.0.4"
- [ ] Add `tool_requires("sparetools-python-scripts/1.0.0")` in `build_requirements()`
- [ ] Test with `conan create`

**Issue to Create:**
```
Title: Migrate to SpareTools v2.0.4 + v1.0.0 Split
Labels: documentation, migration
Body: See https://github.com/sparesparrow/sparetools/blob/main/MIGRATION-2-0-4-GUIDE.md
```

#### 2. sparetools-mcp-orchestrator
**Status:** Needs update
**Changes Required:**
- [ ] Update `python_requires` from "sparetools-base/2.0.3" to "sparetools-base/2.0.4"
- [ ] Add `tool_requires("sparetools-python-scripts/1.0.0")` in `build_requirements()`
- [ ] Test with `conan create`

#### 3. Lennox Packages (igntab, testing, etc.)
**Status:** Needs update if they use runtime imports
**Changes Required:**
- [ ] Review if sparetools runtime modules are used
- [ ] If yes: Update as above
- [ ] If no: Just bump python_requires version to 2.0.4

### Medium Priority (Active Development)

#### 4. sparetools-nucleus
**Status:** Check if migration needed
**Changes Required:**
- [ ] Verify sparetools imports in conanfile
- [ ] Update if runtime modules used, otherwise just version bump

#### 5. sparetools-test-framework
**Status:** Check if migration needed
**Changes Required:**
- [ ] Verify usage pattern
- [ ] Update accordingly

### Lower Priority (Optional)

#### 6. MCP Packages (mcp-core, mcp-servers, mcp-prompts, etc.)
**Status:** Review for needed changes
**Changes Required:**
- [ ] Only update if they use sparetools modules
- [ ] Most MCP packages may only need version bump

#### 7. Other Packages
- sparetools-obd-sim
- sparetools-prompt-system
- sparetools-versioning
- sparetools-pentest-toolkit
- sparetools-sdr-tools
- sparetools-streaming-solutions
- sparetools-wifi-sensing
- sparetools-crypto-suite
- sparetools-embedded

---

## Migration Process Template

For each consumer repository:

### 1. Check Current Usage
```bash
cd <consumer-repo>
grep -r "sparetools-base" conanfile.py
grep -r "from sparetools" . --include="*.py"
```

### 2. Update conanfile.py

**Before:**
```python
python_requires = "sparetools-base/2.0.3"

# Maybe missing tool_requires:
# self.tool_requires("sparetools-python-scripts/1.0.0")
```

**After:**
```python
python_requires = "sparetools-base/2.0.4"

def build_requirements(self):
    # ... other requirements ...
    self.tool_requires("sparetools-python-scripts/1.0.0")  # ADD THIS
```

### 3. Test Locally
```bash
conan create . --version=<current-version>
```

### 4. Create Pull Request
- Title: "chore: Migrate to SpareTools v2.0.4 + v1.0.0"
- Reference: Link to MIGRATION-2-0-4-GUIDE.md
- Test: Show successful `conan create` output

### 5. Merge & Tag
- Merge to main
- Tag with new version if needed
- CI/CD will republish with new packages

---

## Automated Discovery

To find all consumers:
```bash
# From sparetools root:
find .. -name "conanfile.py" -type f -exec grep -l "sparetools-base" {} \;
```

---

## Timeline

| Date | Phase | Action |
|------|-------|--------|
| 2026-01-11 | 0 | Package split + commit + push ✅ |
| 2026-01-11 | 1 | Create migration guide ✅ |
| 2026-01-12 | 2 | Create issues in consumer repos (waiting for CLI access) |
| 2026-01-12 | 3 | Update high-priority consumers (MIA, MCP-Orchestrator, Lennox) |
| 2026-01-13 | 4 | Update medium-priority consumers |
| 2026-01-13 | 5 | Verify all consumers working |
| 2026-02-11 | 6 | Deprecate sparetools-base/2.0.3 |

---

## Success Criteria

- [ ] All high-priority consumers updated
- [ ] All updated consumers pass CI/CD
- [ ] New versions published to Cloudsmith
- [ ] Migration guide widely distributed
- [ ] No consumer builds broken by split

---

## Notes

- The split is **backward compatible** for packages only using `python_requires`
- Only packages that **import sparetools modules** need the `tool_requires` addition
- No breaking changes to the API - just how packages are consumed
- Most changes are simple version bumps + one line addition

---

## GitHub Issue Template

Save this and create as issue in each consumer repo:

```markdown
## ⚠️ Action Required: Migrate to SpareTools v2.0.4 + v1.0.0 Split

SpareTools has been refactored into two focused packages for better separation of concerns:

### What's Needed

1. Update `python_requires` to `sparetools-base/2.0.4`
2. Add `tool_requires("sparetools-python-scripts/1.0.0")` if using runtime imports

### Migration Guide

Please follow: https://github.com/sparesparrow/sparetools/blob/main/MIGRATION-2-0-4-GUIDE.md

### Why This Matters

- ✅ Smaller base package (1500+ files → 2 files)
- ✅ Reliable runtime imports with bundled cpython
- ✅ Clean separation of recipe helpers vs. runtime utilities
- ✅ Better versioning control

### Timeline

- **Now**: Review and migrate
- **30 days**: Deprecate sparetools-base/2.0.3

### Questions?

See the migration guide or open an issue in sparetools repo.
```

---

**Status:** Ready for consumer repository updates
**Last Updated:** 2026-01-11
