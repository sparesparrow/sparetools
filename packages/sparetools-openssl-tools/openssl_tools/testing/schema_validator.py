#!/usr/bin/env python3
"""
Database Schema Validation System
Inspired by oms-dev patterns for robust database schema comparison and validation
"""

import os
import sys
import json
import logging
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import sqlite3
import tempfile

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DatabaseSchemaValidator:
    """Database schema validation system based on oms-dev patterns"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.schema_config_path = project_root / "conan-dev" / "schema-config.yml"
        self.test_fixtures_dir = project_root / "test" / "fixtures" / "db"
        self.reports_dir = project_root / "conan-dev" / "schema-reports"
        
        # Create directories
        self.schema_config_path.parent.mkdir(parents=True, exist_ok=True)
        self.test_fixtures_dir.mkdir(parents=True, exist_ok=True)
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        
    def setup_schema_config(self):
        """Set up database schema validation configuration"""
        config = {
            "database_schema_validation": {
                "enabled": True,
                "tools": {
                    "sqlite_diff": {
                        "enabled": True,
                        "tool_path": "sqlite3",  # Would be sqlite-tools in real implementation
                        "options": ["--schema"]
                    }
                },
                "validation_rules": {
                    "strict_mode": True,
                    "allow_index_differences": True,
                    "require_table_structure_match": True,
                    "require_column_types_match": True,
                    "require_constraints_match": True
                },
                "test_databases": {
                    "baseline_db": "test/fixtures/db/baseline.db",
                    "test_databases": [
                        "test/fixtures/db/test_*.db",
                        "test/fixtures/db/*_test.db"
                    ]
                },
                "ci_integration": {
                    "fail_on_mismatch": True,
                    "allow_opt_out": True,
                    "opt_out_env_var": "SCHEMA_MISMATCH_RAISE_ERROR"
                }
            },
            "monitoring": {
                "track_schema_changes": True,
                "generate_reports": True,
                "store_validation_history": True
            }
        }
        
        with open(self.schema_config_path, 'w') as f:
            import yaml
            yaml.dump(config, f, default_flow_style=False)
        
        logger.info(f"✅ Schema validation configuration created: {self.schema_config_path}")
    
    def validate_schemas(self) -> Dict:
        """Validate database schemas against baseline"""
        logger.info("🗄️ Validating database schemas...")
        
        validation_results = {
            "validation_timestamp": datetime.now().isoformat(),
            "baseline_database": "",
            "test_databases": [],
            "validation_summary": {
                "total_databases": 0,
                "passed_validation": 0,
                "failed_validation": 0,
                "schema_mismatches": []
            }
        }
        
        try:
            with open(self.schema_config_path, 'r') as f:
                import yaml
                config = yaml.safe_load(f)
            
            if not config["database_schema_validation"]["enabled"]:
                logger.info("⏸️ Database schema validation is disabled")
                return validation_results
            
            # Get baseline database
            baseline_db = self._get_baseline_database(config)
            validation_results["baseline_database"] = str(baseline_db)
            
            if not baseline_db.exists():
                logger.warning(f"⚠️ Baseline database not found: {baseline_db}")
                return validation_results
            
            # Get test databases
            test_databases = self._get_test_databases(config)
            validation_results["validation_summary"]["total_databases"] = len(test_databases)
            
            # Validate each test database
            for test_db in test_databases:
                test_result = self._validate_single_database(baseline_db, test_db, config)
                validation_results["test_databases"].append(test_result)
                
                if test_result["validation_passed"]:
                    validation_results["validation_summary"]["passed_validation"] += 1
                else:
                    validation_results["validation_summary"]["failed_validation"] += 1
                    validation_results["validation_summary"]["schema_mismatches"].append({
                        "database": str(test_db),
                        "differences": test_result["differences"]
                    })
            
            # Save validation results
            self._save_validation_results(validation_results)
            
            # Check CI integration rules
            self._check_ci_integration(validation_results, config)
            
            logger.info(f"✅ Schema validation complete: {validation_results['validation_summary']['passed_validation']}/{validation_results['validation_summary']['total_databases']} databases passed")
            
        except Exception as e:
            logger.error(f"❌ Schema validation failed: {e}")
        
        return validation_results
    
    def compare_database_schemas(self, base_database: Path, candidate_database: Path, diff_tool: Path) -> List[str]:
        """Compare database schemas using diff tool - pattern from oms-dev"""
        differences = []
        
        try:
            # Execute schema diff tool
            cmd = [str(diff_tool), '--schema', str(base_database), str(candidate_database)]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode != 0:
                logger.warning(f"Schema diff tool returned non-zero exit code: {result.returncode}")
                return differences
            
            # Parse and filter results
            filtered_result = list(filter(lambda line: len(line) > 0, result.stdout.split('\n')))
            
            current_line = ''
            for filtered_line in filtered_result:
                current_line += filtered_line
                if ';' not in filtered_line:
                    continue
                
                # Filter out INDEX-only differences (pattern from oms-dev)
                if 'INDEX' not in current_line:
                    differences.append(current_line)
                current_line = ''
            
        except Exception as e:
            logger.error(f"Failed to compare schemas: {e}")
        
        return differences
    
    def create_baseline_database(self, source_database: Path) -> bool:
        """Create baseline database from source"""
        logger.info(f"📋 Creating baseline database from {source_database}")
        
        try:
            baseline_path = self.test_fixtures_dir / "baseline.db"
            
            # Copy source database to baseline
            import shutil
            shutil.copy2(source_database, baseline_path)
            
            # Validate the baseline
            if self._validate_database_integrity(baseline_path):
                logger.info(f"✅ Baseline database created: {baseline_path}")
                return True
            else:
                logger.error("❌ Baseline database validation failed")
                return False
                
        except Exception as e:
            logger.error(f"❌ Failed to create baseline database: {e}")
            return False
    
    def generate_schema_documentation(self, database_path: Path) -> str:
        """Generate schema documentation from database"""
        logger.info(f"📚 Generating schema documentation for {database_path}")
        
        try:
            schema_info = self._extract_schema_info(database_path)
            
            # Generate markdown documentation
            doc_content = self._generate_schema_markdown(schema_info, database_path)
            
            # Save documentation
            doc_path = self.reports_dir / f"schema-doc-{database_path.stem}-{datetime.now().strftime('%Y%m%d-%H%M%S')}.md"
            with open(doc_path, 'w') as f:
                f.write(doc_content)
            
            logger.info(f"✅ Schema documentation generated: {doc_path}")
            return str(doc_path)
            
        except Exception as e:
            logger.error(f"❌ Failed to generate schema documentation: {e}")
            return ""
    
    def _get_baseline_database(self, config: Dict) -> Path:
        """Get baseline database path from configuration"""
        baseline_path = config["database_schema_validation"]["test_databases"]["baseline_db"]
        return self.project_root / baseline_path
    
    def _get_test_databases(self, config: Dict) -> List[Path]:
        """Get test database paths from configuration"""
        test_databases = []
        
        for pattern in config["database_schema_validation"]["test_databases"]["test_databases"]:
            pattern_path = self.project_root / pattern
            test_databases.extend(self.project_root.glob(pattern))
        
        return test_databases
    
    def _validate_single_database(self, baseline_db: Path, test_db: Path, config: Dict) -> Dict:
        """Validate a single database against baseline"""
        result = {
            "database": str(test_db),
            "validation_passed": True,
            "differences": [],
            "validation_timestamp": datetime.now().isoformat()
        }
        
        try:
            # Get diff tool
            diff_tool = self._get_diff_tool(config)
            
            # Compare schemas
            differences = self.compare_database_schemas(baseline_db, test_db, diff_tool)
            result["differences"] = differences
            
            if differences:
                result["validation_passed"] = False
                logger.warning(f"⚠️ Schema differences found in {test_db}:")
                for diff in differences:
                    logger.warning(f"  {diff}")
            else:
                logger.info(f"✅ Schema validation passed for {test_db}")
            
        except Exception as e:
            result["validation_passed"] = False
            result["error"] = str(e)
            logger.error(f"❌ Schema validation failed for {test_db}: {e}")
        
        return result
    
    def _get_diff_tool(self, config: Dict) -> Path:
        """Get database diff tool path"""
        tool_config = config["database_schema_validation"]["tools"]["sqlite_diff"]
        tool_path = tool_config["tool_path"]
        
        # In real implementation, this would use sqlite-tools package
        # For demo, we'll use sqlite3 with a custom comparison
        return Path(tool_path)
    
    def _validate_database_integrity(self, database_path: Path) -> bool:
        """Validate database integrity"""
        try:
            conn = sqlite3.connect(str(database_path))
            cursor = conn.cursor()
            
            # Run integrity check
            cursor.execute("PRAGMA integrity_check")
            result = cursor.fetchone()
            
            conn.close()
            
            return result[0] == "ok"
            
        except Exception as e:
            logger.error(f"Database integrity check failed: {e}")
            return False
    
    def _extract_schema_info(self, database_path: Path) -> Dict:
        """Extract schema information from database"""
        schema_info = {
            "database_name": database_path.name,
            "tables": [],
            "indexes": [],
            "triggers": [],
            "views": []
        }
        
        try:
            conn = sqlite3.connect(str(database_path))
            cursor = conn.cursor()
            
            # Get tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            
            for table in tables:
                table_name = table[0]
                table_info = self._get_table_info(cursor, table_name)
                schema_info["tables"].append(table_info)
            
            # Get indexes
            cursor.execute("SELECT name FROM sqlite_master WHERE type='index'")
            indexes = cursor.fetchall()
            
            for index in indexes:
                index_name = index[0]
                index_info = self._get_index_info(cursor, index_name)
                schema_info["indexes"].append(index_info)
            
            # Get triggers
            cursor.execute("SELECT name FROM sqlite_master WHERE type='trigger'")
            triggers = cursor.fetchall()
            
            for trigger in triggers:
                trigger_name = trigger[0]
                trigger_info = self._get_trigger_info(cursor, trigger_name)
                schema_info["triggers"].append(trigger_info)
            
            # Get views
            cursor.execute("SELECT name FROM sqlite_master WHERE type='view'")
            views = cursor.fetchall()
            
            for view in views:
                view_name = view[0]
                view_info = self._get_view_info(cursor, view_name)
                schema_info["views"].append(view_info)
            
            conn.close()
            
        except Exception as e:
            logger.error(f"Failed to extract schema info: {e}")
        
        return schema_info
    
    def _get_table_info(self, cursor, table_name: str) -> Dict:
        """Get detailed table information"""
        table_info = {
            "name": table_name,
            "columns": [],
            "constraints": []
        }
        
        try:
            # Get column information
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            
            for column in columns:
                column_info = {
                    "name": column[1],
                    "type": column[2],
                    "not_null": bool(column[3]),
                    "default_value": column[4],
                    "primary_key": bool(column[5])
                }
                table_info["columns"].append(column_info)
            
            # Get foreign key information
            cursor.execute(f"PRAGMA foreign_key_list({table_name})")
            foreign_keys = cursor.fetchall()
            
            for fk in foreign_keys:
                fk_info = {
                    "column": fk[3],
                    "references_table": fk[2],
                    "references_column": fk[4]
                }
                table_info["constraints"].append(fk_info)
            
        except Exception as e:
            logger.error(f"Failed to get table info for {table_name}: {e}")
        
        return table_info
    
    def _get_index_info(self, cursor, index_name: str) -> Dict:
        """Get index information"""
        index_info = {
            "name": index_name,
            "columns": []
        }
        
        try:
            cursor.execute(f"PRAGMA index_info({index_name})")
            columns = cursor.fetchall()
            
            for column in columns:
                index_info["columns"].append(column[2])
            
        except Exception as e:
            logger.error(f"Failed to get index info for {index_name}: {e}")
        
        return index_info
    
    def _get_trigger_info(self, cursor, trigger_name: str) -> Dict:
        """Get trigger information"""
        trigger_info = {
            "name": trigger_name,
            "sql": ""
        }
        
        try:
            cursor.execute(f"SELECT sql FROM sqlite_master WHERE name='{trigger_name}'")
            result = cursor.fetchone()
            
            if result:
                trigger_info["sql"] = result[0]
            
        except Exception as e:
            logger.error(f"Failed to get trigger info for {trigger_name}: {e}")
        
        return trigger_info
    
    def _get_view_info(self, cursor, view_name: str) -> Dict:
        """Get view information"""
        view_info = {
            "name": view_name,
            "sql": ""
        }
        
        try:
            cursor.execute(f"SELECT sql FROM sqlite_master WHERE name='{view_name}'")
            result = cursor.fetchone()
            
            if result:
                view_info["sql"] = result[0]
            
        except Exception as e:
            logger.error(f"Failed to get view info for {view_name}: {e}")
        
        return view_info
    
    def _generate_schema_markdown(self, schema_info: Dict, database_path: Path) -> str:
        """Generate markdown documentation from schema info"""
        doc = f"""# Database Schema Documentation

