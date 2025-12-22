#!/usr/bin/env python3
"""
FlatBuffers to MCP Tool Generator

Converts FlatBuffers schema definitions to MCP (Model Context Protocol) tool definitions.
Generates JSON schemas for AI agents to interact with hardware interfaces.
"""

import re
import json
from pathlib import Path
from typing import Dict, List, Any, Optional


class FBSToMCPGenerator:
    """Generate MCP tool definitions from FlatBuffers schemas"""

    def __init__(self):
        # Type mappings from FlatBuffers to JSON Schema
        self.type_mappings = {
            'bool': {'type': 'boolean'},
            'byte': {'type': 'integer', 'minimum': -128, 'maximum': 127},
            'ubyte': {'type': 'integer', 'minimum': 0, 'maximum': 255},
            'short': {'type': 'integer', 'minimum': -32768, 'maximum': 32767},
            'ushort': {'type': 'integer', 'minimum': 0, 'maximum': 65535},
            'int': {'type': 'integer', 'minimum': -2147483648, 'maximum': 2147483647},
            'uint': {'type': 'integer', 'minimum': 0, 'maximum': 4294967295},
            'uint16': {'type': 'integer', 'minimum': 0, 'maximum': 65535},
            'uint32': {'type': 'integer', 'minimum': 0, 'maximum': 4294967295},
            'uint64': {'type': 'integer', 'minimum': 0},
            'float': {'type': 'number'},
            'double': {'type': 'number'},
            'string': {'type': 'string'},
        }

        # Array type pattern
        self.array_pattern = re.compile(r'\[(\w+)\]')

    def parse_table(self, table_text: str) -> Dict[str, Any]:
        """Parse a FlatBuffers table definition"""
        lines = table_text.strip().split('\n')
        table_name = lines[0].split()[1]  # "table TableName {"

        properties = {}
        required = []

        for line in lines[1:-1]:  # Skip table declaration and closing brace
            line = line.strip()
            if not line or line.startswith('//'):
                continue

            # Parse field: "field_name: field_type; // comment"
            match = re.match(r'(\w+):\s*([^;]+);', line)
            if match:
                field_name, field_type = match.groups()
                field_type = field_type.strip()

                # Handle arrays
                array_match = self.array_pattern.match(field_type)
                if array_match:
                    item_type = array_match.group(1)
                    if item_type in self.type_mappings:
                        properties[field_name] = {
                            'type': 'array',
                            'items': self.type_mappings[item_type].copy()
                        }
                    else:
                        # Custom type array
                        properties[field_name] = {
                            'type': 'array',
                            'items': {'type': 'object'}  # Placeholder for custom types
                        }
                elif field_type in self.type_mappings:
                    properties[field_name] = self.type_mappings[field_type].copy()
                else:
                    # Custom type - assume object
                    properties[field_name] = {'type': 'object'}

                # Assume all fields are required for now
                required.append(field_name)

        return {
            'type': 'object',
            'properties': properties,
            'required': required
        }

    def parse_schema_file(self, schema_path: Path) -> Dict[str, Dict[str, Any]]:
        """Parse a FlatBuffers schema file and extract table definitions"""
        with open(schema_path, 'r') as f:
            content = f.read()

        # Extract namespace
        namespace_match = re.search(r'namespace\s+([^;]+);', content)
        namespace = namespace_match.group(1) if namespace_match else ""

        # Extract table definitions
        tables = {}
        table_pattern = re.compile(r'table\s+(\w+)\s*{([^}]*)}', re.DOTALL)

        for match in table_pattern.finditer(content):
            table_name = match.group(1)
            table_content = match.group(2)

            # Parse table fields
            schema = self.parse_table(f"table {table_name} {{\n{table_content}\n}}")
            tables[table_name] = schema

        return tables

    def generate_mcp_tools(self, schema_path: Path) -> Dict[str, Dict[str, Any]]:
        """Generate MCP tool definitions from a schema file"""
        tables = self.parse_schema_file(schema_path)
        tools = {}

        # Create tools based on common patterns
        schema_name = schema_path.stem  # hardware, obd, rf

        if schema_name == 'hardware':
            # GPIO tools
            if 'GPIOCommand' in tables:
                tools['set_gpio_pin'] = {
                    'description': 'Control GPIO pins on Raspberry Pi',
                    'input_schema': tables['GPIOCommand']
                }
            if 'SerialCommand' in tables:
                tools['send_serial_command'] = {
                    'description': 'Send command via serial interface',
                    'input_schema': tables['SerialCommand']
                }

        elif schema_name == 'obd':
            # OBD tools
            if 'OBDQuery' in tables:
                tools['query_obd'] = {
                    'description': 'Query OBD-II diagnostic data from vehicle',
                    'input_schema': tables['OBDQuery']
                }
            if 'DTCQuery' in tables:
                tools['query_dtcs'] = {
                    'description': 'Query Diagnostic Trouble Codes from vehicle',
                    'input_schema': tables['DTCQuery']
                }
            if 'DTCClear' in tables:
                tools['clear_dtcs'] = {
                    'description': 'Clear Diagnostic Trouble Codes from vehicle',
                    'input_schema': tables['DTCClear']
                }

        elif schema_name == 'rf':
            # RF tools
            if 'RFCaptureStart' in tables:
                tools['start_rf_capture'] = {
                    'description': 'Start RF signal capture on NucleusESP32',
                    'input_schema': tables['RFCaptureStart']
                }
            if 'RFCaptureStop' in tables:
                tools['stop_rf_capture'] = {
                    'description': 'Stop RF signal capture on NucleusESP32',
                    'input_schema': tables['RFCaptureStop']
                }
            if 'RFReplay' in tables:
                tools['replay_rf_signal'] = {
                    'description': 'Replay captured RF signal on NucleusESP32',
                    'input_schema': tables['RFReplay']
                }
            if 'RFSpectrumQuery' in tables:
                tools['analyze_rf_spectrum'] = {
                    'description': 'Perform RF spectrum analysis',
                    'input_schema': tables['RFSpectrumQuery']
                }

        return tools

    def generate_all_tools(self, schemas_dir: Path) -> Dict[str, Dict[str, Any]]:
        """Generate MCP tools from all schema files"""
        all_tools = {}

        for schema_file in schemas_dir.glob('*.fbs'):
            tools = self.generate_mcp_tools(schema_file)
            all_tools.update(tools)

        return all_tools


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description='Generate MCP tools from FlatBuffers schemas')
    parser.add_argument('schemas_dir', type=Path, help='Directory containing .fbs schema files')
    parser.add_argument('-o', '--output', type=Path, help='Output JSON file (default: stdout)')

    args = parser.parse_args()

    generator = FBSToMCPGenerator()
    tools = generator.generate_all_tools(args.schemas_dir)

    tools_json = json.dumps(tools, indent=2)

    if args.output:
        with open(args.output, 'w') as f:
            f.write(tools_json)
        print(f"Generated MCP tools written to {args.output}")
    else:
        print(tools_json)


if __name__ == '__main__':
    main()