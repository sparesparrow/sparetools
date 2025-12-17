#!/usr/bin/env python3
"""
Documentation Linker and Auto-Generator for SpareTools

Automatically generates documentation links, API references, and maintains
the documentation index across the entire monorepo.
"""

import os
import re
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
from datetime import datetime
import ast
import inspect


class DocumentationLinker:
    """Auto-generates documentation links and maintains documentation structure."""

    def __init__(self, docs_dir: str = "docs"):
        """Initialize documentation linker.

        Args:
            docs_dir: Documentation directory path
        """
        self.docs_dir = Path(docs_dir)
        self.repo_root = Path(__file__).parent.parent.parent

    def regenerate_master_index(self) -> str:
        """Regenerate the master documentation index.

        Returns:
            Path to updated index file
        """
        print("📚 Regenerating master documentation index...")

        index_data = {
            "title": "SpareTools Documentation Index",
            "generated_at": datetime.now().isoformat(),
            "sections": {}
        }

        # Scan all documentation files
        for doc_file in self.docs_dir.rglob("*.md"):
            if doc_file.name == "INDEX.md":
                continue

            relative_path = doc_file.relative_to(self.docs_dir)
            section = self._classify_documentation_file(doc_file)

            if section not in index_data["sections"]:
                index_data["sections"][section] = []

            # Extract title and description
            title, description = self._extract_doc_metadata(doc_file)

            index_data["sections"][section].append({
                "file": str(relative_path),
                "title": title,
                "description": description,
                "last_modified": datetime.fromtimestamp(doc_file.stat().st_mtime).isoformat()
            })

        # Generate INDEX.md
        index_content = self._generate_index_markdown(index_data)
        index_file = self.docs_dir / "INDEX.md"

        with open(index_file, 'w', encoding='utf-8') as f:
            f.write(index_content)

        print(f"✅ Master index updated: {index_file}")
        return str(index_file)

    def generate_api_docs(self, output_dir: str = "api") -> str:
        """Generate API documentation from Python source code.

        Args:
            output_dir: Output directory for API docs

        Returns:
            Path to API docs directory
        """
        print("🔍 Generating API documentation...")

        api_dir = self.docs_dir / output_dir
        api_dir.mkdir(exist_ok=True)

        # Find all Python packages
        packages = {}
        for py_file in self.repo_root.rglob("*.py"):
            if self._is_package_file(py_file):
                package_info = self._extract_package_info(py_file)
                if package_info:
                    package_name = package_info["package"]
                    if package_name not in packages:
                        packages[package_name] = []

                    packages[package_name].append(package_info)

        # Generate API docs for each package
        for package_name, modules in packages.items():
            api_content = self._generate_package_api_doc(package_name, modules)
            api_file = api_dir / f"{package_name.replace('.', '-')}-api.md"

            with open(api_file, 'w', encoding='utf-8') as f:
                f.write(api_content)

        print(f"✅ API documentation generated in {api_dir}")
        return str(api_dir)

    def validate_documentation_links(self) -> Dict[str, Any]:
        """Validate all documentation links and cross-references.

        Returns:
            Validation results
        """
        print("🔗 Validating documentation links...")

        results = {
            "total_files": 0,
            "broken_links": [],
            "missing_files": [],
            "orphaned_files": []
        }

        # Scan all markdown files for links
        for md_file in self.docs_dir.rglob("*.md"):
            results["total_files"] += 1

            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Find all markdown links
            link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
            for match in re.finditer(link_pattern, content):
                link_text, link_target = match.groups()
                self._validate_link(md_file, link_target, results)

        return results

    def create_consumer_integration_guide(self, consumer_name: str) -> str:
        """Create a consumer-specific integration guide.

        Args:
            consumer_name: Name of the consumer

        Returns:
            Path to generated guide
        """
        print(f"📖 Creating integration guide for {consumer_name}...")

        # Load consumer configuration
        config = self._load_consumer_config(consumer_name)
        if not config:
            raise ValueError(f"Consumer configuration not found: {consumer_name}")

        # Generate integration guide
        guide_content = self._generate_integration_guide(consumer_name, config)
        guide_file = self.docs_dir / "integration" / f"{consumer_name.upper()}-INTEGRATION.md"

        guide_file.parent.mkdir(exist_ok=True)
        with open(guide_file, 'w', encoding='utf-8') as f:
            f.write(guide_content)

        print(f"✅ Integration guide created: {guide_file}")
        return str(guide_file)

    def update_cross_references(self) -> None:
        """Update cross-references between documentation files."""
        print("🔄 Updating cross-references...")

        # This would scan all docs and add "See also:" sections
        # For now, it's a placeholder
        print("✅ Cross-references updated (placeholder)")

    def _classify_documentation_file(self, doc_file: Path) -> str:
        """Classify a documentation file into a category."""
        path_parts = doc_file.relative_to(self.docs_dir).parts

        if "foundation" in path_parts:
            return "Foundation"
        elif "consumers" in path_parts:
            return f"Consumer: {path_parts[path_parts.index('consumers') + 1].title()}"
        elif "operations" in path_parts:
            return "Operations"
        elif "integration" in path_parts:
            return "Integration"
        elif "security" in path_parts:
            return "Security"
        elif "development" in path_parts:
            return "Development"
        elif "api" in path_parts:
            return "API"
        elif "examples" in path_parts:
            return "Examples"
        elif "glossary" in path_parts:
            return "Reference"
        else:
            return "General"

    def _extract_doc_metadata(self, doc_file: Path) -> tuple:
        """Extract title and description from a documentation file."""
        try:
            with open(doc_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()[:10]  # First 10 lines

            title = "Untitled"
            description = ""

            for line in lines:
                line = line.strip()
                if line.startswith("# "):
                    title = line[2:]
                    break

            # Look for description in subsequent lines
            for line in lines[1:]:
                line = line.strip()
                if line and not line.startswith("#"):
                    description = line
                    break

            return title, description

        except Exception:
            return doc_file.name, "Documentation file"

    def _generate_index_markdown(self, index_data: Dict[str, Any]) -> str:
        """Generate INDEX.md markdown content."""
        content = f"""# SpareTools Documentation Index

**Auto-generated master index of all SpareTools documentation.**

Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## 📚 Documentation Structure

This index provides a comprehensive overview of all SpareTools documentation, organized by category and consumer domain.

"""

        # Add sections
        for section_name, docs in index_data["sections"].items():
            if docs:
                content += f"### {section_name}\n\n"
                content += "| Document | Description | Status |\n"
                content += "|----------|-------------|--------|\n"

                for doc in sorted(docs, key=lambda x: x["title"]):
                    status = "✅ Complete" if len(doc.get("description", "")) > 10 else "📝 Draft"
                    content += f"| [{doc['title']}]({doc['file']}) | {doc.get('description', 'No description')} | {status} |\n"

                content += "\n"

        # Add statistics
        total_docs = sum(len(docs) for docs in index_data["sections"].values())
        complete_docs = sum(1 for docs in index_data["sections"].values()
                          for doc in docs if len(doc.get("description", "")) > 10)

        content += f"""---

## 📊 Documentation Statistics

- **Total Documents**: {total_docs}
- **Complete**: {complete_docs}
- **In Progress**: {total_docs - complete_docs}
- **Completion Rate**: {(complete_docs/total_docs*100):.1f}%

---

*Auto-generated by `scripts/utilities/doc-linker.py`*
"""

        return content

    def _is_package_file(self, py_file: Path) -> bool:
        """Check if a Python file is part of a package."""
        # Skip test files, __pycache__, etc.
        if any(skip in str(py_file) for skip in ["__pycache__", "test", ".git"]):
            return False

        # Check if it's in a packages directory
        return "packages" in str(py_file)

    def _extract_package_info(self, py_file: Path) -> Optional[Dict[str, Any]]:
        """Extract package information from a Python file."""
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Parse AST to find class definitions
            tree = ast.parse(content)

            package_info = {
                "file": str(py_file.relative_to(self.repo_root)),
                "classes": [],
                "functions": [],
                "docstring": ""
            }

            # Extract module docstring
            if ast.get_docstring(tree):
                package_info["docstring"] = ast.get_docstring(tree).split('\n')[0]

            # Extract classes and functions
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    package_info["classes"].append({
                        "name": node.name,
                        "docstring": ast.get_docstring(node) or ""
                    })
                elif isinstance(node, ast.FunctionDef) and not node.name.startswith('_'):
                    package_info["functions"].append({
                        "name": node.name,
                        "docstring": ast.get_docstring(node) or ""
                    })

            # Determine package name from path
            rel_path = py_file.relative_to(self.repo_root)
            path_parts = rel_path.parts

            if "packages" in path_parts:
                packages_idx = path_parts.index("packages")
                if len(path_parts) > packages_idx + 3:  # packages/type/consumer/package/file.py
                    package_info["package"] = ".".join(path_parts[packages_idx + 3:-1])
                elif len(path_parts) > packages_idx + 2:  # packages/type/package/file.py
                    package_info["package"] = ".".join(path_parts[packages_idx + 2:-1])

            return package_info if package_info["package"] else None

        except Exception as e:
            print(f"Error parsing {py_file}: {e}")
            return None

    def _generate_package_api_doc(self, package_name: str, modules: List[Dict[str, Any]]) -> str:
        """Generate API documentation for a package."""
        content = f"# {package_name} API Reference\n\n"
        content += f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

        for module in modules:
            content += f"## {module['file']}\n\n"

            if module['docstring']:
                content += f"{module['docstring']}\n\n"

            if module['classes']:
                content += "### Classes\n\n"
                for cls in module['classes']:
                    content += f"#### `{cls['name']}`\n\n"
                    if cls['docstring']:
                        content += f"{cls['docstring']}\n\n"

            if module['functions']:
                content += "### Functions\n\n"
                for func in module['functions']:
                    content += f"#### `{func['name']}`\n\n"
                    if func['docstring']:
                        content += f"{func['docstring']}\n\n"

            content += "---\n\n"

        return content

    def _validate_link(self, source_file: Path, link_target: str, results: Dict[str, Any]) -> None:
        """Validate a documentation link."""
        # Skip external links
        if link_target.startswith(('http://', 'https://', 'mailto:')):
            return

        # Resolve relative links
        if not link_target.startswith('/'):
            target_path = (source_file.parent / link_target).resolve()
        else:
            target_path = (self.docs_dir / link_target[1:]).resolve()

        if not target_path.exists():
            results["broken_links"].append({
                "source": str(source_file.relative_to(self.docs_dir)),
                "target": link_target,
                "resolved_path": str(target_path)
            })

    def _load_consumer_config(self, consumer_name: str) -> Optional[Dict[str, Any]]:
        """Load consumer configuration."""
        config_file = self.repo_root / "packages" / "consumers" / consumer_name / ".consumer.yaml"
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    return yaml.safe_load(f)
            except Exception:
                pass
        return None

    def _generate_integration_guide(self, consumer_name: str, config: Dict[str, Any]) -> str:
        """Generate consumer integration guide."""
        display_name = config.get("display_name", consumer_name.upper())
        description = config.get("description", "")
        packages = config.get("packages", [])

        content = f"# {display_name} Integration Guide\n\n"
        content += f"{description}\n\n"
        content += f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

        content += "## Packages\n\n"
        for package in packages:
            content += f"- `{package}`\n"
        content += "\n"

        content += "## Dependencies\n\n"
        foundation_deps = config.get("dependencies", {}).get("foundation", [])
        for dep in foundation_deps:
            content += f"- {dep}\n"
        content += "\n"

        content += "## Integration Steps\n\n"
        content += "1. Install required dependencies\n"
        content += "2. Configure consumer settings\n"
        content += "3. Build and test packages\n"
        content += "4. Deploy to target environment\n\n"

        content += "## Configuration\n\n"
        content += "```yaml\n"
        content += yaml.dump(config, default_flow_style=False)
        content += "```\n\n"

        return content


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Documentation Linker and Auto-Generator"
    )

    parser.add_argument(
        "--regenerate-index",
        action="store_true",
        help="Regenerate the master documentation index"
    )

    parser.add_argument(
        "--generate-api",
        action="store_true",
        help="Generate API documentation"
    )

    parser.add_argument(
        "--validate-links",
        action="store_true",
        help="Validate documentation links"
    )

    parser.add_argument(
        "--create-integration-guide",
        help="Create integration guide for specified consumer"
    )

    parser.add_argument(
        "--update-cross-refs",
        action="store_true",
        help="Update cross-references between docs"
    )

    parser.add_argument(
        "--docs-dir",
        default="docs",
        help="Documentation directory"
    )

    args = parser.parse_args()

    linker = DocumentationLinker(args.docs_dir)

    if args.regenerate_index:
        index_file = linker.regenerate_master_index()
        print(f"Index regenerated: {index_file}")

    if args.generate_api:
        api_dir = linker.generate_api_docs()
        print(f"API docs generated: {api_dir}")

    if args.validate_links:
        results = linker.validate_documentation_links()
        print(f"Link validation: {results['total_files']} files checked")
        if results['broken_links']:
            print(f"Broken links: {len(results['broken_links'])}")
            for link in results['broken_links'][:5]:  # Show first 5
                print(f"  {link['source']} -> {link['target']}")

    if args.create_integration_guide:
        guide_file = linker.create_consumer_integration_guide(args.create_integration_guide)
        print(f"Integration guide created: {guide_file}")

    if args.update_cross_refs:
        linker.update_cross_references()
        print("Cross-references updated")


if __name__ == "__main__":
    main()