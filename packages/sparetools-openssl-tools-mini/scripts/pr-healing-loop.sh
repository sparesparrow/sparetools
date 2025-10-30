#!/usr/bin/env bash
# pr-healing-loop.sh - Automated PR remediation using Cursor agents and GitHub CLI

set -euo pipefail

# Configuration
REPO="sparesparrow/openssl-test"
MAX_ITERATIONS=10
SLEEP_BETWEEN_ITERATIONS=300  # 5 minutes
AGENT_TIMEOUT=600  # 10 minutes for agent operations

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $*"
}

error() {
    echo -e "${RED}[ERROR]${NC} $*" >&2
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $*"
}

warn() {
    echo -e "${YELLOW}[WARNING]${NC} $*"
}

# Check prerequisites
check_prerequisites() {
    log "Checking prerequisites..."

    command -v gh >/dev/null 2>&1 || { error "gh CLI not found"; exit 1; }
    command -v git >/dev/null 2>&1 || { error "git not found"; exit 1; }
    command -v jq >/dev/null 2>&1 || { error "jq not found"; exit 1; }

    # Verify GitHub authentication
    if ! gh auth status >/dev/null 2>&1; then
        error "Not authenticated with GitHub. Run: gh auth login"
        exit 1
    fi

    success "Prerequisites validated"
}

# Get all open PRs
get_open_prs() {
    log "Fetching open pull requests from $REPO..."
    gh pr list --repo "$REPO" --json number,title,headRefName --jq '.[] | .number' || {
        error "Failed to fetch PRs"
        return 1
    }
}

# Check workflow status for a PR
check_workflow_status() {
    local pr_number=$1
    log "Checking workflow status for PR #$pr_number..."

    # Get latest commit SHA for the PR
    local commit_sha
    commit_sha=$(gh pr view "$pr_number" --repo "$REPO" --json headRefOid --jq '.headRefOid')

    # Get workflow runs for this commit
    local workflow_status
    workflow_status=$(gh api "/repos/$REPO/commits/$commit_sha/check-runs" \
        --jq '.check_runs | map(select(.app.slug == "github-actions")) |
        if length == 0 then "none"
        elif any(.conclusion == "failure") then "failure"
        elif any(.conclusion == null) then "pending"
        elif all(.conclusion == "success") then "success"
        else "unknown" end')

    echo "$workflow_status"
}

# Analyze PR for issues
analyze_pr_issues() {
    local pr_number=$1
    log "Analyzing PR #$pr_number for issues..."

    # Get PR details
    local pr_data
    pr_data=$(gh pr view "$pr_number" --repo "$REPO" --json files,changedFiles,additions,deletions,body)

    local changed_files
    changed_files=$(echo "$pr_data" | jq -r '.changedFiles')

    local issues=()

    # Check for excessive file changes
    if [ "$changed_files" -gt 30 ]; then
        issues+=("excessive_files:$changed_files files changed, consider splitting PR")
    fi

    # Check for generated files (build artifacts)
    local has_build_artifacts
    has_build_artifacts=$(echo "$pr_data" | jq -r '.files[] | select(.path | test("build\\.ninja|\\*\\.ninja\\.tmpl|test-.*\\.sh")) | .path' | wc -l)

    if [ "$has_build_artifacts" -gt 0 ]; then
        issues+=("build_artifacts:Generated files detected in PR")
    fi

    # Check for missing PR description
    local body_length
    body_length=$(echo "$pr_data" | jq -r '.body | length')

    if [ "$body_length" -lt 100 ]; then
        issues+=("insufficient_description:PR description too short")
    fi

    # Return issues as JSON array
    printf '%s\n' "${issues[@]}" | jq -R . | jq -s .
}

# Generate remediation strategy
generate_remediation_strategy() {
    local pr_number=$1
    local issues=$2

    log "Generating remediation strategy for PR #$pr_number..."

    local strategy=""

    # Parse issues and create strategy
    echo "$issues" | jq -r '.[]' | while IFS=: read -r issue_type issue_desc; do
        case "$issue_type" in
            excessive_files)
                strategy+="STEP: Split PR into focused changes. Use git log to identify logical groupings. Create separate branches for: (1) Conan integration, (2) Security workflows, (3) Upstream sync. Cherry-pick relevant commits to each branch.
"
                ;;
            build_artifacts)
                strategy+="STEP: Remove build artifacts. Execute: git rm build.ninja.in build.ninja.new test-*.sh Configurations/*.ninja.tmpl. Update .gitignore with patterns: build.ninja*, *.ninja.tmpl, test-*.sh. Commit changes.
