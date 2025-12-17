# Project Relationships Analysis: OMS Ecosystem vs SpareTools Ecosystem

## Executive Summary

This document analyzes the relationships between three OMS projects (ngapy-dev, ngaims-icd-dev, oms-dev) and suggests similar relationship patterns for the SpareTools ecosystem, including integration with ai-servis and other related projects.

## OMS Ecosystem Analysis

### Project Hierarchy

```
┌─────────────────────────────────────────────────────────────┐
│                    OMS Ecosystem Structure                   │
└─────────────────────────────────────────────────────────────┘

┌─────────────────┐
│   ngapy-dev      │  Foundation/Tooling Layer
│                 │  - Python utilities (ngapy/)
│                 │  - Conan helpers
│                 │  - Test harness
│                 │  - Build orchestration
└────────┬────────┘
         │ build_requires
         │
         ▼
┌─────────────────┐
│ ngaims-icd-dev  │  Interface Definition Layer
│                 │  - FlatBuffers schema (.fbs)
│                 │  - ICD header generation
│                 │  - Code generation tools
└────────┬────────┘
         │ build_requires
         │
         ▼
┌─────────────────┐
│    oms-dev      │  Application Layer
│                 │  - Main aerospace application
│                 │  - Uses ngapy utilities
│                 │  - Consumes ICD definitions
│                 │  - Multi-target builds (HW/ASE)
└─────────────────┘
```

### Detailed Relationships

#### 1. ngapy-dev (Foundation)

**Purpose:** Core tooling and utilities package

**Key Features:**
- Python package (`ngapy/`) with utilities:
  - `ngapy/util/` - File operations, command execution
  - `ngapy/conan/` - Conan integration helpers
  - `ngapy/build/` - Build orchestration
  - `ngapy/core/` - Core module handlers
  - `ngapy/io_platform/` - I/O interfaces
- Test harness (`test_harness/`)
- Configuration loader (`config_loader/`)
- Product-specific extensions (`product_specific/`)

**Conan Package:**
```python
class NgaPyConan(ConanFile):
    name = 'ngapy'
    build_requires = ['titan-python-environment/3.10.6+dev1']
    python_requires = ['nga-conan-base/master_...']
```

**Usage Pattern:**
- Imported as `build_requires` by other projects
- Provides utilities via `from ngapy.util import ...`
- Used for build orchestration, file operations, Conan helpers

#### 2. ngaims-icd-dev (Interface Layer)

**Purpose:** Interface Control Document (ICD) definitions and code generation

**Key Features:**
- FlatBuffers schema files (`.fbs`)
- C++ header generation from schemas
- Enum extraction and header processing
- ICD structure management

**Conan Package:**
```python
class NgaNgaImsIcdConan(ConanFile):
    name = 'ngaims-icd-dev'
    build_requires = [
        'ngapy/develop_2022_08_15_14.37.18_8fd3ff25',  # ← Depends on ngapy
        'titan-python-environment/3.10.6+dev1',
        'FlatBuffers/2.0.0',
    ]
```

**Relationship:**
- **Depends on:** ngapy-dev (uses `ngapy.util.execute_command` for code generation)
- **Provides:** ICD headers, FlatBuffers generated code
- **Used by:** oms-dev (build_requires)

**Build Process:**
1. Uses ngapy utilities to execute FlatBuffers compiler
2. Generates C++ headers from `.fbs` files
3. Extracts enums and creates extracted headers
4. Packages generated headers

#### 3. oms-dev (Application)

**Purpose:** Main aerospace application

**Key Features:**
- Multi-target builds (HW-dbg, ASE-dbg, etc.)
- Database schema validation
- Product-specific configurations
- OpenSSL integration
- Extensive use of ngapy utilities

**Conan Package:**
```python
class NgaImsConan(ConanFile):
    name = 'ngaims'
    build_requires = [
        'ngapy/develop_2022_11_28_17.18.49_09c61846',  # ← Depends on ngapy
        'ngaims-icd-dev/0.1.21.0',                      # ← Depends on ICD
        # ... 40+ other dependencies
    ]
```

**Relationship:**
- **Depends on:** 
  - ngapy-dev (build utilities, file operations, build orchestration)
  - ngaims-icd-dev (ICD headers, interface definitions)
