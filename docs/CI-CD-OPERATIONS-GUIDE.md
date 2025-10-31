# CI/CD Operations Guide

**Date:** October 31, 2025 | **Status:** Production | **Audience:** DevOps, Operations

---

## Overview

This guide covers daily operations, monitoring, maintenance, and troubleshooting of the SpareTools CI/CD pipeline.

---

## 📊 Daily Monitoring

### Morning Checklist (5 minutes)

```bash
#!/bin/bash
# Run each morning to verify pipeline health

echo "=== SpareTools CI/CD Daily Check ==="

# 1. Check recent workflow runs
echo "Recent Runs:"
gh run list --limit 10 --status completed

# 2. Check for failures
echo "Failed Runs:"
gh run list --limit 20 --status failure

# 3. Check nightly test results
echo "Nightly Status:"
gh run list --workflow=nightly.yml --limit 5

# 4. Check security scan results
echo "Security Scan Status:"
gh run list --workflow=security.yml --limit 3
```

### Key Metrics to Track

- **CI Success Rate:** Should be >95% on main branch
- **Build Time:** Should be <15 minutes per platform
- **Security Scan Results:** 0 CRITICAL vulnerabilities
- **Nightly Test Status:** All platforms passing

### Alerting Setup

Monitor these GitHub Actions notifications:
1. **Workflow failures** - Immediate attention required
2. **Security findings** - Review daily
3. **Nightly test failures** - Creates GitHub issues automatically
4. **Long-running builds** - >20 minutes indicates performance issue

---

## 🔄 Weekly Maintenance

### Monday Morning (15 minutes)

```bash
#!/bin/bash
# Weekly maintenance checklist

echo "=== Weekly Maintenance ==="

# 1. Review security scan results
echo "Security Summary (past 7 days):"
gh run list --workflow=security.yml --limit 7 --status completed

# 2. Check nightly test trend
echo "Nightly Test Trend:"
gh run list --workflow=nightly.yml --limit 7

# 3. Monitor artifact storage
echo "Recent Artifact Sizes:"
# Check GitHub Actions storage usage
# Settings → Billing and plans → Actions → Storage

# 4. Review workflow logs
echo "Checking for warnings/errors..."
# Download and review logs
gh run download $(gh run list --limit 1 --jq '.[] | .databaseId')
```

### Weekly Tasks

- [ ] Review failed workflow logs
- [ ] Check security scan trends
- [ ] Monitor build time trends
- [ ] Verify Cloudsmith uploads
- [ ] Check GitHub Actions storage usage

### Performance Baseline

Track these metrics weekly:

```bash
# Create a metrics summary
cat > build-metrics-$(date +%Y-%m-%d).json << 'EOF'
{
  "date": "2025-10-31",
  "ci_success_rate": "98.5%",
  "avg_build_time_linux": "8.2 minutes",
  "avg_build_time_macos": "12.5 minutes",
  "avg_build_time_windows": "14.1 minutes",
  "security_critical": 0,
  "security_high": 2,
  "nightly_passes": 24,
  "artifact_size_gb": 45.2
}
EOF
```

---

## 🔐 Security & Secret Management

### Secret Rotation Schedule

**Every 90 Days:**

```bash
#!/bin/bash
# Rotate Cloudsmith API key

echo "🔄 Rotating CLOUDSMITH_API_KEY"

# 1. Generate new key in Cloudsmith
# https://cloudsmith.io → Settings → API Keys → Create New

# 2. Update GitHub secret
read -s -p "Enter new Cloudsmith API key: " NEW_KEY
gh secret set CLOUDSMITH_API_KEY -R sparesparrow/sparetools << EOF
$NEW_KEY
EOF

# 3. Revoke old key in Cloudsmith
echo "⚠️  Remember to revoke old API key in Cloudsmith UI"

# 4. Verify new key works
gh workflow run publish.yml

echo "✅ Key rotation complete"
```

### Secret Access Audit

```bash
#!/bin/bash
# Review secret access in GitHub Actions logs

echo "=== Secret Access Audit ==="

# 1. List all workflows that use secrets
grep -r "secrets\." .github/workflows/ | grep -v node_modules

# 2. Check publish.yml specifically
echo "Workflows using CLOUDSMITH_API_KEY:"
grep -l "CLOUDSMITH_API_KEY" .github/workflows/*.yml

# 3. Review access logs
echo "Access logs available at:"
echo "https://github.com/sparesparrow/sparetools/settings/audit-log"
```

### Security Best Practices

✅ **Do:**
- Rotate secrets every 90 days
- Use least-privilege API keys
- Monitor secret access in logs
- Audit GitHub Actions history monthly

❌ **Don't:**
- Commit secrets to repository
- Log secret values in workflow output
- Use personal access tokens as secrets
- Share secrets via Slack/email

---