"
                ;;
            insufficient_description)
                strategy+="STEP: Enhance PR description. Add sections: Overview, Changes Made, Testing Evidence, Prerequisites, Migration Path. Include platform-specific test results and compatibility notes.
"
                ;;
        esac
    done

    echo "$strategy"
}

# Execute remediation using Cursor agent
execute_cursor_agent() {
    local pr_number=$1
    local prompt=$2

    log "Executing Cursor agent for PR #$pr_number..."

    # Get PR branch name
    local branch_name
    branch_name=$(gh pr view "$pr_number" --repo "$REPO" --json headRefName --jq '.headRefName')

    # Ensure we're on the correct branch
    git fetch origin "$branch_name"
    git checkout "$branch_name"

    # Export prompt for agent
    export CURSOR_AGENT_PROMPT="$prompt"

    # Create instruction file for manual execution
    local instruction_file="/tmp/cursor-agent-pr-${pr_number}.md"
    cat > "$instruction_file" << EOF
# Cursor Agent Instructions for PR #$pr_number

$CURSOR_AGENT_PROMPT

## Execution Steps:
1. Review current branch: $branch_name
2. Apply changes as described above
3. Commit with descriptive message
4. Push to origin

## Validation:
- Run local tests if applicable
- Verify no build artifacts committed
- Ensure commit message follows conventions

## OpenSSL CI/CD Specialist Context:
- Follow the specialized Cursor rule for OpenSSL development
- Prioritize security and compliance
- Maintain backward compatibility
- Update versions before conanfile changes
- Use proper build order: Foundation → Tooling → Domain
EOF

    warn "Cursor agent CLI not available. Instructions saved to: $instruction_file"
    warn "Please execute manually and press Enter to continue..."
    read -r
}

# Re-run failed workflows
rerun_failed_workflows() {
    local pr_number=$1
    log "Re-running failed workflows for PR #$pr_number..."

    local commit_sha
    commit_sha=$(gh pr view "$pr_number" --repo "$REPO" --json headRefOid --jq '.headRefOid')

    # Get failed workflow runs
    local failed_runs
    failed_runs=$(gh api "/repos/$REPO/commits/$commit_sha/check-runs" \
        --jq '.check_runs | map(select(.conclusion == "failure" and .app.slug == "github-actions")) | .[].id')

    if [ -z "$failed_runs" ]; then
        log "No failed workflows to re-run"
        return 0
    fi

    # Trigger re-runs
    echo "$failed_runs" | while read -r run_id; do
        log "Re-running workflow run ID: $run_id"
        gh api -X POST "/repos/$REPO/check-runs/$run_id/rerequest" || {
            warn "Failed to re-run workflow $run_id"
        }
    done
}

# Enable disabled workflows
enable_workflows() {
    log "Checking for disabled workflows..."

    local disabled_workflows
    disabled_workflows=$(gh api "/repos/$REPO/actions/workflows" \
        --jq '.workflows | map(select(.state == "disabled_manually")) | .[].id')

    if [ -z "$disabled_workflows" ]; then
        log "No disabled workflows found"
        return 0
    fi

    echo "$disabled_workflows" | while read -r workflow_id; do
        log "Enabling workflow ID: $workflow_id"
        gh api -X PUT "/repos/$REPO/actions/workflows/$workflow_id/enable" || {
            warn "Failed to enable workflow $workflow_id"
        }
    done
}

