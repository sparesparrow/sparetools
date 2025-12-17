# SpareTools Monorepo Migration: Detailed Checklist

**Status:** Planning  
**Created:** December 13, 2025  
**Target Completion:** Q1 2026

---

## Overview

This checklist provides granular task breakdown for the 16-week migration plan outlined in SPARETOOLS-MONOREPO-PLAN.md. Each section maps to implementation phases with specific deliverables, validation gates, and rollback procedures.

---

## 🔵 Phase 1: Foundation Setup (Weeks 1-2)

### Directory Structure Creation

- [ ] Create root-level directories
  ```bash
  mkdir -p .github .tooling docs scripts tools examples workspaces _Build
  mkdir -p packages/foundation packages/consumers
  ```
  - [ ] Verify directory tree matches Part 1 of plan
  - [ ] Initialize .gitignore entries for _Build/
  - [ ] Create .github/CODEOWNERS file

- [ ] Create foundation package directories
  ```bash
  cd packages/foundation
  mkdir -p {sparetools-base,sparetools-bootstrap,sparetools-shared-dev-tools,sparetools-cpython}/{src,tests,docs,scripts}
  ```
  - [ ] Verify structure for each package
  - [ ] Create placeholder README.md in each
  - [ ] Validate with: `find packages/foundation -type d | wc -l`

- [ ] Create consumer domain structure
  ```bash
  cd packages/consumers
  mkdir -p {openssl,mia,mcp,audio}/{sparetools-*/src,sparetools-*/tests,sparetools-*/docs}
  ```
  - [ ] Verify all 8+ consumer packages have structure
  - [ ] Create .consumer.yaml in each domain directory
  - [ ] Validate with: `find packages/consumers -name ".consumer.yaml" | wc -l`

### Scripts Directory Setup

- [ ] Create scripts/ subdirectories
  ```bash
  mkdir -p scripts/{bootstrap,build,validation,ci-cd,deployment,utilities,testing}
  ```
  - [ ] Copy existing scripts from packages/
  - [ ] Create README.md for each scripts/ subdirectory
  - [ ] Establish ownership in CODEOWNERS

- [ ] Create recipe_base.py
  - [ ] Define SpareToolsBaseConan class
  - [ ] Define OpenSSLBaseConan class
  - [ ] Define ConsumerPackageConan class
  - [ ] Write unit tests: `test_recipe_base.py`
  - [ ] Run: `pytest scripts/test_recipe_base.py -v`

### Documentation Hub

- [ ] Create docs/ structure
  - [ ] Create docs/README.md (entry point)
  - [ ] Create docs/INDEX.md (placeholder for auto-generation)
  - [ ] Create docs/{foundation,consumers,operations,integration,security,development,api,examples,glossary,templates}/ directories
  - [ ] Copy existing docs to appropriate locations
  - [ ] Update all relative links in copied docs

- [ ] Create documentation templates
  - [ ] docs/templates/PACKAGE-README-TEMPLATE.md
  - [ ] docs/templates/CONSUMER-INTEGRATION-TEMPLATE.md
  - [ ] docs/templates/API-REFERENCE-TEMPLATE.md
  - [ ] docs/templates/CHANGELOG-TEMPLATE.md

### Consumer Configuration Files

- [ ] Create .consumer.yaml for each domain
  - [ ] packages/consumers/openssl/.consumer.yaml
  - [ ] packages/consumers/mia/.consumer.yaml
  - [ ] packages/consumers/mcp/.consumer.yaml
  - [ ] packages/consumers/audio/.consumer.yaml
  - [ ] Create validation schema: `schemas/consumer.schema.json`
  - [ ] Validate all .consumer.yaml: `scripts/validation/validate-consumer-yaml.py`

### Phase 1 Validation Gate

- [ ] Directory structure complete
  - [ ] Run: `python3 scripts/utilities/validate-structure.py`
  - [ ] Expected output: All checks ✅
  - [ ] No broken symlinks: `find . -type l ! -exec test -e {} \;`

- [ ] Documentation hub initialized
  - [ ] All required directories exist
  - [ ] All templates present
  - [ ] No doc orphans

- [ ] Consumer metadata complete
  - [ ] All .consumer.yaml files valid
  - [ ] All domain directories have metadata
  - [ ] Schema validation passes