- **Uses extensively:**
  - `ngapy.util.file_operations` - Symlink management
  - `ngapy.util.execute_command` - Command execution
  - `ngapy.build.build` - Build filtering
  - `ngapy.util.setup_environment` - Environment setup
  - `ngapy.exceptions.ngapy_exceptions` - Error handling

**Key Patterns:**
1. Symlinks ICD package directory into source folder
2. Uses ngapy utilities for all file operations
3. Multi-configuration builds (HW vs ASE)
4. Database schema validation using ngapy utilities

### Relationship Summary

| Project | Type | Depends On | Provides | Used By |
|---------|------|-----------|----------|---------|
| **ngapy-dev** | Foundation | titan-python-environment | Python utilities, test harness, Conan helpers | ngaims-icd-dev, oms-dev |
| **ngaims-icd-dev** | Interface | ngapy-dev, FlatBuffers | ICD headers, generated code | oms-dev |
| **oms-dev** | Application | ngapy-dev, ngaims-icd-dev | Main application | (end product) |

## SpareTools Ecosystem Analysis

### Current Structure

```
┌─────────────────────────────────────────────────────────────┐
│                SpareTools Ecosystem Structure                │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────┐
│ sparetools-base     │  Foundation Layer
│                     │  - Core utilities
│                     │  - Security gates
│                     │  - Symlink helpers
└──────────┬──────────┘
           │ python_requires
           │
           ▼
┌─────────────────────┐
│ sparetools-cpython  │  Runtime Layer
│                     │  - Bundled Python 3.12.7
│                     │  - Zero-copy architecture
└──────────┬──────────┘
           │ tool_requires
           │
           ▼
┌─────────────────────┐
│ sparetools-obd-sim  │  Application Layer
│                     │  - OBD-II simulation
│                     │  - Testing tools
└──────────┬──────────┘
           │ tool_requires (by consumers)
           │
           ▼
┌─────────────────────┐
│    ai-servis        │  Consumer Application
│    (mia)            │  - Uses sparetools-obd-sim
│                     │  - Hardware control
│                     │  - MCP integration
└─────────────────────┘
```

### Suggested Relationship Pattern (Based on OMS)

#### Proposed Structure

```
┌─────────────────────────────────────────────────────────────┐
│          SpareTools Ecosystem (OMS-Inspired Pattern)        │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────┐
│ sparetools-base         │  Foundation (like ngapy-dev)
│                         │  - Core utilities
│                         │  - Security gates
│                         │  - Symlink helpers
│                         │  - Test harness (NEW)
└──────────┬──────────────┘
           │ python_requires
           │
           ▼
┌─────────────────────────┐
│ sparetools-cpython      │  Runtime (like titan-python-env)
│                         │  - Bundled Python 3.12.7
│                         │  - Zero-copy architecture
└──────────┬──────────────┘
           │ tool_requires
           │
           ▼
┌─────────────────────────┐
│ sparetools-test-harness │  Testing Framework (NEW)
│                         │  - ngapy-style test harness
│                         │  - Verification methods
│                         │  - JUnit XML output
└──────────┬──────────────┘
           │ requires
           │
           ▼
┌─────────────────────────┐
│ sparetools-icd          │  Interface Layer (NEW - like ngaims-icd-dev)
│                         │  - Protocol definitions
│                         │  - Code generation
│                         │  - Schema management
└──────────┬──────────────┘
           │ build_requires
           │
           ▼
┌─────────────────────────┐
│ sparetools-obd-sim      │  Application (like oms-dev)
│                         │  - OBD-II simulation
│                         │  - Testing tools
└──────────┬──────────────┘
           │ tool_requires
           │
           ▼
┌─────────────────────────┐
│    ai-servis (mia)      │  Consumer Application
│                         │  - Uses sparetools packages
│                         │  - Hardware control
│                         │  - MCP integration
└─────────────────────────┘
```

### Detailed Recommendations

#### 1. Foundation Layer (sparetools-base)

**Current State:**
- Core utilities (security-gates.py, symlink-helpers.py)
- Python-require package
- Used by all other packages

**Enhancement (Based on ngapy-dev):**
- Add test harness utilities (ngapy-style)
- Add build orchestration helpers
- Add configuration loader
- Add exception handling utilities

