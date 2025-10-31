# SpareTools CI/CD Modernization - Quick Start Guide

**Last Updated:** 2025-10-31
**Status:** ✅ Ready to Deploy

---

## 🚀 Start Here (5 Minutes)

This guide helps you implement the modern CI/CD pipeline for OpenSSL builds.

### Prerequisites Check

```bash
cd /home/sparrow/sparetools
bash scripts/check-prerequisites.sh
```

**Expected Output:**
```
✓ Git 2.30+ (or later)
✓ GitHub CLI authenticated
✓ Conan 2.0+
✓ CMake 3.22+
✓ Perl 5.30+
✓ Python 3.9+
✓ ALL CHECKS PASSED
```

If any checks fail, follow the recommendations in the output.

---

## 📋 Implementation Roadmap

### Phase 1: Deploy Documentation (10 min)

```bash
bash scripts/setup-documentation.sh
```

This script:
- Copies CLAUDE.md to local repository clones
- Updates .gitignore to exclude local clones
- Validates all deployed files
- Generates a deployment report

### Phase 2: Create GitHub Actions (15 min)

Copy the workflow files provided in the CI/CD_MODERNIZATION_GUIDE.md to `.github/workflows/`:

```bash
# Files to create:
.github/workflows/openssl-analysis.yml      # NEW
.github/workflows/build-test.yml            # ENHANCED
.github/workflows/integration.yml           # NEW
```

Or use the automated deployment:
```bash
bash scripts/deploy-workflows.sh
```

### Phase 3: Validate Everything (10 min)

```bash
bash scripts/validate-ci-setup.sh --verbose
```

This validates:
- ✅ GitHub workflows present and valid
- ✅ CLAUDE.md documentation deployed
- ✅ Repository structure correct
- ✅ Conan configuration ready
- ✅ Git configuration complete
- ✅ GitHub integration working

### Phase 4: Push to Repository (5 min)

```bash
git add .
git commit -m "ci: modernize CI/CD for OpenSSL"
git push origin develop
```

### Phase 5: Monitor First Run (15 min)

```bash
# Watch the workflow
gh run watch -w openssl-analysis.yml

# Or check in GitHub
# https://github.com/sparesparrow/sparetools/actions
```

**Expected:**
- openssl-analysis.yml runs first (~3 min)
- Reports OpenSSL version and recommended build method
- Comments on PR with analysis

---

## 📚 Documentation Reference

### For Detailed Implementation
→ **[IMPLEMENTATION_CHECKLIST.md](IMPLEMENTATION_CHECKLIST.md)** (8 phases, 15-18 hours)

### For Architecture Overview
→ **[CI_CD_IMPLEMENTATION_SUMMARY.md](CI_CD_IMPLEMENTATION_SUMMARY.md)** (Overview, scripts, timeline)

### For Advanced Configuration
→ **[CI_CD_MODERNIZATION_GUIDE.md](CI_CD_MODERNIZATION_GUIDE.md)** (8 workflows, 12+ build matrix)

### For OpenSSL 3.6.0 Deep Dive
→ **[OPENSSL-360-BUILD-ANALYSIS.md](OPENSSL-360-BUILD-ANALYSIS.md)** (Technical reference)

---

## 🔧 Automation Scripts

### 1. Check Prerequisites
```bash
bash scripts/check-prerequisites.sh
```
Validates all required tools and configurations.

### 2. Setup Documentation
```bash
bash scripts/setup-documentation.sh
```
Deploys CLAUDE.md files to local clones.

### 3. Deploy Workflows
```bash
bash scripts/deploy-workflows.sh
```
Creates GitHub Actions workflows.

### 4. Validate Setup
```bash
bash scripts/validate-ci-setup.sh
```
Comprehensive validation of all CI/CD components.

---

## ⚡ What Gets Built

### Build Matrix (12+ Configurations)

**Tier 1: Production-Critical (Must Pass)**
- ✅ Linux-GCC11-Perl-Default
- ✅ Linux-GCC11-Perl-FIPS
- ✅ Linux-Clang14-CMake-Default
- ✅ macOS-AppleClang-Perl
- ✅ Windows-MSVC-CMake

**Tier 2: Advanced (Nice to Have)**
- ◐ Linux-GCC11-Minimal
- ◐ Linux-GCC11-Shared
- ◐ Linux-GCC11-Autotools
- ◐ Linux-ARM64-GCC11

**Tier 3: Experimental (Future)**
- ◐ OpenSSL-3.6.0-Perl-Only

### Output: CPS Files

For each configuration, **4 CPS file variants** are generated:
- `openssl-static-release.cps`
- `openssl-static-debug.cps`
- `openssl-shared-release.cps`
- `openssl-shared-debug.cps`

These files integrate with CMake for consumers.

---