**Rollback:** `git checkout HEAD -- packages/ docs/ scripts/` (if not committed yet)

---

## 🟢 Phase 2: Foundation Package Migration (Weeks 3-4)

### sparetools-base Migration

- [ ] Extract sparetools-base
  - [ ] Verify current location: `find . -name "sparetools-base" -type d`
  - [ ] Copy to: `packages/foundation/sparetools-base/`
  - [ ] Verify conanfile.py present and valid
  - [ ] Check export() method references correct paths

- [ ] Update sparetools-base conanfile.py
  - [ ] Remove old export_folder settings
  - [ ] Update python_requires list
  - [ ] Verify no absolute paths
  - [ ] Run: `conan export .`
  - [ ] Verify: `conan list "sparetools-base/*"`

- [ ] Test sparetools-base
  - [ ] Run: `conan create . --version=2.0.0`
  - [ ] Verify build succeeds
  - [ ] Check exported functions available: `python3 -c "from sparetools_base import *; print('OK')"`

### sparetools-bootstrap Migration

- [ ] Extract sparetools-bootstrap
  - [ ] Copy to: `packages/foundation/sparetools-bootstrap/`
  - [ ] Verify directory structure
  - [ ] **FIX ISSUE #4**: Add missing python_requires declaration
    ```python
    python_requires = "sparetools-base/2.0.0", "sparetools-shared-dev-tools/2.0.0"
    ```
  - [ ] Verify conanfile.py is valid

- [ ] Update bootstrap scripts
  - [ ] Update: `scripts/bootstrap/complete-bootstrap.py`
    - [ ] All imports point to new location
    - [ ] All path references use relative paths
    - [ ] Test with: `./scripts/bootstrap/complete-bootstrap.py --dry-run`

- [ ] Test sparetools-bootstrap
  - [ ] Run: `conan create packages/foundation/sparetools-bootstrap --version=2.0.0`
  - [ ] Verify orchestration agent available
  - [ ] Verify FIPS validator available

### sparetools-shared-dev-tools Migration

- [ ] Extract sparetools-shared-dev-tools
  - [ ] Copy to: `packages/foundation/sparetools-shared-dev-tools/`
  - [ ] Update conanfile.py: add python_requires for sparetools-base
  - [ ] Update all script references

- [ ] Verify shared-dev-tools
  - [ ] Check exports in conanfile.py
  - [ ] Verify all scripts present
  - [ ] Test: `conan create . --version=2.0.0`

### sparetools-cpython Migration

- [ ] Extract sparetools-cpython
  - [ ] Copy to: `packages/foundation/sparetools-cpython/`
  - [ ] Verify conanfile.py
  - [ ] Update build-scripts/ paths

- [ ] Create platform patches
  - [ ] If not present: patches/macos-arm64.patch
  - [ ] If not present: patches/windows-msvc.patch
  - [ ] If not present: patches/linux-musl.patch
  - [ ] Document patch application in build-scripts/build-cpython.sh

- [ ] Test sparetools-cpython
  - [ ] Run: `conan create . --version=3.12.7`
  - [ ] Verify binary exports (bin/python3, bin/pip3)
  - [ ] Verify conf_info (user.cpython:executable, user.cpython:home)

### Update Cross-References

- [ ] Find all conanfile.py files
  ```bash
  find packages/ -name "conanfile.py" -type f
  ```

- [ ] Update each conanfile.py
  - [ ] If python_requires: Update to point to sparetools-base
  - [ ] If tool_requires: Update to point to sparetools-cpython
  - [ ] If references old package paths: Update to new paths
  - [ ] Validate syntax: `python3 -m py_compile <file>`

- [ ] Update CI/CD workflows
  - [ ] .github/workflows/*.yml: Update package paths
  - [ ] Update conan commands to use new Conan remote paths
  - [ ] Validate with: `python3 scripts/validation/validate-workflows.py`

### Phase 2 Validation Gate

- [ ] All foundation packages migrated
  - [ ] Run: `conan list "sparetools-*/*"`
  - [ ] Verify 4 packages present:
    - [ ] sparetools-base/2.0.0
    - [ ] sparetools-bootstrap/2.0.0
    - [ ] sparetools-shared-dev-tools/2.0.0
    - [ ] sparetools-cpython/3.12.7