**Suggested Structure:**
```
sparetools-base/
├── security-gates.py
├── symlink-helpers.py
├── test-harness.py          # ← NEW (ngapy-style)
├── build-helpers.py         # ← NEW
├── config-loader.py         # ← NEW
└── exceptions.py            # ← NEW
```

#### 2. Test Harness Package (NEW - sparetools-test-harness)

**Purpose:** Unified testing framework (inspired by ngapy test_harness)

**Dependencies:**
```python
class SparetoolsTestHarnessConan(ConanFile):
    name = "sparetools-test-harness"
    tool_requires = "sparetools-cpython/3.12.7"
    python_requires = "sparetools-base/2.0.0"
```

**Features:**
- ngapy-compatible verification API
- JUnit XML output
- Structured logging
- Pytest integration

**Used By:**
- All SpareTools packages (for testing)
- ai-servis (for test infrastructure)
- Other consumer projects

#### 3. Interface Layer (NEW - sparetools-icd)

**Purpose:** Protocol and interface definitions (inspired by ngaims-icd-dev)

**Dependencies:**
```python
class SparetoolsIcdConan(ConanFile):
    name = "sparetools-icd"
    build_requires = [
        "sparetools-base/2.0.0",      # For utilities
        "sparetools-cpython/3.12.7",  # For code generation
        "flatbuffers/23.5.26",        # For schema compilation
    ]
```

**Features:**
- Protocol definitions (OBD-II, MCP, etc.)
- FlatBuffers schema files
- Code generation (C++, Python)
- Interface versioning

**Used By:**
- sparetools-obd-sim (OBD-II protocols)
- ai-servis (MCP protocols, vehicle interfaces)

#### 4. Application Layer (sparetools-obd-sim)

**Current State:**
- OBD-II simulation tools
- Uses sparetools-base and sparetools-cpython

**Enhancement:**
- Add dependency on sparetools-icd (for protocol definitions)
- Add dependency on sparetools-test-harness (for testing)

**Updated Dependencies:**
```python
class SparetoolsObdSimConan(ConanFile):
    name = "sparetools-obd-sim"
    tool_requires = [
        "sparetools-cpython/3.12.7",
        "sparetools-test-harness/2.0.0",  # ← NEW
    ]
    build_requires = [
        "sparetools-icd/2.0.0",  # ← NEW (for OBD-II protocols)
    ]
    python_requires = "sparetools-base/2.0.0"
```

#### 5. Consumer Applications (ai-servis)

**Current State:**
- Uses `sparetools-obd-sim/2.0.0` as tool_requires
- Has its own conanfile.py (mia)

**Enhancement:**
- Add dependency on sparetools-test-harness
- Add dependency on sparetools-icd (for MCP protocols)

**Updated Dependencies:**
```python
class MIAConan(ConanFile):
    name = "mia"
    tool_requires = [
        "sparetools-obd-sim/2.0.0",
        "sparetools-test-harness/2.0.0",  # ← NEW
        "sparetools-cpython/3.12.7",     # ← NEW (explicit)
    ]
    build_requires = [
        "sparetools-icd/2.0.0",  # ← NEW (for MCP/vehicle protocols)
    ]
```

## Comparison Table

| Aspect | OMS Ecosystem | SpareTools Ecosystem (Current) | SpareTools Ecosystem (Proposed) |
|--------|---------------|-------------------------------|--------------------------------|
| **Foundation** | ngapy-dev | sparetools-base | sparetools-base (enhanced) |
| **Runtime** | titan-python-environment | sparetools-cpython | sparetools-cpython |
| **Testing** | test_harness/ (in ngapy) | pytest (ad-hoc) | sparetools-test-harness (NEW) |
| **Interface** | ngaims-icd-dev | (none) | sparetools-icd (NEW) |
| **Application** | oms-dev | sparetools-obd-sim | sparetools-obd-sim (enhanced) |
| **Consumer** | (end product) | ai-servis | ai-servis (enhanced) |

## Implementation Recommendations

### Phase 1: Foundation Enhancement
1. Add test harness utilities to sparetools-base
2. Add build helpers and configuration loader
3. Add exception handling utilities

### Phase 2: Test Harness Package
1. Create sparetools-test-harness package
2. Implement ngapy-compatible API
3. Add JUnit XML output
4. Integrate with pytest

