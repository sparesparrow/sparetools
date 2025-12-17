# Ecosystem Relationships Summary

## Overview

This document summarizes the relationships between OMS projects, SpareTools ecosystem, and related projects (ai-servis), along with recommendations for organizing the SpareTools ecosystem based on proven patterns from the OMS architecture.

## OMS Ecosystem Pattern

### Architecture

```
ngapy-dev (Foundation)
    ↓ build_requires
ngaims-icd-dev (Interface Layer)
    ↓ build_requires
oms-dev (Application)
```

### Key Relationships

1. **ngapy-dev** → Foundation tooling
   - Python utilities (`ngapy/util/`, `ngapy/conan/`, `ngapy/build/`)
   - Test harness (`test_harness/`)
   - Used by all other projects

2. **ngaims-icd-dev** → Interface definitions
   - Depends on: `ngapy-dev` (for utilities)
   - Provides: FlatBuffers schemas, generated headers
   - Used by: `oms-dev`

3. **oms-dev** → Main application
   - Depends on: `ngapy-dev`, `ngaims-icd-dev`
   - Uses: Extensive ngapy utilities
   - Provides: End product

## SpareTools Ecosystem (Current)

### Architecture

```
sparetools-base (Foundation)
    ↓ python_requires
sparetools-cpython (Runtime)
    ↓ tool_requires
sparetools-obd-sim (Application)
    ↓ tool_requires
ai-servis (Consumer)
```

### Current Relationships

1. **sparetools-base** → Foundation utilities
   - Security gates, symlink helpers
   - Used by all packages via `python_requires`

2. **sparetools-cpython** → Bundled Python runtime
   - Python 3.12.7 with zero-copy architecture
   - Used via `tool_requires`

3. **sparetools-obd-sim** → OBD-II simulation
   - Uses: `sparetools-base`, `sparetools-cpython`
   - Used by: `ai-servis` via `tool_requires`

4. **ai-servis** → Consumer application
   - Uses: `sparetools-obd-sim/2.0.0`
   - References: sparetools packages in docs and scripts

## Recommended SpareTools Ecosystem (Based on OMS Pattern)

### Proposed Architecture

```
sparetools-base (Foundation)
    ↓ python_requires
sparetools-cpython (Runtime)
    ↓ tool_requires
sparetools-test-harness (Testing Framework) ← NEW
    ↓ requires
sparetools-icd (Interface Layer) ← NEW
    ↓ build_requires
sparetools-obd-sim (Application)
    ↓ tool_requires
ai-servis (Consumer)
```

### Recommended Relationships

1. **sparetools-base** (Enhanced)
   - Current: Security gates, symlink helpers
   - Add: Test harness utilities, build helpers, config loader

2. **sparetools-cpython** (Unchanged)
   - Bundled Python 3.12.7
   - Zero-copy architecture

3. **sparetools-test-harness** (NEW)
   - ngapy-style test framework
   - Verification methods, JUnit XML
   - Depends on: `sparetools-base`, `sparetools-cpython`

4. **sparetools-icd** (NEW)
   - Protocol definitions (OBD-II, MCP, etc.)
   - Code generation (FlatBuffers, etc.)
   - Depends on: `sparetools-base`, `sparetools-cpython`, `flatbuffers`

5. **sparetools-obd-sim** (Enhanced)
   - Current: OBD-II simulation
   - Add: Dependencies on `sparetools-test-harness`, `sparetools-icd`

6. **ai-servis** (Enhanced)
   - Current: Uses `sparetools-obd-sim`
   - Add: Dependencies on `sparetools-test-harness`, `sparetools-icd`

## Comparison Table

| Layer | OMS Ecosystem | SpareTools (Current) | SpareTools (Proposed) |
|-------|---------------|---------------------|----------------------|
| **Foundation** | ngapy-dev | sparetools-base | sparetools-base (enhanced) |
| **Runtime** | titan-python-environment | sparetools-cpython | sparetools-cpython |
| **Testing** | test_harness/ (in ngapy) | pytest (ad-hoc) | sparetools-test-harness (NEW) |
| **Interface** | ngaims-icd-dev | (none) | sparetools-icd (NEW) |
| **Application** | oms-dev | sparetools-obd-sim | sparetools-obd-sim (enhanced) |
| **Consumer** | (end product) | ai-servis | ai-servis (enhanced) |

