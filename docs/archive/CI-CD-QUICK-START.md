# SpareTools CI/CD - Quick Start Guide

**Status:** Production-Ready | **Date:** October 31, 2025

---

## ⚡ 5-Minute Setup

Get your CI/CD pipeline running in 5 minutes:

### 1. Verify Prerequisites

```bash
# Check you have the essential tools
gh --version           # GitHub CLI 2.0+
git --version          # Git 2.30+
conan --version        # Conan 2.0+
```

### 2. Configure Cloudsmith Secret

```bash
# Set your Cloudsmith API key (get from https://cloudsmith.io → Settings → API Keys)
gh secret set CLOUDSMITH_API_KEY -R sparesparrow/sparetools

# Verify it's set
gh secret list -R sparesparrow/sparetools
```

### 3. Enable Workflows

Workflows are already in `.github/workflows/` - just push to deploy:

```bash
git add .github/workflows/ CLAUDE.md
git commit -m "ci: enable production CI/CD workflows"
git push origin develop
```

### 4. Watch Workflows Run

```bash
# Monitor in GitHub UI
gh run watch

# Or check CLI
gh run list --limit 5
```

**Done!** 🎉 Your CI/CD pipeline is now active.

---

## 📖 Next Steps by Role

### 👨‍💻 **For Developers**

Read these in order:
1. **This file** (you're reading it!)
2. [GITHUB-SECRETS-SETUP.md](GITHUB-SECRETS-SETUP.md) - Secret configuration
3. [CI-CD-IMPLEMENTATION-COMPLETE.md](CI-CD-IMPLEMENTATION-COMPLETE.md) - How workflows work

**Key commands:**
```bash
# View workflow runs
gh run list --limit 10

# Watch a specific workflow
gh run view <run-id> --log

# Trigger a manual workflow
gh workflow run publish.yml
```

### 🔧 **For DevOps/Operations**

Read these:
1. [CI-CD-OPERATIONS-GUIDE.md](CI-CD-OPERATIONS-GUIDE.md) - Monitoring & maintenance
2. [CI-CD-ARCHITECTURE.md](CI-CD-ARCHITECTURE.md) - Design decisions
3. [CI-CD-TROUBLESHOOTING.md](CI-CD-TROUBLESHOOTING.md) - Common issues

**Key responsibilities:**
- Monitor workflow success rates
- Rotate secrets every 90 days
- Review security scan results
- Troubleshoot workflow failures

### 🏗️ **For Architects**

Review:
1. [CI-CD-ARCHITECTURE.md](CI-CD-ARCHITECTURE.md) - Design patterns
2. [CI-CD-MODERNIZATION-ANALYSIS.md](CI-CD-MODERNIZATION-ANALYSIS.md) - Strategic decisions
3. [OPENSSL-360-BUILD-ANALYSIS.md](OPENSSL-360-BUILD-ANALYSIS.md) - Complex builds

---

## 📊 What's Running

### Active Workflows

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| **ci.yml** | Push to main/develop, PRs | Test on all platforms |
| **publish.yml** | Push to main, tags | Publish to Cloudsmith + GitHub |
| **security.yml** | Push/PR, weekly | Vulnerability scanning |
| **nightly.yml** | Daily 02:00 UTC | Comprehensive testing |
| **reusable/build-package.yml** | Internal use | Shared build logic |

### Build Platforms

- ✅ **Linux:** GCC 11, Clang 18
- ✅ **macOS:** AppleClang (x86_64)
- ✅ **Windows:** MSVC 2022

### Published Packages

- Cloudsmith (primary): https://cloudsmith.io/~sparesparrow-conan/repos/openssl-conan/
- GitHub Packages (for tags): ghcr.io/sparesparrow/*

---

## 🔐 Secrets Required

Only **1 secret is required** to get started:

| Secret | Purpose | Required |
|--------|---------|----------|
| `CLOUDSMITH_API_KEY` | Publish packages | ✅ YES |
| `GITHUB_TOKEN` | GitHub operations | ✅ Automatic |

See [GITHUB-SECRETS-SETUP.md](GITHUB-SECRETS-SETUP.md) for detailed setup.

---

## ✅ Verify Setup

Run this checklist to ensure everything is configured:

- [ ] Cloudsmith API key is set: `gh secret list | grep CLOUDSMITH`
- [ ] All workflows appear in `.github/workflows/`: `ls .github/workflows/*.yml`
- [ ] GitHub Actions is enabled: Settings → Actions → Allow all actions
- [ ] Workflows ran successfully: `gh run list | head -5`

---

## 🚀 Deploy Your First Package

Once setup is complete:

```bash
# 1. Tag a release
git tag v3.3.2
git push origin v3.3.2

# 2. Watch the workflow
gh run watch -w publish.yml

# 3. Verify in Cloudsmith
# https://cloudsmith.io/~sparesparrow-conan/repos/openssl-conan/packages/
```

---

## 📞 Common Tasks

### Run Tests on All Platforms

```bash
# Automatic on push, or trigger manually:
gh workflow run ci.yml
```

### Run Security Scans

```bash
# Automatic weekly, or trigger manually:
gh workflow run security.yml
```

### Run Nightly Tests

```bash
# Automatic daily at 02:00 UTC, or trigger manually:
gh workflow run nightly.yml
```

### Publish to Cloudsmith

```bash
# Automatic on push to main, or trigger manually:
gh workflow run publish.yml
```

---

## 🎯 Key Features

- ✅ **Multi-Platform Testing** - Linux, macOS, Windows
- ✅ **Automatic Publishing** - Cloudsmith + GitHub
- ✅ **Security Scanning** - Trivy, Syft, CodeQL
- ✅ **Nightly Testing** - Comprehensive regression tests
- ✅ **Change Detection** - Skip docs-only changes
- ✅ **Caching** - Fast rebuilds with Conan cache

---

## 📚 Full Documentation

For detailed information, see:

- **[CI-CD-IMPLEMENTATION-COMPLETE.md](CI-CD-IMPLEMENTATION-COMPLETE.md)** - Workflow details
- **[GITHUB-SECRETS-SETUP.md](GITHUB-SECRETS-SETUP.md)** - Secrets configuration
- **[CI-CD-OPERATIONS-GUIDE.md](CI-CD-OPERATIONS-GUIDE.md)** - Monitoring & maintenance
- **[CI-CD-ARCHITECTURE.md](CI-CD-ARCHITECTURE.md)** - Design decisions
- **[CI-CD-TROUBLESHOOTING.md](CI-CD-TROUBLESHOOTING.md)** - Problem solving
- **[OPENSSL-360-BUILD-ANALYSIS.md](OPENSSL-360-BUILD-ANALYSIS.md)** - Complex builds

---

## ❓ Troubleshooting

### Workflow doesn't run on push
- Check GitHub Actions is enabled: Settings → Actions
- Check branch rules don't block workflows
- Verify `.github/workflows/` files exist

### Secret not found in workflow
- Verify secret is set: `gh secret list`
- Wait 1-2 minutes after setting (caching)
- Recreate secret if it's old

### Build fails on specific platform
- See [CI-CD-TROUBLESHOOTING.md](CI-CD-TROUBLESHOOTING.md)
- Check platform-specific issue in logs: `gh run view <id> --log`

---

**You're all set!** Start pushing code and watch your workflows run. 🚀
