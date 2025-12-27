#!/usr/bin/env python3
"""
Mock MCP server for testing gamepad mapper functionality
"""
import json
import sys

def send_response(response):
    print(json.dumps(response), flush=True)

def handle_request(request):
    method = request.get('method')
    req_id = request.get('id')

    if method == 'initialize':
        # Respond to initialization
        response = {
            'jsonrpc': '2.0',
            'id': req_id,
            'result': {
                'protocolVersion': '2024-11-05',
                'capabilities': {
                    'tools': {}
                },
                'serverInfo': {
                    'name': 'gamepad-mapper-mock',
                    'version': '1.0.0'
                }
            }
        }
        send_response(response)

    elif method == 'tools/list':
        # List available tools
        response = {
            'jsonrpc': '2.0',
            'id': req_id,
            'result': {
                'tools': [
                    {
                        'name': 'add_mapping',
                        'description': 'Add a new gamepad to keyboard/mouse mapping',
                        'inputSchema': {
                            'type': 'object',
                            'properties': {
                                'input': {
                                    'type': 'string',
                                    'description': 'Gamepad input (e.g., A, B, LEFT_X)'
                                },
                                'output': {
                                    'type': 'string',
                                    'description': 'Output action (e.g., KEY_ENTER, MOUSE_LEFT_CLICK)'
                                }
                            },
                            'required': ['input', 'output']
                        }
                    },
                    {
                        'name': 'remove_mapping',
                        'description': 'Remove an existing gamepad mapping',
                        'inputSchema': {
                            'type': 'object',
                            'properties': {
                                'input': {
                                    'type': 'string',
                                    'description': 'Gamepad input to remove mapping for'
                                }
                            },
                            'required': ['input']
                        }
                    },
                    {
                        'name': 'get_status',
                        'description': 'Get the current status of the gamepad mapper',
                        'inputSchema': {
                            'type': 'object',
                            'properties': {}
                        }
                    }
                ]
            }
        }
        send_response(response)

    elif method == 'tools/call':
        params = request.get('params', {})
        tool_name = params.get('name')

        if tool_name == 'add_mapping':
            args = params.get('arguments', {})
            input_val = args.get('input', 'unknown')
            output_val = args.get('output', 'unknown')

            response = {
                'jsonrpc': '2.0',
                'id': req_id,
                'result': {
                    'content': [
                        {
                            'type': 'text',
                            'text': f'Successfully added mapping: {input_val} -> {output_val}'
                        }
                    ]
                }
            }

        elif tool_name == 'remove_mapping':
            args = params.get('arguments', {})
            input_val = args.get('input', 'unknown')

            response = {
                'jsonrpc': '2.0',
                'id': req_id,
                'result': {
                    'content': [
                        {
                            'type': 'text',
                            'text': f'Successfully removed mapping for: {input_val}'
                        }
                    ]
                }
            }

        elif tool_name == 'get_status':
            response = {
                'jsonrpc': '2.0',
                'id': req_id,
                'result': {
                    'content': [
                        {
                            'type': 'text',
                            'text': 'Gamepad Mapper Status:\n- Server: Running (Mock)\n- Backends: X11, Wayland, KDE, SDL2, UInput\n- MCP Protocol: Enabled\n- Status: Ready for testing'
                        }
                    ]
                }
            }

        else:
            response = {
                'jsonrpc': '2.0',
                'id': req_id,
                'error': {
                    'code': -32601,
                    'message': f'Tool not found: {tool_name}'
                }
            }

        send_response(response)

    else:
        # Unknown method
        response = {
            'jsonrpc': '2.0',
            'id': req_id,
            'error': {
                'code': -32601,
                'message': f'Method not found: {method}'
            }
        }
        send_response(response)

def main():
    # Read JSON-RPC requests from stdin
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue

        try:
            request = json.loads(line)
            handle_request(request)
        except json.JSONDecodeError as e:
            # Send parse error response
            error_response = {
                'jsonrpc': '2.0',
                'error': {
                    'code': -32700,
                    'message': f'Parse error: {str(e)}'
                },
                'id': None
            }
            send_response(error_response)

if __name__ == '__main__':
    main()