- [ ] Package dependencies resolved
  - [ ] Run: `conan graph info packages/foundation/sparetools-bootstrap`
  - [ ] Verify no unresolved dependencies
  - [ ] Verify dependency tree correct

- [ ] All exports valid
  - [ ] Can import sparetools_base in Python
  - [ ] Can import sparetools_bootstrap
  - [ ] Can import sparetools_shared_dev_tools

**Rollback:** `git checkout HEAD -- packages/foundation/`

---

## 🟡 Phase 3: Consumer Package Migration (Weeks 5-8)

### OpenSSL Consumer Migration

- [ ] Migrate sparetools-openssl
  - [ ] Copy to: `packages/consumers/openssl/sparetools-openssl/`
  - [ ] Update conanfile.py
    - [ ] Add: `python_requires = "sparetools-base/2.0.0"`
    - [ ] Update: `tool_requires = "sparetools-cpython/3.12.7", "sparetools-openssl-tools/2.0.0"`
    - [ ] Verify build methods paths (perl_configure.py, cmake_build.py, etc.)
  - [ ] Test: `conan create . --version=3.3.2 --build=missing`

- [ ] Migrate sparetools-openssl-tools
  - [ ] Copy to: `packages/consumers/openssl/sparetools-openssl-tools/`
  - [ ] Update conanfile.py with python_requires
  - [ ] Update profile paths: `profiles/base/`, `profiles/build-methods/`, `profiles/features/`
  - [ ] Test: `conan create . --version=2.0.0`

- [ ] Create openssl/.consumer.yaml
  - [ ] Name: "openssl"
  - [ ] Display name: "OpenSSL Package Suite"
  - [ ] List both packages
  - [ ] Define CI workflows: build-openssl, test-openssl-variants, security-scan-openssl
  - [ ] Define platforms: linux (x86_64, aarch64), macos (x86_64, arm64), windows (x86_64)

### MIA Consumer Migration

- [ ] Migrate sparetools-mia
  - [ ] Copy to: `packages/consumers/mia/sparetools-mia/`
  - [ ] Update conanfile.py
    - [ ] Add python_requires for sparetools-base
    - [ ] Add requires: sparetools-openssl/3.3.2
    - [ ] Add tool_requires: sparetools-cpython/3.12.7
  - [ ] Test: `conan create . --version=2.0.0 --build=missing`

- [ ] Migrate sparetools-obd-sim
  - [ ] Copy to: `packages/consumers/mia/sparetools-obd-sim/`
  - [ ] Update bootstrap script: `scripts/bootstrap-obd.py`
    - [ ] Update CPython Cloudsmith URL
    - [ ] Verify platform detection
    - [ ] Test with: `./scripts/bootstrap-obd.py --dry-run`
  - [ ] Test: `conan create . --version=2.0.0`

- [ ] Create mia/.consumer.yaml
  - [ ] Name: "mia"
  - [ ] Display name: "MIA IoT Architecture"
  - [ ] List sparetools-mia and sparetools-obd-sim
  - [ ] Define dependencies: requires openssl consumer
  - [ ] Define CI workflows

### MCP Consumer Migration

- [ ] Migrate sparetools-mcp-orchestrator
  - [ ] Copy to: `packages/consumers/mcp/sparetools-mcp-orchestrator/`
  - [ ] Update conanfile.py
    - [ ] Add python_requires for sparetools-base
    - [ ] Add tool_requires for sparetools-cpython
  - [ ] Verify prompts/ directory (700+ templates)
  - [ ] Test: `conan create . --version=2.0.0`

- [ ] Migrate sparetools-tinymcp (if present)
  - [ ] Copy to: `packages/consumers/mcp/sparetools-tinymcp/`
  - [ ] Update conanfile.py

- [ ] Migrate sparetools-mcpserver-cpp (if present)
  - [ ] Copy to: `packages/consumers/mcp/sparetools-mcpserver-cpp/`
  - [ ] Update conanfile.py
  - [ ] Verify C++ source files

- [ ] Create mcp/.consumer.yaml

### Audio Consumer Migration

- [ ] Migrate sparetools-rtp-midi
  - [ ] Copy to: `packages/consumers/audio/sparetools-rtp-midi/`
  - [ ] Update conanfile.py
  - [ ] Test: `conan create . --version=2.0.0`

