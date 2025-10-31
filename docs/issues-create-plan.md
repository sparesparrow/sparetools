# Issue Creation Plan

The following `gh` commands can be used to materialise the drafted issues once
repository credentials are available. Replace `--body-file` targets with the
corresponding sections from `docs/issues-draft.md` or inline bullet points.

```bash
# sparesparrow/openssl
gh issue create --repo sparesparrow/openssl \
  --title "Track provider ordering and MSVC coverage" \
  --label enhancement \
  --body "See sparetools repository: docs/issues-draft.md (OpenSSL section)."

# sparesparrow/openssl-tools
gh issue create --repo sparesparrow/openssl-tools \
  --title "Expose build_matrix CLI for CI reuse" \
  --label enhancement \
  --body "Reference tasks in docs/issues-draft.md"

# Repeat for each repository listed.
```

