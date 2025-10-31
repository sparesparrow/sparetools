# GitHub Secrets Configuration Guide

This guide documents the GitHub secrets required for CI/CD workflows in the sparetools repository.

## Required Secrets

### 1. CLOUDSMITH_API_KEY

**Purpose:** Authenticate with Cloudsmith for package publishing

**Workflows using this secret:**
- `publish.yml` - Package publishing workflow

**How to obtain:**
1. Log in to Cloudsmith: https://cloudsmith.io
2. Navigate to your account settings
3. Go to API Settings → API Keys
4. Create a new API key with "Write" permissions for the `openssl-conan` repository
5. Copy the generated key

**How to configure:**
```bash
# Via GitHub CLI
gh secret set CLOUDSMITH_API_KEY -R sparesparrow/sparetools

# Via GitHub Web UI
# Navigate to: Settings → Secrets and variables → Actions → New repository secret
# Name: CLOUDSMITH_API_KEY
# Value: <your-api-key>
```

**Testing:**
```bash
# Test authentication locally
export CLOUDSMITH_API_KEY="your-key-here"
conan remote login sparesparrow-conan sparesparrow --password "$CLOUDSMITH_API_KEY"
```

---

### 2. GITHUB_TOKEN (Automatic)

**Purpose:** Authenticate with GitHub Packages and GitHub API

**Workflows using this secret:**
- `publish.yml` - GitHub Packages publishing
- `nightly.yml` - Create issues on failure
- `security.yml` - Upload to GitHub Security tab

**Configuration:** ✅ **No action required** - Automatically provided by GitHub Actions

**Permissions required:**
- `packages: write` - For publishing to GitHub Packages
- `contents: write` - For creating GitHub Releases
- `security-events: write` - For security scanning results
- `issues: write` - For creating issues on nightly failures

**How permissions are set:**
```yaml
# In workflow files
permissions:
  packages: write
  contents: write
  security-events: write
  issues: write
```

---

## Optional Secrets

### 3. CONAN_REMOTE_PASSWORD (Future)

**Purpose:** Additional authentication for custom Conan remotes

**Status:** Not currently required, but documented for future use

**How to configure:**
```bash
gh secret set CONAN_REMOTE_PASSWORD -R sparesparrow/sparetools
```

---

## Verification Checklist

Use this checklist to verify all secrets are configured correctly:

### Pre-deployment Checklist

- [ ] CLOUDSMITH_API_KEY is set in GitHub repository secrets
- [ ] CLOUDSMITH_API_KEY has write permissions for openssl-conan repository
- [ ] GitHub Actions is enabled for the repository
- [ ] Workflow permissions are configured correctly

### Test Commands

```bash
# 1. Verify GitHub CLI authentication
gh auth status

# 2. List current secrets (shows names only, not values)
gh secret list -R sparesparrow/sparetools

# 3. Test Cloudsmith authentication locally
conan remote add sparesparrow-conan https://conan.cloudsmith.io/sparesparrow-conan/openssl-conan/
conan remote login sparesparrow-conan sparesparrow --password "$CLOUDSMITH_API_KEY"

# 4. Test package upload (dry run - query only)
conan search -r sparesparrow-conan
```

---

## Workflow-Specific Requirements

### ci.yml
- ✅ No secrets required
- Uses public Cloudsmith repository for downloads

### publish.yml
- ✅ CLOUDSMITH_API_KEY (required for Cloudsmith publishing)
- ✅ GITHUB_TOKEN (automatic, for GitHub Packages publishing)

### security.yml
- ✅ GITHUB_TOKEN (automatic, for uploading security scan results)

### nightly.yml
- ✅ GITHUB_TOKEN (automatic, for creating issues on failures)

---

## Troubleshooting

### Issue: "CLOUDSMITH_API_KEY secret missing"

**Solution:**
```bash
# Check if secret exists
gh secret list -R sparesparrow/sparetools | grep CLOUDSMITH_API_KEY

# Set the secret if missing
gh secret set CLOUDSMITH_API_KEY -R sparesparrow/sparetools
```

### Issue: "Authentication failed" during conan upload

**Possible causes:**
1. API key expired or revoked
2. Incorrect repository permissions
3. API key not configured in GitHub secrets

**Solution:**
1. Generate a new Cloudsmith API key
2. Verify permissions: Settings → API Keys → Check "Write" permission
3. Update GitHub secret:
   ```bash
   gh secret set CLOUDSMITH_API_KEY -R sparesparrow/sparetools
   ```

### Issue: "Resource not accessible by integration" for GitHub Packages

