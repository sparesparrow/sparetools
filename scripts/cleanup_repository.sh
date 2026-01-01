#!/bin/bash
# Cleanup repository from redundant, outdated, or unwanted files
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

DRY_RUN="${1:-}"

if [ "$DRY_RUN" == "--dry-run" ]; then
    echo "🔍 DRY RUN MODE - No files will be deleted"
    echo ""
fi

DELETED=0

delete_file() {
    local file="$1"
    local reason="$2"
    
    if [ ! -e "$file" ]; then
        return
    fi
    
    if [ "$DRY_RUN" == "--dry-run" ]; then
        echo "Would delete: $file ($reason)"
        ((DELETED++)) || true
    else
        if [ -f "$file" ]; then
            rm -f "$file" && echo "Deleted: $file ($reason)" && ((DELETED++)) || true
        elif [ -d "$file" ]; then
            rm -rf "$file" && echo "Deleted directory: $file ($reason)" && ((DELETED++)) || true
        fi
    fi
}

echo "🧹 Starting repository cleanup..."
echo ""

# Log files
echo "📋 Cleaning log files..."
for log in *.log; do
    [ -f "$log" ] && delete_file "$log" "log file"
done

# Python cache
echo "🐍 Cleaning Python cache..."
find . -type d -name "__pycache__" -not -path "./.git/*" | while read -r dir; do
    delete_file "$dir" "Python cache"
done
find . -type f \( -name "*.pyc" -o -name "*.pyo" \) -not -path "./.git/*" | while read -r file; do
    delete_file "$file" "Python bytecode"
done

# Build directories
echo "🔨 Cleaning build directories..."
find . -type d -name "build" -not -path "./.git/*" -not -path "./scripts/build/*" | while read -r dir; do
    [ -f "$dir/conanbuildinfo.txt" ] || [ -f "$dir/conaninfo.txt" ] && delete_file "$dir" "Conan build directory"
done

# Dist directories
echo "📦 Cleaning dist directories..."
find . -type d -name "dist" -not -path "./.git/*" | while read -r dir; do
    delete_file "$dir" "dist directory"
done

# Temporary files
echo "🗑️  Cleaning temporary files..."
find . -type f \( -name "*.tmp" -o -name "*.bak" -o -name "*.swp" -o -name "*.swo" -o -name "*~" \) -not -path "./.git/*" | while read -r file; do
    delete_file "$file" "temporary file"
done

# IDE files
echo "💻 Cleaning IDE files..."
find . -type f -name ".directory" -not -path "./.git/*" | while read -r file; do
    delete_file "$file" "IDE file"
done

# Report files
echo "📊 Cleaning report files..."
for report in *_REPORT.json *_VALIDATION_REPORT.json BUILD_UPLOAD_REPORT.json SYNC_REPORT.json SYNC_VALIDATION_REPORT.json build_report.json; do
    [ -f "$report" ] && delete_file "$report" "build report"
done

# Conan artifacts
echo "🔧 Cleaning Conan artifacts..."
find . -type f \( -name "conanbuildinfo.txt" -o -name "conaninfo.txt" -o -name "graph_info.json" -o -name "conanbuild.sh" -o -name "conanrun.sh" \) -not -path "./.git/*" | while read -r file; do
    delete_file "$file" "Conan artifact"
done

# Pytest cache
echo "🧪 Cleaning pytest cache..."
find . -type d -name ".pytest_cache" -not -path "./.git/*" | while read -r dir; do
    delete_file "$dir" "pytest cache"
done

# Node modules (should not be committed)
echo ""
echo "📦 Cleaning node_modules..."
find . -type d -name "node_modules" -not -path "./.git/*" | while read -r dir; do
    delete_file "$dir" "node_modules"
done

# Root-level scripts that are in .gitignore
echo ""
echo "🗑️  Cleaning ignored root-level scripts..."
for script in build_and_upload_all.sh build_packages_skip_cpython.sh upload_all_packages.sh upload_with_cloudsmith_cli.sh create_cloudsmith_repo.sh; do
    [ -f "$script" ] && delete_file "$script" "ignored script"
done

# Conan build scripts in root
echo ""
echo "🔧 Cleaning Conan build scripts..."
for script in conanbuild.sh conanrun.sh conanbuildenv-*.sh conanrunenv-*.sh deactivate_conan*.sh; do
    [ -f "$script" ] && delete_file "$script" "Conan build script"
done

# .directory files (KDE/Dolphin)
echo ""
echo "💻 Cleaning .directory files..."
find . -type f -name ".directory" -not -path "./.git/*" | while read -r file; do
    delete_file "$file" ".directory file"
done

echo ""
echo "✅ Cleanup complete!"
[ "$DRY_RUN" == "--dry-run" ] && echo "   Files that would be deleted: $DELETED" || echo "   Files deleted: $DELETED"