- [ ] Create audio/.consumer.yaml

### Cross-Consumer Integration

- [ ] Update all conanfile.py requires
  - [ ] sparetools-mia depends on sparetools-openssl: ✅
  - [ ] sparetools-mcp-orchestrator depends on sparetools-openssl (optional): ✅
  - [ ] Verify dependency resolution: `conan graph info packages/consumers/mia/sparetools-mia`

- [ ] Create cross-consumer test suite
  - [ ] Test: OpenSSL → MIA (OBD-II over encrypted)
  - [ ] Test: OpenSSL → MCP (secure MCP)
  - [ ] Test: MIA → MCP (orchestration)
  - [ ] Test: All → CPython (runtime isolation)

### Phase 3 Validation Gate

- [ ] All consumer packages migrated
  - [ ] Run: `find packages/consumers -name "conanfile.py" | wc -l`
  - [ ] Expected: 8+ conanfiles

- [ ] All .consumer.yaml files created
  - [ ] Run: `find packages/consumers -name ".consumer.yaml" | wc -l`
  - [ ] Expected: 5+ files

- [ ] Cross-consumer dependencies resolve
  - [ ] Run: `python3 scripts/validation/validate-cross-consumer-deps.py`
  - [ ] Expected: All graphs valid

**Rollback:** `git checkout HEAD -- packages/consumers/`

---

## 🟠 Phase 4: Automation & CI/CD (Weeks 9-12)

### Shared Scripts Development

- [ ] Create scripts/bootstrap/platform-detect.py
  - [ ] Detect OS (Linux, macOS, Windows)
  - [ ] Detect architecture (x86_64, aarch64, arm64)
  - [ ] Detect system Python version
  - [ ] Test with: `python3 scripts/bootstrap/platform-detect.py`

- [ ] Create scripts/bootstrap/cpython-fetch.py
  - [ ] Download from Cloudsmith
  - [ ] Verify checksums
  - [ ] Extract atomically
  - [ ] Test with: `python3 scripts/bootstrap/cpython-fetch.py --dry-run`

- [ ] Create scripts/build/build-orchestrator.py
  - [ ] Accept --consumer, --package, --platform flags
  - [ ] Generate build matrix
  - [ ] Execute builds serially/parallel
  - [ ] Collect artifacts
  - [ ] Test with: `python3 scripts/build/build-orchestrator.py --dry-run`

- [ ] Create scripts/validation/security-scan.py
  - [ ] Run Trivy scan
  - [ ] Generate SBOM (Syft)
  - [ ] Output JSON report
  - [ ] Test with: `python3 scripts/validation/security-scan.py --help`

- [ ] Create scripts/ci-cd/matrix-generator.py
  - [ ] Read .consumer.yaml files
  - [ ] Generate GitHub Actions matrix JSON
  - [ ] Include platform, consumer, package combinations
  - [ ] Test with: `python3 scripts/ci-cd/matrix-generator.py --output matrix.json`

- [ ] Create scripts/utilities/workspace-generator.py
  - [ ] Read .consumer.yaml
  - [ ] Generate VS Code workspace JSON
  - [ ] Create workspaces/ files
  - [ ] Test: `python3 scripts/utilities/workspace-generator.py --all`

### Documentation Automation

- [ ] Create scripts/utilities/doc-linker.py
  - [ ] generate_master_index() - create INDEX.md
  - [ ] link_related_docs() - insert cross-references
  - [ ] validate_links() - verify all links valid
  - [ ] generate_api_docs() - extract docstrings
  - [ ] Test: `python3 scripts/utilities/doc-linker.py --regenerate`

- [ ] Create documentation generation workflow
  - [ ] On push to docs/: run doc-linker.py
  - [ ] Auto-commit generated docs (INDEX.md, API docs)
  - [ ] Validate all links in PR checks

### CI/CD Workflows

- [ ] Create .github/workflows/build-matrix.yml
  - [ ] generate-matrix job: runs matrix-generator.py
  - [ ] build job: matrix strategy with all combinations
  - [ ] Test workflow locally with: `act -j build`

- [ ] Create per-consumer workflows
  - [ ] .github/workflows/consumer-openssl.yml
  - [ ] .github/workflows/consumer-mia.yml
  - [ ] .github/workflows/consumer-mcp.yml
  - [ ] .github/workflows/consumer-audio.yml
  - [ ] Each runs consumer-specific tests

