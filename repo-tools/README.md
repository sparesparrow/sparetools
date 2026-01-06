# Repository Management Tools

This directory contains scripts for managing multiple Git repositories and automated cloning operations.

## Directory Structure

```
repo-tools/
├── scripts/          # Repository management scripts
│   ├── clone_all_2025_repos.sh
│   └── sync_repos.sh
└── README.md
```

## Components

### Repository Cloning
- **Bulk Clone**: Clone multiple repositories automatically
- **Sync Repos**: Synchronize repository states across systems

## Usage

### Clone All Repositories
```bash
./scripts/clone_all_2025_repos.sh
```

### Sync Repositories
```bash
./scripts/sync_repos.sh --source /path/to/source --target /path/to/target
```

## Features

- Batch repository operations
- Progress tracking
- Error handling and retry logic
- Configuration-based repository lists
- Git authentication handling

## Requirements

- Git
- SSH keys configured for repositories
- Sufficient disk space
- Network connectivity

## Configuration

Repository lists can be configured in the script or external config files for different projects and organizations.