## 🔐 GitHub Configuration Required

### 1. GitHub Secrets

Set up Cloudsmith integration:
```bash
gh secret set CLOUDSMITH_API_KEY
# Paste your Cloudsmith API key when prompted
```

### 2. Branch Protection

In GitHub Settings → Branches → Branch protection rules for `develop`:
- ✅ Require status checks to pass before merging
- ✅ Require at least 1 code review approval
- ✅ Dismiss stale pull request approvals when new commits are pushed

### 3. Status Checks Required

These workflows must pass before merging:
- `openssl-analysis` (recommendation step)
- `build-matrix: Linux-GCC11-Perl-Default` (critical)
- `build-matrix: macOS-AppleClang-Perl` (critical)
- `build-matrix: Windows-MSVC-CMake` (critical)

---

## ✅ Success Checklist

### After Phase 1 (Documentation)
- [ ] `bash scripts/setup-documentation.sh` completed
- [ ] CLAUDE.md files deployed to _local-clones/*/
- [ ] Deployment report generated

### After Phase 2 (Workflows)
- [ ] 3 new workflow files created in .github/workflows/
- [ ] All YAML files have valid syntax
- [ ] GitHub secrets configured (CLOUDSMITH_API_KEY)

### After Phase 3 (Validation)
- [ ] `bash scripts/validate-ci-setup.sh` shows ✓ ALL CHECKS PASSED
- [ ] No critical failures or unresolved warnings

### After Phase 4 (Push)
- [ ] Changes committed to develop branch
- [ ] Push to GitHub successful
- [ ] No merge conflicts

### After Phase 5 (Monitoring)
- [ ] openssl-analysis.yml workflow ran successfully
- [ ] Workflow detected OpenSSL version (3.3.2 or 3.6.0)
- [ ] Recommended build method reported
- [ ] PR comment posted with analysis

---

## 🆘 Troubleshooting

### "Perl Configure syntax error"
→ See OPENSSL-360-BUILD-ANALYSIS.md → Validation Checklist

### "CPS files not generated"
→ Check conanfile.py has `self.cpp_info.set_property("cmake_find_mode", "both")`

### "GitHub CLI not authenticated"
→ Run: `gh auth login`

### "Workflow not triggering"
→ Check branch protection rules in Settings → Branches

### "Conan profiles not found"
→ Run: `bash scripts/check-prerequisites.sh --strict`

---

## 📊 Build Timings

**Expected CI/CD Run Times:**

- **openssl-analysis.yml:** ~3 minutes
- **build-matrix (Tier 1):** ~20-25 minutes
- **build-matrix (Tier 2):** ~15-20 minutes (parallel)
- **integration.yml:** ~10-15 minutes
- **security.yml:** ~5-10 minutes

**Total:** ~40-60 minutes for full CI/CD run

---

## 🎯 Key Features

| Feature | Status | Details |
|---------|--------|---------|
| Multi-Platform Support | ✅ | Linux, macOS, Windows, ARM64 |
| Multi-Build Methods | ✅ | Perl, CMake, Autotools, Python |
| CPS File Generation | ✅ | 4 variants per build |
| FIPS Support | ✅ | Conditional FIPS-enabled builds |
| Security Scanning | ✅ | Trivy, Syft, CodeQL |
| Zero-Copy Artifacts | ✅ | Symlinks save 99% disk space |
| Consumer Testing | ✅ | nginx, curl, PostgreSQL, Python |
| Cloudsmith Publishing | ✅ | Automatic package upload |

---

## 📖 Next Steps

### Short-term (Today)
1. Run prerequisite check: `bash scripts/check-prerequisites.sh`
2. Read this file completely
3. Deploy documentation: `bash scripts/setup-documentation.sh`

### Medium-term (This Week)
1. Follow IMPLEMENTATION_CHECKLIST.md Phases 1-4
2. Create and deploy GitHub Actions workflows
3. Run initial workflow tests
4. Validate builds are working

### Long-term (Next 3 Weeks)
1. Complete Phases 5-8 of IMPLEMENTATION_CHECKLIST.md
2. Train team on CI/CD operations
3. Establish monitoring and metrics
4. Plan long-term maintenance

---

## 📞 Questions?

Refer to:
- **CI/CD_IMPLEMENTATION_SUMMARY.md** - Overview and architecture
- **IMPLEMENTATION_CHECKLIST.md** - Detailed step-by-step guide
- **CI_CD_MODERNIZATION_GUIDE.md** - Workflow and configuration details
- **OPENSSL-360-BUILD-ANALYSIS.md** - Technical reference

---

**Ready to start? Run:**
```bash
bash scripts/check-prerequisites.sh
```

Then follow the output recommendations. You should see "✓ ALL CHECKS PASSED" within 2-3 minutes.

Happy building! 🚀