# Post GitHub CLI comments
post_github_comments() {
    local pr_number=$1
    local issues=$2

    log "Posting GitHub CLI comments for PR #$pr_number..."

    # Post structured feedback
    local comment_body="@cursor This PR has been analyzed for common issues. "

    if echo "$issues" | jq -e '.[] | select(startswith("excessive_files"))' >/dev/null; then
        comment_body+="The PR contains many changed files that should be split into focused PRs. "
    fi

    if echo "$issues" | jq -e '.[] | select(startswith("build_artifacts"))' >/dev/null; then
        comment_body+="Generated build artifacts detected - these should be removed and added to .gitignore. "
    fi

    if echo "$issues" | jq -e '.[] | select(startswith("insufficient_description"))' >/dev/null; then
        comment_body+="PR description needs enhancement with testing evidence and migration path. "
    fi

    comment_body+="See detailed instructions in the automated healing process."

    gh pr review "$pr_number" --repo "$REPO" --comment --body "$comment_body"
}

# Main healing loop
main_healing_loop() {
    local iteration=0
    local all_passing=false

    while [ $iteration -lt $MAX_ITERATIONS ] && [ "$all_passing" = false ]; do
        iteration=$((iteration + 1))
        log "=== Iteration $iteration/$MAX_ITERATIONS ==="

        # Enable any disabled workflows first
        enable_workflows

        # Get all open PRs
        local prs
        prs=$(get_open_prs)

        if [ -z "$prs" ]; then
            warn "No open PRs found"
            break
        fi

        local all_prs_passing=true

        # Process each PR
        while IFS= read -r pr_number; do
            log "Processing PR #$pr_number"

            # Check current status
            local status
            status=$(check_workflow_status "$pr_number")

            case "$status" in
                success)
                    success "PR #$pr_number workflows passing"
                    ;;
                none)
                    warn "PR #$pr_number has no workflows"
                    ;;
                pending)
                    log "PR #$pr_number workflows still running"
                    all_prs_passing=false
                    ;;
                failure)
                    warn "PR #$pr_number workflows failed"
                    all_prs_passing=false

                    # Analyze issues
                    local issues
                    issues=$(analyze_pr_issues "$pr_number")

                    if [ "$(echo "$issues" | jq 'length')" -gt 0 ]; then
                        log "Found $(echo "$issues" | jq 'length') issues in PR #$pr_number"

                        # Post GitHub comments
                        post_github_comments "$pr_number" "$issues"

                        # Generate remediation strategy
                        local strategy
                        strategy=$(generate_remediation_strategy "$pr_number" "$issues")

                        # Execute remediation
                        if execute_cursor_agent "$pr_number" "$strategy"; then
                            success "Applied remediation to PR #$pr_number"
                        else
                            warn "Failed to apply remediation to PR #$pr_number"
                        fi
                    fi

                    # Re-run failed workflows
                    rerun_failed_workflows "$pr_number"
                    ;;
                *)
                    warn "PR #$pr_number has unknown status: $status"
                    all_prs_passing=false
                    ;;
            esac
        done <<< "$prs"

        if [ "$all_passing" = true ]; then
            all_passing=true
            success "All PRs have passing workflows!"
        else
            log "Some PRs still need attention, sleeping for $SLEEP_BETWEEN_ITERATIONS seconds..."
            sleep $SLEEP_BETWEEN_ITERATIONS
        fi
    done

    if [ "$all_passing" = true ]; then
        success "=== Healing complete! All workflows passing ==="
        return 0
    else
        error "=== Maximum iterations reached without full success ==="
        return 1
    fi
}

# Main execution
main() {
    log "Starting PR healing loop for $REPO"

    check_prerequisites
    main_healing_loop

    local exit_code=$?

    if [ $exit_code -eq 0 ]; then
        success "PR healing process completed successfully"
    else
        error "PR healing process completed with issues"
    fi

    exit $exit_code
}

# Run main function
main "$@"