- [ ] Create validation workflows
  - [ ] .github/workflows/validate-packages.yml
  - [ ] .github/workflows/security-gates.yml
  - [ ] .github/workflows/cross-consumer-integration.yml

- [ ] Create release workflow
  - [ ] .github/workflows/release.yml
  - [ ] Trigger on version tags: v2.x.x
  - [ ] Build all packages
  - [ ] Upload to Cloudsmith
  - [ ] Generate release notes

### Validation Framework

- [ ] Create scripts/validation/tier1-syntax.py
  - [ ] Validate all conanfile.py syntax
  - [ ] Check YAML files (consumer configs)
  - [ ] Validate JSON files (schemas, configs)
  - [ ] Test: `python3 scripts/validation/tier1-syntax.py`

- [ ] Create scripts/validation/tier2-dependencies.py
  - [ ] Resolve dependency graphs
  - [ ] Check for circular dependencies
  - [ ] Verify all requires/tool_requires exist
  - [ ] Test: `python3 scripts/validation/tier2-dependencies.py`

- [ ] Create scripts/validation/tier3-cross-consumer.py
  - [ ] Test cross-consumer builds
  - [ ] Verify MIA can use OpenSSL
  - [ ] Verify MCP can use OpenSSL (optional)
  - [ ] Test: `python3 scripts/validation/tier3-cross-consumer.py`

- [ ] Create scripts/validation/tier4-integration.py
  - [ ] Run integration test suite
  - [ ] Test real-world scenarios
  - [ ] Verify all examples build
  - [ ] Test: `python3 scripts/validation/tier4-integration.py`

- [ ] Create scripts/validation/tier5-security.py
  - [ ] Run security gates
  - [ ] Generate SBOMs
  - [ ] Check FIPS compliance
  - [ ] Run supply chain verification
  - [ ] Test: `python3 scripts/validation/tier5-security.py`

### Phase 4 Validation Gate

- [ ] All shared scripts created and tested
  - [ ] Run: `python3 scripts/bootstrap/platform-detect.py`
  - [ ] Run: `python3 scripts/build/build-orchestrator.py --dry-run`
  - [ ] Run: `python3 scripts/validation/security-scan.py --help`

- [ ] CI/CD workflows functional
  - [ ] Validate workflow syntax: `python3 -m json.tool .github/workflows/*.yml > /dev/null`
  - [ ] Test locally with: `act -j build`
  - [ ] Verify all environments set correctly

- [ ] Validation framework complete
  - [ ] Run all 5 tiers: `python3 scripts/validation/tier*.py`
  - [ ] Expected: All pass
  - [ ] Generate coverage report: `python3 scripts/validation/coverage-report.py`

**Rollback:** `git checkout HEAD -- scripts/ .github/workflows/`

---

## 🟣 Phase 5: Developer Experience (Weeks 13-16)

### Workspace Generation

- [ ] Generate root workspace
  - [ ] Run: `python3 scripts/utilities/workspace-generator.py --root`
  - [ ] Creates: `workspaces/root.code-workspace`
  - [ ] Verify in VS Code: `code workspaces/root.code-workspace`

- [ ] Generate foundation workspace
  - [ ] Run: `python3 scripts/utilities/workspace-generator.py --foundation`
  - [ ] Creates: `workspaces/foundation.code-workspace`

- [ ] Generate per-consumer workspaces
  - [ ] Run: `python3 scripts/utilities/workspace-generator.py --consumer openssl`
  - [ ] Run: `python3 scripts/utilities/workspace-generator.py --consumer mia`
  - [ ] Run: `python3 scripts/utilities/workspace-generator.py --consumer mcp`
  - [ ] Run: `python3 scripts/utilities/workspace-generator.py --consumer audio`
  - [ ] Verify each opens correctly in VS Code

- [ ] Generate development workspaces
  - [ ] workspaces/development/recipe-dev.code-workspace
  - [ ] workspaces/development/python-dev.code-workspace
  - [ ] workspaces/development/cpp-dev.code-workspace

- [ ] Generate CI/CD workspaces
  - [ ] workspaces/ci-cd/testing.code-workspace
  - [ ] workspaces/ci-cd/security.code-workspace
  - [ ] workspaces/ci-cd/documentation.code-workspace

