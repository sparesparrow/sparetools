# Setting Up Cloudsmith and GitHub Packages Repositories

## Current Status

✅ **22 packages built and ready for upload**
⚠️ **Repositories need to be created/configured**

## Cloudsmith Setup

### Step 1: Create Repository

1. Go to https://cloudsmith.io
2. Create a new repository:
   - **Owner**: `sparesparrow-conan`
   - **Repository Name**: `sparetools` (or your preferred name)
   - **Format**: Conan

### Step 2: Get Repository URL

After creating, the URL will be:
```
https://dl.cloudsmith.io/public/sparesparrow-conan/sparetools/conan/
```

### Step 3: Update Script

Update `upload_all_packages.sh` with correct URL:
```bash
CLOUDSMITH_URL="https://dl.cloudsmith.io/public/sparesparrow-conan/sparetools/conan/"
```

### Step 4: Get API Key

1. Go to Cloudsmith Settings → API Keys
2. Create new API key with write permissions
3. Set environment variable:
   ```bash
   export CLOUDSMITH_API_KEY=your_api_key
   ```

## GitHub Packages Setup

### Step 1: Repository Must Exist

GitHub Packages requires the repository to exist first:
- Repository: `sparesparrow/sparetools` (or your repo)

### Step 2: Get Token

1. GitHub → Settings → Developer settings → Personal access tokens
2. Create token with `write:packages` permission
3. Set environment variable:
   ```bash
   export GITHUB_TOKEN=your_github_token
   ```

### Step 3: Verify Repository

The repository must exist at:
```
https://github.com/sparesparrow/sparetools
```

## Quick Setup Script

```bash
#!/bin/bash
# setup_repositories.sh

echo "Setting up SpareTools package repositories..."

# Cloudsmith
read -p "Cloudsmith API Key: " CLOUDSMITH_API_KEY
read -p "Cloudsmith Repository URL: " CLOUDSMITH_URL

# GitHub
read -p "GitHub Token: " GITHUB_TOKEN
read -p "GitHub Owner: " GITHUB_OWNER
read -p "GitHub Repo: " GITHUB_REPO

# Update upload script
sed -i "s|CLOUDSMITH_URL=.*|CLOUDSMITH_URL=\"$CLOUDSMITH_URL\"|" upload_all_packages.sh

export CLOUDSMITH_API_KEY
export GITHUB_TOKEN
export GITHUB_REPOSITORY_OWNER=$GITHUB_OWNER
export GITHUB_REPOSITORY="$GITHUB_OWNER/$GITHUB_REPO"

echo "✅ Configuration updated"
echo "Run: ./upload_all_packages.sh"
```

## Packages Ready for Upload

All 22 packages are built and ready. Once repositories are configured:

```bash
./upload_all_packages.sh
```

## Alternative: Use Existing Repositories

If you already have repositories set up, just update the URLs in `upload_all_packages.sh`:
- Line ~45: `CLOUDSMITH_URL=`
- Line ~55: `GITHUB_URL=`