## 🛠️ Troubleshooting Workflows

### Workflow Won't Trigger

**Check these:**
1. Is GitHub Actions enabled? Settings → Actions → Allow all actions
2. Is the workflow file valid YAML? Run `yamllint .github/workflows/*.yml`
3. Are branch protection rules blocking it? Settings → Branches
4. Is the trigger condition met? (push to main/develop, tag, etc.)

```bash
# Validate all workflows
for file in .github/workflows/*.yml; do
    echo "Checking $file..."
    python3 -m yaml "$file" && echo "✅ Valid" || echo "❌ Invalid"
done
```

### Workflow Runs But Fails

**Check the logs:**
```bash
# Get latest run
RUN_ID=$(gh run list --limit 1 --jq '.[] | .databaseId')

# View detailed logs
gh run view $RUN_ID --log

# Download all logs
gh run download $RUN_ID
```

**Common failures:**
- Secret not set → Check GITHUB-SECRETS-SETUP.md
- Conan cache issue → Clear cache: `conan cache clean "*"`
- Platform-specific error → Check logs for platform (Linux/macOS/Windows)

---

## 📈 Build Performance Optimization

### Monitoring Build Times

```bash
#!/bin/bash
# Track build time trends

for i in {1..10}; do
    gh run list --workflow=ci.yml --limit $i | tail -1 | \
    awk '{print $3, $2}' # Duration, status
done
```

### Optimization Strategies

**If builds are >15 minutes:**

1. **Enable Conan cache:** Already enabled, but verify:
   ```bash
   grep "cache:" .github/workflows/ci.yml
   ```

2. **Parallel builds:** Tier 2/3 configurations run in parallel
   ```bash
   grep "continue-on-error:" .github/workflows/ci.yml
   ```

3. **Skip unnecessary builds:**
   ```bash
   grep "change-detection:" .github/workflows/ci.yml
   ```

4. **Use smaller test matrix for dev**:
   - Tier 1 (critical) always runs
   - Tier 2 (advanced) can be skipped in PR
   - Tier 3 (experimental) only on schedule

---

## 📦 Package Publishing

### Publishing Process

1. **Commit to main** → ci.yml validates
2. **Create version tag** → publish.yml triggers
3. **Upload to Cloudsmith** → Dual-registry publishing
4. **Create GitHub Release** → Automatic release notes

### Verify Published Packages

```bash
# Check Cloudsmith
conan remote add sparesparrow-conan https://conan.cloudsmith.io/sparesparrow-conan/openssl-conan/
conan search "*" -r sparesparrow-conan

# Check GitHub Packages
gh release list --repo sparesparrow/sparetools
```

---

## 📅 Maintenance Schedule

### Daily (5 min)
- [ ] Check workflow status
- [ ] Review any failures

### Weekly (15 min)
- [ ] Review security scans
- [ ] Check performance trends
- [ ] Audit artifact storage

### Monthly (30 min)
- [ ] Review GitHub Actions logs
- [ ] Update documentation
- [ ] Plan performance improvements

### Quarterly (1 hour)
- [ ] Rotate secrets
- [ ] Update dependencies
- [ ] Review and update build matrix
- [ ] Capacity planning

### Annually (2 hours)
- [ ] Comprehensive security audit
- [ ] Performance optimization review
- [ ] Update CI/CD strategy
- [ ] Plan major updates

---

## 📊 Reporting

### Weekly Status Report

```bash
#!/bin/bash
# Generate weekly status

cat > weekly-report-$(date +%Y-W%V).md << 'EOF'
# Weekly CI/CD Report

**Week:** $(date +%Y-W%V)

## Summary
- CI Success Rate: [X]%
- Build Time Trend: [improving/stable/degrading]
- Security Findings: [X]
- Nightly Tests: [X] passed, [X] failed

## Top Issues
1. [Issue 1]
2. [Issue 2]

## Recommendations
- [Action 1]
- [Action 2]

---
Generated: $(date)
EOF

echo "✅ Report generated: weekly-report-$(date +%Y-W%V).md"
```

---

## 🔗 Related Documentation

- [CI-CD-QUICK-START.md](CI-CD-QUICK-START.md) - Getting started
- [CI-CD-IMPLEMENTATION-COMPLETE.md](CI-CD-IMPLEMENTATION-COMPLETE.md) - Technical details
- [GITHUB-SECRETS-SETUP.md](GITHUB-SECRETS-SETUP.md) - Secrets configuration
- [CI-CD-TROUBLESHOOTING.md](CI-CD-TROUBLESHOOTING.md) - Problem solving

---

## 📞 Escalation Path

**Level 1 (Ops Team):** Workflow failures, secret issues
**Level 2 (DevOps Lead):** Performance degradation, security issues
**Level 3 (Architecture):** Design changes, major updates

---

**Last Updated:** October 31, 2025