### Documentation Completion

- [ ] Generate master documentation
  - [ ] Run: `python3 scripts/utilities/doc-linker.py --regenerate`
  - [ ] Creates: docs/INDEX.md with TOC
  - [ ] Creates: docs/api/*.md with API reference
  - [ ] Creates: Cross-links in all docs

- [ ] Create consumer integration examples
  - [ ] examples/openssl-basic/conanfile.py
  - [ ] examples/openssl-advanced/conanfile.py
  - [ ] examples/mia-consumer/conanfile.py
  - [ ] examples/mcp-consumer/conanfile.py
  - [ ] Test each: `cd examples/*/; conan install . --build=missing`

- [ ] Create developer guides
  - [ ] docs/development/LOCAL-DEVELOPMENT.md
  - [ ] docs/development/WORKSPACE-SETUP.md
  - [ ] docs/development/DEBUGGING-GUIDE.md
  - [ ] docs/development/TESTING-STRATEGY.md

- [ ] Create quick-start guides per consumer
  - [ ] docs/consumers/openssl/QUICKSTART.md
  - [ ] docs/consumers/mia/QUICKSTART.md
  - [ ] docs/consumers/mcp/QUICKSTART.md
  - [ ] docs/consumers/audio/QUICKSTART.md

### Integration Examples

- [ ] Create basic OpenSSL consumer example
  ```python
  # examples/openssl-basic/conanfile.py
  from conan import ConanFile
  
  class ExampleConsumer(ConanFile):
      requires = "sparetools-openssl/3.3.2"
      
      def generate(self):
          # Generate dependency info
          pass
  ```
  - [ ] Test: `conan install . --build=missing`
  - [ ] Verify OpenSSL libraries available

- [ ] Create MIA consumer example
  ```python
  # examples/mia-consumer/conanfile.py
  class ExampleConsumer(ConanFile):
      requires = ["sparetools-openssl/3.3.2", "sparetools-mia/2.0.0"]
      
      def generate(self):
          pass
  ```
  - [ ] Test: `conan install . --build=missing`
  - [ ] Verify both packages available

- [ ] Create cross-consumer integration example
  - [ ] Example using OpenSSL in MCP context
  - [ ] Example using MIA with MCP orchestration
  - [ ] Document patterns and best practices

### Training & Onboarding

- [ ] Create new developer checklist
  - [ ] docs/NEWDEV-CHECKLIST.md
  - [ ] Step 1: Clone repo
  - [ ] Step 2: Install requirements
  - [ ] Step 3: Open workspace
  - [ ] Step 4: Run first build
  - [ ] Step 5: Run tests

- [ ] Create FAQ
  - [ ] docs/FAQ.md
  - [ ] Common questions per consumer
  - [ ] Troubleshooting common issues
  - [ ] Links to deeper documentation

- [ ] Create glossary
  - [ ] docs/glossary/CONAN-TERMINOLOGY.md
  - [ ] docs/glossary/OPENSSL-TERMINOLOGY.md
  - [ ] docs/glossary/MCP-TERMINOLOGY.md

### Phase 5 Validation Gate

- [ ] All workspaces functional
  - [ ] Count workspaces: `find workspaces -name "*.code-workspace" | wc -l`
  - [ ] Expected: 12+ workspaces
  - [ ] Validate each workspace JSON: `python3 -m json.tool workspaces/*.code-workspace > /dev/null`
  - [ ] Test opening in VS Code (manual)

- [ ] Documentation complete
  - [ ] Verify docs/INDEX.md exists
  - [ ] Verify docs/api/ populated
  - [ ] Verify all examples build: `for ex in examples/*/; do (cd $ex; conan install . --build=missing); done`
  - [ ] Verify all links valid: `python3 scripts/utilities/doc-linker.py --validate`

- [ ] Onboarding materials complete
  - [ ] docs/NEWDEV-CHECKLIST.md exists
  - [ ] docs/FAQ.md exists
  - [ ] All glossaries exist

**Rollback:** `git checkout HEAD -- docs/ examples/ workspaces/`

---

## 📊 Cross-Phase Validation Checkpoints

### After Each Phase

**Run comprehensive validation:**

```bash
# Phase validation script
python3 scripts/validation/comprehensive-check.py \
  --phase $PHASE_NUMBER \
  --consumers openssl,mia,mcp,audio \
  --report report-phase-$PHASE_NUMBER.json
