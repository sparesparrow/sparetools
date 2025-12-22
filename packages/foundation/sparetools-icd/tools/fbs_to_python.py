#!/usr/bin/env python3
"""
FlatBuffers to Python Dataclass Generator

Converts FlatBuffers schema definitions to Python dataclasses for use in MIA.
Generates type-safe Python classes that match the FlatBuffers message structures.
"""

import re
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field


class FBSToPythonGenerator:
    """Generate Python dataclasses from FlatBuffers schemas"""

    def __init__(self):
        # Type mappings from FlatBuffers to Python
        self.type_mappings = {
            'bool': 'bool',
            'byte': 'int',
            'ubyte': 'int',
            'short': 'int',
            'ushort': 'int',
            'int': 'int',
            'uint': 'int',
            'uint16': 'int',
            'uint32': 'int',
            'uint64': 'int',
            'float': 'float',
            'double': 'float',
            'string': 'str',
        }

        # Array type pattern
        self.array_pattern = re.compile(r'\[(\w+)\]')

        # Enum pattern
        self.enum_pattern = re.compile(r'enum\s+(\w+)\s*:\s*(\w+)\s*{([^}]*)}', re.DOTALL)

    def parse_enum(self, enum_text: str) -> str:
        """Parse a FlatBuffers enum definition and generate Python Enum"""
        match = self.enum_pattern.search(enum_text)
        if not match:
            return ""

        enum_name, base_type, enum_body = match.groups()

        # Parse enum values
        values = []
        for line in enum_body.strip().split('\n'):
            line = line.strip()
            if not line or line.startswith('//'):
                continue

            # Parse: VALUE = number,
            value_match = re.match(r'(\w+)\s*=\s*([^,]+)', line)
            if value_match:
                name, val = value_match.groups()
                values.append(f"    {name} = {val.strip()}")

        if not values:
            return ""

        enum_code = f"""class {enum_name}(Enum):
{chr(10).join(values)}
"""

        return enum_code

    def parse_table(self, table_text: str, enums: Dict[str, str]) -> str:
        """Parse a FlatBuffers table definition and generate Python dataclass"""
        lines = table_text.strip().split('\n')
        table_name = lines[0].split()[1]  # "table TableName {"

        fields = []
        field_defaults = []

        for line in lines[1:-1]:  # Skip table declaration and closing brace
            line = line.strip()
            if not line or line.startswith('//'):
                continue

            # Parse field: "field_name: field_type; // comment"
            match = re.match(r'(\w+):\s*([^;]+);', line)
            if match:
                field_name, field_type = match.groups()
                field_type = field_type.strip()

                python_type = self.get_python_type(field_type, enums)

                # Create field annotation
                if field_name == 'timestamp' and python_type == 'int':
                    # Special handling for timestamps
                    fields.append(f"    {field_name}: {python_type} = field(default_factory=lambda: int(time.time() * 1_000_000))")
                else:
                    fields.append(f"    {field_name}: {python_type}")

        if not fields:
            return ""

        dataclass_code = f"""@dataclass
class {table_name}:
{chr(10).join(fields)}
"""

        return dataclass_code

    def get_python_type(self, fbs_type: str, enums: Dict[str, str]) -> str:
        """Convert FlatBuffers type to Python type annotation"""
        # Handle arrays
        array_match = self.array_pattern.match(fbs_type)
        if array_match:
            item_type = array_match.group(1)
            if item_type in self.type_mappings:
                return f"List[{self.type_mappings[item_type]}]"
            elif item_type in enums:
                return f"List[{item_type}]"
            else:
                return f"List[Any]"

        # Handle basic types
        if fbs_type in self.type_mappings:
            return self.type_mappings[fbs_type]

        # Handle enums
        if fbs_type in enums:
            return fbs_type

        # Default to Any for custom types
        return "Any"

    def parse_schema_file(self, schema_path: Path) -> str:
        """Parse a FlatBuffers schema file and generate Python code"""
        with open(schema_path, 'r') as f:
            content = f.read()

        # Extract namespace
        namespace_match = re.search(r'namespace\s+([^;]+);', content)
        namespace = namespace_match.group(1) if namespace_match else "sparetools.icd"

        # Extract enums first
        enums = {}
        for match in self.enum_pattern.finditer(content):
            enum_name = match.group(1)
            enum_code = self.parse_enum(match.group(0))
            if enum_code:
                enums[enum_name] = enum_code

        # Extract table definitions
        tables = []
        table_pattern = re.compile(r'table\s+(\w+)\s*{([^}]*)}', re.DOTALL)

        for match in table_pattern.finditer(content):
            table_name = match.group(1)
            table_content = match.group(2)

            table_code = self.parse_table(f"table {table_name} {{\n{table_content}\n}}", enums)
            if table_code:
                tables.append(table_code)

        # Generate Python module
        imports = [
            "from dataclasses import dataclass, field",
            "from typing import List, Any",
            "from enum import Enum",
            "import time"
        ]

        module_code = f'''"""Generated Python dataclasses for {namespace}"""

{chr(10).join(imports)}

# Enums
{chr(10).join(enums.values())}

# Tables
{chr(10).join(tables)}
'''

        return module_code

    def generate_python_module(self, schema_path: Path, output_path: Optional[Path] = None) -> str:
        """Generate Python module from schema file"""
        python_code = self.parse_schema_file(schema_path)

        if output_path:
            with open(output_path, 'w') as f:
                f.write(python_code)
            print(f"Generated Python module written to {output_path}")

        return python_code


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description='Generate Python dataclasses from FlatBuffers schemas')
    parser.add_argument('schema_file', type=Path, help='FlatBuffers schema file (.fbs)')
    parser.add_argument('-o', '--output', type=Path, help='Output Python file')

    args = parser.parse_args()

    generator = FBSToPythonGenerator()
    python_code = generator.generate_python_module(args.schema_file, args.output)

    if not args.output:
        print(python_code)


if __name__ == '__main__':
    main()