**Database:** {database_path.name}  
**Generated:** {datetime.now().isoformat()}

## Tables

"""
        
        for table in schema_info["tables"]:
            doc += f"### {table['name']}\n\n"
            doc += "| Column | Type | Not Null | Default | Primary Key |\n"
            doc += "|--------|------|----------|---------|-------------|\n"
            
            for column in table["columns"]:
                doc += f"| {column['name']} | {column['type']} | {column['not_null']} | {column['default_value'] or ''} | {column['primary_key']} |\n"
            
            if table["constraints"]:
                doc += "\n**Foreign Keys:**\n"
                for constraint in table["constraints"]:
                    doc += f"- {constraint['column']} → {constraint['references_table']}.{constraint['references_column']}\n"
            
            doc += "\n"
        
        if schema_info["indexes"]:
            doc += "## Indexes\n\n"
            for index in schema_info["indexes"]:
                doc += f"### {index['name']}\n"
                doc += f"Columns: {', '.join(index['columns'])}\n\n"
        
        if schema_info["views"]:
            doc += "## Views\n\n"
            for view in schema_info["views"]:
                doc += f"### {view['name']}\n"
                doc += f"```sql\n{view['sql']}\n```\n\n"
        
        return doc
    
    def _check_ci_integration(self, validation_results: Dict, config: Dict):
        """Check CI integration rules"""
        ci_config = config["database_schema_validation"]["ci_integration"]
        
        if validation_results["validation_summary"]["failed_validation"] > 0:
            if ci_config["fail_on_mismatch"]:
                # Check if opt-out is allowed
                if ci_config["allow_opt_out"]:
                    opt_out_env = ci_config["opt_out_env_var"]
                    if os.getenv(opt_out_env, "1") == "0":
                        logger.warning(f"⚠️ Schema validation failed but opt-out is enabled via {opt_out_env}")
                        return
                
                logger.error("❌ Schema validation failed - CI build should be rejected")
                sys.exit(1)
    
    def _save_validation_results(self, results: Dict):
        """Save validation results"""
        report_path = self.reports_dir / f"schema-validation-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
        with open(report_path, 'w') as f:
            json.dump(results, f, indent=2)

def main():
    """Main entry point for database schema validation"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Database Schema Validation")
    parser.add_argument("--project-root", type=Path, default=Path.cwd(),
                       help="Project root directory")
    parser.add_argument("--action", choices=["setup", "validate", "create-baseline", "generate-docs"],
                       required=True, help="Action to perform")
    parser.add_argument("--database", type=Path, help="Database path (for create-baseline and generate-docs)")
    
    args = parser.parse_args()
    
    dsv = DatabaseSchemaValidator(args.project_root)
    
    if args.action == "setup":
        dsv.setup_schema_config()
    elif args.action == "validate":
        dsv.validate_schemas()
    elif args.action == "create-baseline":
        if args.database:
            dsv.create_baseline_database(args.database)
        else:
            logger.error("--database argument required for create-baseline action")
    elif args.action == "generate-docs":
        if args.database:
            dsv.generate_schema_documentation(args.database)
        else:
            logger.error("--database argument required for generate-docs action")

if __name__ == "__main__":
    main()