```

**Verify no regressions:**

```bash
# Run full test suite
pytest tests/ -v --cov=scripts --cov=packages --cov-report=html

# Run integration tests
python3 scripts/validation/tier3-cross-consumer.py
python3 scripts/validation/tier4-integration.py
```

**Check CI/CD health:**

```bash
# Simulate GitHub Actions locally
act -j build --input consumer=openssl
act -j build --input consumer=mia
```

---

## 🎯 Success Criteria Per Phase

### Phase 1: Foundation Setup
- [ ] All directories created (0 errors)
- [ ] All .consumer.yaml files valid (0 validation errors)
- [ ] docs/ structure complete (all templates present)
- [ ] scripts/ organized (bootstrap, build, validation, ci-cd, utilities, testing)

### Phase 2: Foundation Package Migration
- [ ] 4 foundation packages in Conan
- [ ] All exports working (no ModuleNotFoundError)
- [ ] All conanfile.py syntax valid
- [ ] `conan list "sparetools-*/*"` returns all packages

### Phase 3: Consumer Package Migration
- [ ] 8+ consumer packages in Conan
- [ ] All .consumer.yaml files created (5 domains)
- [ ] Cross-consumer dependencies resolve
- [ ] No unresolved python_requires
- [ ] Cross-consumer test suite runs (0 failures)

### Phase 4: Automation & CI/CD
- [ ] All 5 validation tiers pass
- [ ] Build matrix generates correctly
- [ ] All workflows validate (no syntax errors)
- [ ] Security gates pass
- [ ] Artifacts upload to Cloudsmith successfully

### Phase 5: Developer Experience
- [ ] 12+ workspaces functional
- [ ] docs/INDEX.md generated with TOC
- [ ] docs/api/ populated with all APIs
- [ ] 4+ integration examples build successfully
- [ ] Developer checklist and FAQ complete

---

## 🚨 Rollback Procedures

**If any phase fails validation:**

### Quick Rollback
```bash
# Rollback to last good commit
git revert HEAD --no-edit

# Or specific directory
git checkout HEAD -- packages/
```

### Selective Rollback
```bash
# Restore one consumer
git checkout HEAD -- packages/consumers/openssl/

# Restore one package
git checkout HEAD -- packages/foundation/sparetools-base/
```

### Full Rollback
```bash
# Start over from main
git checkout main
git pull
git checkout -b migration-retry
```

---

## 📝 Deliverables Checklist

### Phase 1 Deliverables
- [ ] Directory structure diagram (ASCII or Mermaid)
- [ ] Consumer.yaml schema (JSON Schema)
- [ ] scripts/utilities/validate-structure.py (tool)

### Phase 2 Deliverables
- [ ] Migration completion report (4 packages)
- [ ] Updated conanfile.py files (all 4)
- [ ] Build test results (conan create output)

### Phase 3 Deliverables
- [ ] Consumer package inventory (8+ packages)
- [ ] Cross-consumer integration test results
- [ ] Dependency graph diagrams (per consumer)

### Phase 4 Deliverables
- [ ] Scripts documentation (docstrings)
- [ ] CI/CD workflow diagrams
- [ ] Validation framework architecture document
- [ ] Build matrix examples (JSON)

### Phase 5 Deliverables
- [ ] Workspace directory listing
- [ ] docs/INDEX.md (auto-generated)
- [ ] docs/api/ reference (auto-generated)
- [ ] Integration examples (4+ functional)
- [ ] Developer onboarding guide

---

## 📞 Getting Help

**Issue during migration?** Refer to:

1. **Phase details** - Above in this checklist
2. **Architecture plan** - SPARETOOLS-MONOREPO-PLAN.md
3. **Validation** - scripts/validation/tier*.py
4. **Rollback** - Rollback Procedures section above

**Create issue with:**
- Phase number
- Specific step failing
- Error output (full traceback)
- Platform info (`uname -a`, `conan --version`, `python --version`)

---

**Checklist Version:** 1.0  
**Created:** December 13, 2025  
**Last Updated:** December 13, 2025  
**Status:** Ready for Phase 1 Kickoff
