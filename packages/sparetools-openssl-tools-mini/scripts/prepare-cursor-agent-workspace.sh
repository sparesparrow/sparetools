#!/bin/bash
set -euo pipefail

echo "Preparing cursor-agent workspace..."

# Create directory structure
mkdir -p prompts
mkdir -p .cursor/rules/{track-a,track-b,track-c}

# Track B prompt
cat > prompts/track-b-devex.md << 'PROMPT'
# Track B: Developer Experience & Onboarding Implementation

## Goal
Create zero-friction onboarding for sparesparrow OpenSSL developers.

## Context
- Current state: Conan extensions working (openssl:build, openssl:graph)
- Target: < 15 minute onboarding for new developers
- Platform support: Linux, macOS, Windows WSL

## Deliverables

### 1. Bootstrap Script (openssl-test/bootstrap/openssl-conan-init.py)
Standalone Python 3.8+ script with:
- Auto-detect and install Conan 2.x if missing
- Configure remotes (sparesparrow-conan, conancenter)
- Clone/update all repos (use ~/sparesparrow/ directory)
- Install openssl-tools extensions via install-extensions.sh
- Modes: --minimal (Conan only), --full (repos), --dev (IDE)
- Colored progress indicators (use ANSI codes)
- Error handling with actionable fixes

### 2. VS Code Integration (openssl-test/.vscode/)
- extensions.json: Recommended extensions (C/C++, CMake, Python, Conan)
- settings.json: Workspace settings (paths, IntelliSense)
- launch.json: Debug configs (OpenSSL CLI, FIPS self-test, Python recipes)
- tasks.json: Build/test/clean tasks

### 3. IntelliSense Helper (openssl-test/scripts/update-intellisense.py)
- Extract include paths from Conan dependencies
- Update c_cpp_properties.json automatically
- Support for cross-compilation toolchains

### 4. Documentation (openssl-test/docs/)
- getting-started.md: Quick start, common tasks, troubleshooting
- architecture.md: Repo relationships, diagrams

## Implementation Constraints
- Bootstrap MUST be standalone (no pip install until Conan is ready)
- Use pathlib not os.path
- Cross-platform (Linux/macOS/Windows WSL)
- Idempotent (safe to run multiple times)

## Testing Requirements
- Test on fresh Ubuntu 22.04 VM
- Verify < 15 minute onboarding time
- VS Code IntelliSense works immediately after bootstrap
- Debugging with breakpoints functional

## Success Criteria
- [ ] Bootstrap script completes in < 15 minutes on fresh system
- [ ] VS Code opens project with working IntelliSense
- [ ] Debugging OpenSSL CLI works with breakpoints
- [ ] Documentation covers 90% of common questions
PROMPT

# Track B rules
cat > .cursor/rules/track-b/devex.mdrule << 'RULES'
---
tags: [devex, bootstrap, vscode, onboarding]
globs:
  - "**/bootstrap/**"
  - "**/.vscode/**"
  - "**/scripts/update-intellisense.py"
---

# Track B: Developer Experience Rules

## Context
Repository: sparesparrow/openssl-test
Focus: Zero-friction onboarding, IDE integration

## Code Style
- Python: PEP 8, type hints, docstrings
- Use pathlib not os.path
- ANSI colors with fallback for non-TTY
- JSON: indent=2 for readability

## Bootstrap Script Requirements
- Standalone (no external deps initially)
- Progress indicators (spinner or percentage)
- Clear error messages with fixes
- Retry logic for network operations
- Cleanup on interrupt (Ctrl+C)

## VS Code Configuration
- Extensions MUST be workspace recommendations
- Settings should not override user global settings
- Launch configs for OpenSSL debugging (GDB on Linux, LLDB on macOS)
- Tasks should use Conan commands where possible

## File Structure
```
openssl-test/
├── bootstrap/
│   ├── openssl-conan-init.py
│   ├── requirements.txt
│   └── README.md
├── .vscode/
│   ├── extensions.json
│   ├── settings.json
│   ├── launch.json
│   └── tasks.json
├── scripts/
│   ├── update-intellisense.py
│   ├── test-environment.sh
│   └── test-environment.sh
└── docs/
    ├── getting-started.md
    └── architecture.md
```

## Testing Checklist
- [ ] Bootstrap on fresh Ubuntu 22.04
- [ ] Bootstrap on macOS 13+
- [ ] Bootstrap on Windows 11 WSL2
- [ ] VS Code IntelliSense finds OpenSSL headers
- [ ] Debugging OpenSSL CLI with breakpoints
- [ ] All scripts pass shellcheck/pylint
RULES

echo "✓ Workspace prepared for cursor-agent"
echo ""
echo "Next: Run implementation script"
echo "  ./scripts/implement-parallel-tracks.sh --track=B"
