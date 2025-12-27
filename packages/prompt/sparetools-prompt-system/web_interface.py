#!/usr/bin/env python3
"""
Web interface for the Mermaid Diagram Generator

A simple Flask-based web interface for generating diagrams through a browser.
"""

from flask import Flask, render_template, request, jsonify, send_file
import json
import tempfile
import os
from diagram_generator import DiagramGenerator

app = Flask(__name__)
generator = DiagramGenerator("diagram_templates")

@app.route('/')
def index():
    """Main page with template selection and form."""
    templates = generator.list_templates()
    return render_template('index.html', templates=templates)

@app.route('/api/templates')
def get_templates():
    """API endpoint to get available templates."""
    return jsonify(generator.list_templates())

@app.route('/api/generate', methods=['POST'])
def generate_diagram():
    """API endpoint to generate a diagram."""
    try:
        data = request.get_json()
        template_name = data.get('template_name')
        variables = data.get('variables', {})
        output_format = data.get('format', 'svg')
        
        # Generate diagram
        mermaid_code = generator.generate_diagram(template_name, variables)
        
        # If format is not 'raw', export the diagram
        if output_format != 'raw':
            with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{output_format}') as f:
                temp_file = f.name
            
            generator.export_diagram(mermaid_code, output_format, temp_file)
            
            return send_file(temp_file, as_attachment=True, 
                           download_name=f'diagram.{output_format}')
        else:
            return jsonify({
                'success': True,
                'mermaid_code': mermaid_code
            })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@app.route('/api/examples')
def get_examples():
    """API endpoint to get example configurations."""
    try:
        with open('config/diagram_configs.json', 'r') as f:
            examples = json.load(f)
        return jsonify(examples)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Create templates directory for Flask
    os.makedirs('templates', exist_ok=True)
    
    # Create basic HTML template
    html_template = '''
<!DOCTYPE html>
<html>
<head>
    <title>Mermaid Diagram Generator</title>
    <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .container { max-width: 1200px; margin: 0 auto; }
        .form-group { margin: 10px 0; }
        label { display: block; margin-bottom: 5px; font-weight: bold; }
        select, textarea, input { width: 100%; padding: 8px; margin-bottom: 10px; }
        textarea { height: 200px; font-family: monospace; }
        button { background: #007bff; color: white; padding: 10px 20px; border: none; cursor: pointer; }
        button:hover { background: #0056b3; }
        .diagram-container { margin-top: 20px; border: 1px solid #ddd; padding: 20px; }
        .error { color: red; margin-top: 10px; }
        .success { color: green; margin-top: 10px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Mermaid Diagram Generator</h1>
        
        <div class="form-group">
            <label for="template">Template:</label>
            <select id="template">
                {% for name, metadata in templates.items() %}
                <option value="{{ name }}">{{ name }} - {{ metadata.description }}</option>
                {% endfor %}
            </select>
        </div>
        
        <div class="form-group">
            <label for="variables">Variables (JSON):</label>
            <textarea id="variables" placeholder='{"title": "My Diagram", "steps": ["Start", "End"]}'></textarea>
        </div>
        
        <div class="form-group">
            <label for="format">Output Format:</label>
            <select id="format">
                <option value="raw">Raw Mermaid Code</option>
                <option value="svg">SVG</option>
                <option value="png">PNG</option>
                <option value="pdf">PDF</option>
            </select>
        </div>
        
        <button onclick="generateDiagram()">Generate Diagram</button>
        <button onclick="loadExample()">Load Example</button>
        
        <div id="result" class="diagram-container" style="display: none;">
            <h3>Generated Diagram:</h3>
            <div id="diagram"></div>
        </div>
        
        <div id="message"></div>
    </div>

    <script>
        mermaid.initialize({ startOnLoad: false });
        
        async function generateDiagram() {
            const template = document.getElementById('template').value;
            const variablesText = document.getElementById('variables').value;
            const format = document.getElementById('format').value;
            
            try {
                const variables = JSON.parse(variablesText);
                
                const response = await fetch('/api/generate', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        template_name: template,
                        variables: variables,
                        format: format
                    })
                });
                
                if (format === 'raw') {
                    const data = await response.json();
                    if (data.success) {
                        document.getElementById('diagram').innerHTML = '<pre>' + data.mermaid_code + '</pre>';
                        document.getElementById('result').style.display = 'block';
                        mermaid.init(undefined, document.getElementById('diagram'));
                        showMessage('Diagram generated successfully!', 'success');
                    } else {
                        showMessage('Error: ' + data.error, 'error');
                    }
                } else {
                    if (response.ok) {
                        const blob = await response.blob();
                        const url = window.URL.createObjectURL(blob);
                        const a = document.createElement('a');
                        a.href = url;
                        a.download = 'diagram.' + format;
                        a.click();
                        showMessage('Diagram downloaded successfully!', 'success');
                    } else {
                        const error = await response.json();
                        showMessage('Error: ' + error.error, 'error');
                    }
                }
            } catch (error) {
                showMessage('Error parsing JSON: ' + error.message, 'error');
            }
        }
        
        async function loadExample() {
            try {
                const response = await fetch('/api/examples');
                const examples = await response.json();
                
                // Load first example from flowchart_examples
                if (examples.flowchart_examples) {
                    const example = examples.flowchart_examples.simple_process;
                    document.getElementById('variables').value = JSON.stringify(example.variables, null, 2);
                }
            } catch (error) {
                showMessage('Error loading examples: ' + error.message, 'error');
            }
        }
        
        function showMessage(text, type) {
            const messageDiv = document.getElementById('message');
            messageDiv.textContent = text;
            messageDiv.className = type;
        }
    </script>
</body>
</html>
    '''
    
    with open('templates/index.html', 'w') as f:
        f.write(html_template)
    
    print("Starting web interface...")
    print("Open http://localhost:5000 in your browser")
    app.run(debug=True, host='0.0.0.0', port=5000)