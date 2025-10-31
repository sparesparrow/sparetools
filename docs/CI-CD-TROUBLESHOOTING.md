# CI/CD Troubleshooting Guide

**Status:** Production | **Last Updated:** October 31, 2025

Quick solutions for common CI/CD issues.

---

## Workflow Issues

### Issue: "Workflow doesn't run on push"

**Check:**
```bash
# 1. Verify GitHub Actions is enabled
# Settings → Actions → Allow all actions

# 2. Check workflow file exists
ls -la .github/workflows/ci.yml

# 3. Validate YAML syntax
python3 -c "import yaml; yaml.safe_load(open('.github/workflows/ci.yml'))"

# 4. Check branch protection
# Settings → Branches → develop → Check status checks
```

**Solution:**
- Enable GitHub Actions in Settings
- Fix YAML syntax errors
- Remove branch protection blocks if needed
- Ensure .github/ directory is committed

---

### Issue: "Workflow runs but fails immediately"

**Check logs:**
```bash
gh run list --limit 5
gh run view <run-id> --log
```

**Common causes:**
1. Secret not set → See [Secret Issues](#secret-issues)
2. Syntax error → Check workflow YAML
3. Missing dependency → Check conanfile.py
4. Permissions issue → Check workflow permissions

**Solution:**
```bash
# Rerun workflow after fixing issue
gh run rerun <run-id>
```

---

### Issue: "Workflow hangs/times out"

**Causes:**
- Large build taking >6 hours
- Network connectivity issue
- GitHub Actions outage

**Check:**
```bash
# Monitor job duration
gh run view <run-id> --log | grep -i "duration\|timeout"

# Check GitHub status
# https://www.githubstatus.com/
```

**Solution:**
- Increase timeout if legitimate long build
- Check Conan cache is working (should speed up)
- Split into smaller jobs if possible

---

## Secret Issues

### Issue: "CLOUDSMITH_API_KEY secret missing"

**Fix:**
```bash
# 1. Check if secret exists
gh secret list -R sparesparrow/sparetools

# 2. If missing, set it
gh secret set CLOUDSMITH_API_KEY -R sparesparrow/sparetools
# Paste your key when prompted

# 3. Verify (should show in list)
gh secret list -R sparesparrow/sparetools
```

**Note:** Secrets take 1-2 minutes to propagate. Try rerunning workflow.

---

### Issue: "Authentication failed - invalid API key"

**Check:**
```bash
# 1. Verify key is correct format
echo $CLOUDSMITH_API_KEY | wc -c  # Should be ~32 chars

# 2. Test authentication locally
conan remote login sparesparrow-conan sparesparrow \
  --password "$CLOUDSMITH_API_KEY"

# 3. Check key permissions in Cloudsmith
# https://cloudsmith.io → Settings → API Keys
```

**Solution:**
- Generate new API key in Cloudsmith
- Update GitHub secret: `gh secret set CLOUDSMITH_API_KEY`
- Revoke old key in Cloudsmith

---

### Issue: "Workflow has no access to secrets"

**Check:**
```bash
# Only happen if using fork or workflow_dispatch from PR

# Solution: GitHub requires explicit approval
# Actions → Latest run → Approve and run
```

---

## Build Issues

### Issue: "Conan dependency not found"

**Error:** `ERROR: Remote 'conancenter' doesn't have recipe...`

**Fix:**
```bash
# 1. Verify Conan is using right remotes
conan remote list

# 2. Update Conan remotes
conan remote add conancenter \
  https://center.conan.io --index=0

# 3. Search for package
conan search sparetools-base/2.0.0 -r conancenter
```

---

### Issue: "Build fails on specific platform (Linux/macOS/Windows)"

**Check platform logs:**
```bash
# Get workflow run ID
RUN_ID=$(gh run list --limit 1 --jq '.[] | .databaseId')

# Download all logs
gh run download $RUN_ID

# Check platform-specific logs
ls -la logs/
```

**Platform-specific issues:**

**Linux (GCC/Clang):**
- Missing development headers: `apt-get install build-essential`
- GCC version mismatch: Check GCC version in runner

**macOS (AppleClang):**
- Xcode version: `xcode-select --install`
- M1/M2 ARM64 support: May need special flags

**Windows (MSVC):**
- Visual Studio version: Must be 2019+
- PATH issues: Check `%MSVC_PATH%` is set
- Long path issues: Enable long path support

---

### Issue: "Out of disk space"

**Error:** `No space left on device`

**Causes:**
- Large artifacts not cleaned up
- Conan cache too large
- Multiple parallel builds on same runner

**Fix:**
```bash
# Check disk usage
df -h

# Clean Conan cache (if needed)
conan cache clean "*" --confirm

# Remove old artifacts locally
gh run list --status completed | tail -n +20 | \
  awk '{print $1}' | xargs -I {} gh run delete {} --confirm
```

---

## Package Publishing Issues

### Issue: "Upload to Cloudsmith failed"

**Check:**
```bash
# 1. Verify Cloudsmith credentials
conan remote list

# 2. Test upload locally
conan create . --version=3.3.2
conan upload sparetools-openssl/3.3.2@ -r sparesparrow-conan

# 3. Check API key permissions
# Cloudsmith → Settings → API Keys → Verify "Write" permission
```

**Solution:**
- Verify CLOUDSMITH_API_KEY secret is set
- Check API key has write permissions
- Retry publish workflow: `gh workflow run publish.yml`

---

### Issue: "Package already exists in Cloudsmith"

**Cause:** Trying to upload duplicate version

**Fix:**
```bash
# Option 1: Increment version and retry
# Edit conanfile.py, change version to X.Y.Z+1

# Option 2: Delete package in Cloudsmith UI and retry
# Cloudsmith UI → openssl-conan → find package → Delete

# Option 3: Force push (not recommended)
conan upload sparetools-openssl/3.3.2@ -r sparesparrow-conan \
  --force --confirm
```

---

## Caching Issues

### Issue: "Cache not working - builds are slow"

**Check:**
```bash
# Look for cache hit in logs
gh run view <run-id> --log | grep -i "cache\|hit"
```

**Should see:**
```
Cache hit: False (first run)
...
Saving to cache...
Cache saved!
```

**If not saving:**
1. Check `.github/workflows/ci.yml` has cache action
2. Check conanfile lock file hasn't changed
3. Check Conan cache directory path is correct

---

### Issue: "Corrupt cache causing build failures"

**Fix:**
```bash
# Clear entire cache
gh run list --workflow=ci.yml --limit 1 --jq '.[] | .databaseId' | \
  xargs -I {} gh api repos/:owner/:repo/actions/caches -X DELETE \
    --input '{"key": "conan-*"}'

# Or manually clear local cache
rm -rf ~/.conan2/p/*
conan cache clean "*"

# Rerun workflow
gh run rerun <run-id>
```

---

## Security Scanning Issues

### Issue: "Trivy scan fails"

**Causes:**
- Trivy database outdated
- Format error in dockerfile
- Permission denied

**Fix:**
```bash
# Check Trivy database
trivy image --severity CRITICAL

# Update database
trivy image --download-db-only

# Verbose mode
trivy fs --debug .
```

---

### Issue: "CodeQL fails with 'Autoinstall failed'"

**Cause:** No Python/JavaScript files found

**Fix:**
```bash
# CodeQL is optional - failures don't block workflow
# To disable: Remove CodeQL step from security.yml

# To fix: Ensure Python files exist
find . -name "*.py" -type f | head -5
```

---

### Issue: "SBOM generation fails"

**Cause:** Syft version incompatibility

**Fix:**
```bash
# Update Syft to latest
syft version

# Run manually
syft dir:. -o spdx-json > sbom.spdx.json
```

---

## Nightly Test Issues

### Issue: "Nightly tests fail but ci.yml passes"

**Causes:**
- Nightly has extended test matrix (more platforms)
- Nightly runs longer, may hit platform-specific issues
- Configuration differences

**Fix:**
```bash
# Check what nightly matrix includes
grep "matrix:" .github/workflows/nightly.yml

# Run locally with same config
conan create . --profile:b=profiles/nightly/linux-arm64.profile

# Fix issue and commit
git push origin develop

# Nightly will auto-rerun next scheduled time
```

---

### Issue: "Nightly auto-creates issue on failure"

**This is expected behavior.** Issues auto-close when test passes.

**To disable:**
```bash
# Edit nightly.yml and remove "create-issue" step
# Or set continue-on-error: true
```

---

## General Debugging

### Enable Workflow Debug Logging

```bash
# Set environment variable
gh secret set ACTIONS_STEP_DEBUG true -R sparesparrow/sparetools

# Run workflow
gh workflow run ci.yml

# Check logs (very verbose)
gh run view <run-id> --log | head -200
```

**Warning:** Debug logs are very large. Disable after debugging:
```bash
gh secret delete ACTIONS_STEP_DEBUG -R sparesparrow/sparetools
```

---

### Rerun Failed Workflow

```bash
# Rerun entire workflow
gh run rerun <run-id>

# Rerun failed jobs only
gh run rerun <run-id> --failed
```

---

### Download Workflow Artifacts

```bash
# List available artifacts
gh run view <run-id> --json artifacts

# Download all
gh run download <run-id> -D artifacts/

# Download specific artifact
gh run download <run-id> -n "linux-artifacts"
```

---

### Compare Workflow Runs

```bash
# Show run durations
gh run list --workflow=ci.yml | head -10 | \
  awk '{print $2, $3, $4}'

# Show success rate trend
gh run list --workflow=ci.yml --limit 20 --status completed | \
  awk '{print $3}' | sort | uniq -c
```

---

## Escalation

### Level 1: Self-Service
- Check this guide
- Review workflow logs
- Check GitHub Actions status page

### Level 2: Team Review
- Ask team on Slack
- Check GitHub Discussions
- Review recent commits for issues

### Level 3: Report Bug
- Create GitHub Issue with:
  - Workflow name and run ID
  - Error logs (full output)
  - Platform/configuration affected
  - Steps to reproduce

---

## References

- [GitHub Actions Troubleshooting](https://docs.github.com/en/actions/learn-github-actions/workflow-syntax-for-github-actions)
- [Conan Troubleshooting](https://docs.conan.io/2/reference/cli.html)
- [Cloudsmith Support](https://help.cloudsmith.io/)
- [GitHub Status](https://www.githubstatus.com/)

---

**Still stuck?** Check related docs:
- [CI-CD-IMPLEMENTATION-COMPLETE.md](CI-CD-IMPLEMENTATION-COMPLETE.md) - Workflow details
- [GITHUB-SECRETS-SETUP.md](GITHUB-SECRETS-SETUP.md) - Secrets configuration
- [CI-CD-OPERATIONS-GUIDE.md](CI-CD-OPERATIONS-GUIDE.md) - Operations procedures

---

**Last Updated:** October 31, 2025