**Possible causes:**
- Insufficient workflow permissions

**Solution:**
Add permissions to workflow file:
```yaml
permissions:
  packages: write
  contents: read
```

---

## Security Best Practices

1. **Rotate secrets regularly**
   - Cloudsmith API keys should be rotated every 90 days
   - Generate new keys when team members leave

2. **Use minimal permissions**
   - Grant only "Write" permission for package publishing
   - Avoid "Admin" permissions unless absolutely necessary

3. **Monitor secret usage**
   - Review GitHub Actions logs for authentication failures
   - Check Cloudsmith access logs periodically

4. **Protect secrets**
   - Never commit secrets to the repository
   - Never log secret values in workflow outputs
   - Use GitHub's secret masking (automatic)

---

## Automated Setup from Environment Variables

If you have your secrets stored as environment variables in `~/.bashrc`, you can use the automated sync script to configure GitHub secrets automatically.

### Using the Sync Script

The `scripts/sync-github-secrets.sh` script reads environment variables from your `~/.bashrc` and configures them as GitHub secrets:

```bash
# Run the sync script
./scripts/sync-github-secrets.sh
```

**What it does:**
1. ✅ Verifies GitHub CLI authentication
2. ✅ Sources `~/.bashrc` to load environment variables
3. ✅ Maps environment variables to GitHub secrets:
   - `CLOUDSMITH_API_KEY` → `CLOUDSMITH_API_KEY` (required)
   - `GITHUB_TOKEN` → `GITHUB_TOKEN` (optional)
   - `CONAN_REMOTE_PASSWORD` → `CONAN_REMOTE_PASSWORD` (optional)
4. ✅ Sets each secret via GitHub CLI
5. ✅ Verifies configuration by listing all secrets

**Prerequisites:**
- GitHub CLI (`gh`) installed and authenticated
- Environment variables exported in `~/.bashrc`:
  ```bash
  export CLOUDSMITH_API_KEY="your-key-here"
  ```

**Example Output:**
```
🔐 GitHub Secrets Sync from ~/.bashrc
======================================

✅ GitHub CLI authenticated

📖 Sourcing environment variables from /home/user/.bashrc...
✅ Environment variables loaded

📝 Configuring required secrets...

Setting CLOUDSMITH_API_KEY...
✅ CLOUDSMITH_API_KEY configured successfully

📝 Configuring optional secrets (if available)...

🔍 Verifying configured secrets...

CLOUDSMITH_API_KEY  Updated 2 minutes ago

✅ Setup complete!
```

**Troubleshooting:**

If the script can't find environment variables:
```bash
# Verify your bashrc has the export statements
grep "export CLOUDSMITH_API_KEY" ~/.bashrc

# Source bashrc manually first
source ~/.bashrc
./scripts/sync-github-secrets.sh
```

---

## Quick Setup Script

```bash
#!/bin/bash
# setup-github-secrets.sh

echo "🔐 GitHub Secrets Setup for SpareTools"
echo "======================================"
echo ""

# Check GitHub CLI authentication
if ! gh auth status > /dev/null 2>&1; then
    echo "❌ GitHub CLI not authenticated"
    echo "Run: gh auth login"
    exit 1
fi

echo "✅ GitHub CLI authenticated"
echo ""

# Prompt for Cloudsmith API key
echo "Enter your Cloudsmith API key:"
echo "(Get it from https://cloudsmith.io → Settings → API Keys)"
read -s CLOUDSMITH_KEY

if [ -z "$CLOUDSMITH_KEY" ]; then
    echo "❌ No API key provided"
    exit 1
fi

# Set the secret
echo ""
echo "Setting CLOUDSMITH_API_KEY secret..."
echo "$CLOUDSMITH_KEY" | gh secret set CLOUDSMITH_API_KEY -R sparesparrow/sparetools

if [ $? -eq 0 ]; then
    echo "✅ CLOUDSMITH_API_KEY configured successfully"
else
    echo "❌ Failed to configure secret"
    exit 1
fi

# Verify
echo ""
echo "Verifying secrets..."
gh secret list -R sparesparrow/sparetools

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Verify the secret in GitHub UI: Settings → Secrets and variables → Actions"
echo "2. Test the workflow: gh workflow run publish.yml"
```

Save this script and run:
```bash
chmod +x setup-github-secrets.sh
./setup-github-secrets.sh
```

---

## References

- [GitHub Actions Secrets Documentation](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- [Cloudsmith API Keys](https://help.cloudsmith.io/docs/api-keys)
- [Conan Remote Authentication](https://docs.conan.io/2/reference/commands/remote.html#conan-remote-login)