## Implementation Roadmap

### Phase 1: Foundation Enhancement
- [ ] Add test harness utilities to `sparetools-base`
- [ ] Add build helpers and configuration loader
- [ ] Add exception handling utilities

### Phase 2: Test Harness Package
- [ ] Create `sparetools-test-harness` package
- [ ] Implement ngapy-compatible API
- [ ] Add JUnit XML output
- [ ] Integrate with pytest

### Phase 3: Interface Layer
- [ ] Create `sparetools-icd` package
- [ ] Define protocol schemas (OBD-II, MCP, etc.)
- [ ] Add code generation tools
- [ ] Version interface definitions

### Phase 4: Application Updates
- [ ] Update `sparetools-obd-sim` to use new packages
- [ ] Update `ai-servis` to use new packages
- [ ] Migrate existing tests to test harness

## Directory Structure

### Correct Location: `~/sparetools`

```
~/sparetools/
├── packages/
│   ├── foundation/
│   │   ├── sparetools-base/
│   │   ├── sparetools-cpython/
│   │   ├── sparetools-test-harness/  ← NEW
│   │   └── sparetools-icd/            ← NEW
│   └── consumers/
│       └── sparetools-obd-sim/
├── scripts/
├── docs/
└── test/
```

### Accidental Location: `~/projects/SpareTools` (TO BE REMOVED)

**Status:** Accidental duplicate with different organizational approach
**Action:** Archive and remove (see `ACCIDENTAL-DIRECTORY-ANALYSIS.md`)

## ai-servis Integration

### Current Integration

```python
# ai-servis/conanfile.py
class MIAConan(ConanFile):
    tool_requires = [
        "sparetools-obd-sim/2.0.0",
    ]
```

### Recommended Integration

```python
# ai-servis/conanfile.py
class MIAConan(ConanFile):
    tool_requires = [
        "sparetools-cpython/3.12.7",      # Bundled Python
        "sparetools-obd-sim/2.0.0",       # OBD simulation
        "sparetools-test-harness/2.0.0",  # Test framework
    ]
    build_requires = [
        "sparetools-icd/2.0.0",           # Protocol definitions
    ]
    python_requires = "sparetools-base/2.0.0"
```

## Benefits of OMS-Inspired Structure

1. **Clear Separation of Concerns**
   - Foundation → Runtime → Testing → Interface → Application

2. **Reusability**
   - Test harness usable across all projects
   - ICD definitions shared between projects
   - Utilities available everywhere

3. **Maintainability**
   - Single source of truth for each layer
   - Versioned interfaces
   - Consistent testing approach

4. **Scalability**
   - Easy to add new applications
   - Easy to extend interfaces
   - Easy to add new test types

## Key Takeaways

1. **OMS Pattern Works Well**
   - Clear dependency hierarchy
   - Reusable components
   - Proven in production

2. **SpareTools Can Adopt Similar Pattern**
   - Foundation layer exists
   - Need to add testing and interface layers
   - Will improve consistency and reusability

3. **Accidental Directory Should Be Removed**
   - Different organizational approach
   - Not connected to git remote
   - Causes confusion

4. **ai-servis Integration Can Be Enhanced**
   - Currently uses only `sparetools-obd-sim`
   - Can benefit from test harness and ICD packages
   - Will improve consistency across projects

## Next Steps

1. ✅ Document relationships (this document)
2. ⬜ Review accidental directory and clean up
3. ⬜ Plan `sparetools-test-harness` package
4. ⬜ Plan `sparetools-icd` package
5. ⬜ Update `sparetools-obd-sim` dependencies
6. ⬜ Update `ai-servis` integration

## Related Documents

- `PROJECT-RELATIONSHIPS-ANALYSIS.md` - Detailed analysis of OMS and SpareTools relationships
- `ACCIDENTAL-DIRECTORY-ANALYSIS.md` - Analysis of accidental `~/projects/SpareTools` directory
- `UNIFIED-TESTING-ENVIRONMENT.md` - Test harness implementation plan
- `UNIFIED-TESTING-IMPROVEMENTS.md` - Improvements based on ngapy analysis