### Phase 3: Interface Layer
1. Create sparetools-icd package
2. Define protocol schemas (OBD-II, MCP, etc.)
3. Add code generation tools
4. Version interface definitions

### Phase 4: Application Updates
1. Update sparetools-obd-sim to use new packages
2. Update ai-servis to use new packages
3. Migrate existing tests to test harness

## Directory Structure Recommendations

### Current SpareTools Structure
```
~/sparetools/                    # ← CORRECT location
├── packages/
│   ├── foundation/
│   │   ├── sparetools-base/
│   │   └── sparetools-cpython/
│   └── consumers/
│       └── sparetools-obd-sim/
└── ...
```

### Accidental Duplicate
```
~/projects/SpareTools/           # ← ACCIDENTAL (should be removed)
├── consumers/                   # Different structure
├── foundation/                  # Different structure
└── docs/                       # Different structure
```

### Recommended Structure (After Enhancements)
```
~/sparetools/                    # ← CORRECT location
├── packages/
│   ├── foundation/
│   │   ├── sparetools-base/         # Enhanced
│   │   ├── sparetools-cpython/
│   │   ├── sparetools-test-harness/ # NEW
│   │   └── sparetools-icd/          # NEW
│   └── consumers/
│       └── sparetools-obd-sim/      # Enhanced
└── ...
```

## ai-servis Integration

### Current Integration
- Uses `sparetools-obd-sim/2.0.0` as tool_requires
- References sparetools packages in documentation
- Uses sparetools-cpython in bootstrap scripts

### Recommended Integration
```python
# ai-servis/conanfile.py
class MIAConan(ConanFile):
    name = "mia"
    
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

## Migration Path

### For Existing Projects

1. **Update sparetools-base:**
   - Add test harness utilities
   - Add build helpers
   - Maintain backward compatibility

2. **Create new packages:**
   - sparetools-test-harness
   - sparetools-icd

3. **Update existing packages:**
   - sparetools-obd-sim: Add dependencies on new packages
   - Maintain backward compatibility

4. **Update consumers:**
   - ai-servis: Gradually adopt new packages
   - Other consumers: Optional migration

### For New Projects

1. Use unified bootstrap script
2. Automatically get all SpareTools packages
3. Use test harness from day one
4. Use ICD definitions for protocols

## Benefits of OMS-Inspired Structure

1. **Clear Separation of Concerns:**
   - Foundation → Runtime → Testing → Interface → Application

2. **Reusability:**
   - Test harness usable across all projects
   - ICD definitions shared between projects
   - Utilities available everywhere

3. **Maintainability:**
   - Single source of truth for each layer
   - Versioned interfaces
   - Consistent testing approach

4. **Scalability:**
   - Easy to add new applications
   - Easy to extend interfaces
   - Easy to add new test types

## Action Items

### Immediate
1. ✅ Document current relationships (this document)
2. ⬜ Remove accidental ~/projects/SpareTools (or document differences)
3. ⬜ Plan sparetools-test-harness package

### Short-term
1. ⬜ Create sparetools-test-harness package
2. ⬜ Enhance sparetools-base with utilities
3. ⬜ Update sparetools-obd-sim dependencies

### Long-term
1. ⬜ Create sparetools-icd package
2. ⬜ Migrate ai-servis to new structure
3. ⬜ Create unified bootstrap script

## Notes on Accidental Directory

**Location:** `~/projects/SpareTools`

**Status:** Accidental duplicate (should only exist at `~/sparetools`)

**Differences:**
- Different directory structure (consumers/ vs packages/consumers/)
- Different documentation structure
- Appears to be a different organizational approach

**Recommendation:**
1. Compare structures to understand differences
2. Decide which structure to keep
3. Migrate useful content to correct location
4. Remove accidental directory

## Conclusion

The OMS ecosystem demonstrates a clear layered architecture:
- **Foundation** (ngapy-dev) → **Interface** (ngaims-icd-dev) → **Application** (oms-dev)

SpareTools can adopt a similar pattern:
- **Foundation** (sparetools-base) → **Testing** (sparetools-test-harness) → **Interface** (sparetools-icd) → **Application** (sparetools-obd-sim) → **Consumer** (ai-servis)

This structure provides:
- Clear dependencies
- Reusable components
- Consistent testing
- Versioned interfaces
- Scalable architecture
