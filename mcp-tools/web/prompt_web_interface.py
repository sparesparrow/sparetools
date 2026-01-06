#!/usr/bin/env python3
"""
Web interface for the Prompt Renderer

A Flask-based web interface for rendering prompts through a browser.
"""

from flask import Flask, render_template, request, jsonify, send_file
import json
import tempfile
import os
from prompt_renderer import PromptRenderer

app = Flask(__name__)
renderer = PromptRenderer("prompt_templates", "mcp_prompts.json")

@app.route('/')
def index():
    """Main page with template selection and form."""
    templates = renderer.list_templates()
    mcp_prompts = renderer.list_mcp_prompts()
    categories = renderer.get_categories()
    return render_template('prompt_index.html', 
                         templates=templates, 
                         mcp_prompts=mcp_prompts,
                         categories=categories)

@app.route('/api/templates')
def get_templates():
    """API endpoint to get available templates."""
    return jsonify(renderer.list_templates())

@app.route('/api/mcp-prompts')
def get_mcp_prompts():
    """API endpoint to get MCP database prompts."""
    return jsonify(renderer.list_mcp_prompts())

@app.route('/api/categories')
def get_categories():
    """API endpoint to get available categories."""
    return jsonify(renderer.get_categories())

@app.route('/api/search')
def search_prompts():
    """API endpoint to search prompts."""
    query = request.args.get('q', '')
    category = request.args.get('category', '')
    results = renderer.search_prompts(query, category)
    return jsonify(results)

@app.route('/api/render', methods=['POST'])
def render_prompt():
    """API endpoint to render a prompt."""
    try:
        data = request.get_json()
        template_name = data.get('template_name')
        variables = data.get('variables', {})
        
        # Render prompt
        rendered = renderer.render_prompt(template_name, variables)
        
        return jsonify({
            'success': True,
            'rendered_prompt': rendered,
            'template_name': template_name,
            'variables': variables
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@app.route('/api/export', methods=['POST'])
def export_prompt():
    """API endpoint to export a rendered prompt."""
    try:
        data = request.get_json()
        template_name = data.get('template_name')
        variables = data.get('variables', {})
        format_type = data.get('format', 'txt')
        
        # Render prompt
        rendered = renderer.render_prompt(template_name, variables)
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix=f'.{format_type}') as f:
            if format_type == 'json':
                export_data = {
                    'template_name': template_name,
                    'variables': variables,
                    'rendered_content': rendered,
                    'metadata': renderer.get_template(template_name)['metadata'] if renderer.get_template(template_name) else {}
                }
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            else:
                f.write(rendered)
            temp_file = f.name
        
        return send_file(temp_file, as_attachment=True, 
                       download_name=f'{template_name}_prompt.{format_type}')
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@app.route('/api/mcp/add', methods=['POST'])
def add_mcp_prompt():
    """API endpoint to add a new MCP prompt."""
    try:
        data = request.get_json()
        name = data.get('name')
        content = data.get('content')
        metadata = data.get('metadata', {})
        
        renderer.add_mcp_prompt(name, content, metadata)
        
        return jsonify({
            'success': True,
            'message': f'Prompt "{name}" added successfully'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@app.route('/api/mcp/update', methods=['POST'])
def update_mcp_prompt():
    """API endpoint to update an MCP prompt."""
    try:
        data = request.get_json()
        name = data.get('name')
        content = data.get('content')
        metadata = data.get('metadata')
        
        renderer.update_mcp_prompt(name, content, metadata)
        
        return jsonify({
            'success': True,
            'message': f'Prompt "{name}" updated successfully'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@app.route('/api/mcp/delete', methods=['POST'])
def delete_mcp_prompt():
    """API endpoint to delete an MCP prompt."""
    try:
        data = request.get_json()
        name = data.get('name')
        
        renderer.delete_mcp_prompt(name)
        
        return jsonify({
            'success': True,
            'message': f'Prompt "{name}" deleted successfully'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

if __name__ == '__main__':
    # Create templates directory for Flask
    os.makedirs('templates', exist_ok=True)
    
    # Create HTML template
    html_template = '''
<!DOCTYPE html>
<html>
<head>
    <title>Prompt Template Renderer</title>
    <style>
        body { 
            font-family: Arial, sans-serif; 
            margin: 20px; 
            background-color: #f5f5f5;
        }
        .container { 
            max-width: 1200px; 
            margin: 0 auto; 
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 2px solid #e0e0e0;
        }
        .tabs {
            display: flex;
            margin-bottom: 20px;
            border-bottom: 1px solid #ddd;
        }
        .tab {
            padding: 10px 20px;
            cursor: pointer;
            border: none;
            background: none;
            border-bottom: 2px solid transparent;
        }
        .tab.active {
            border-bottom-color: #007bff;
            color: #007bff;
        }
        .tab-content {
            display: none;
        }
        .tab-content.active {
            display: block;
        }
        .form-group { 
            margin: 15px 0; 
        }
        label { 
            display: block; 
            margin-bottom: 5px; 
            font-weight: bold; 
            color: #333;
        }
        select, textarea, input { 
            width: 100%; 
            padding: 10px; 
            margin-bottom: 10px; 
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 14px;
        }
        textarea { 
            height: 200px; 
            font-family: 'Courier New', monospace; 
            resize: vertical;
        }
        .variables-section {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 4px;
            margin: 15px 0;
        }
        .variable-input {
            display: flex;
            margin-bottom: 10px;
        }
        .variable-input input {
            flex: 1;
            margin-right: 10px;
        }
        .variable-input button {
            padding: 10px 15px;
            background: #dc3545;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
        }
        .add-variable {
            background: #28a745;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            margin-bottom: 15px;
        }
        button { 
            background: #007bff; 
            color: white; 
            padding: 10px 20px; 
            border: none; 
            border-radius: 4px;
            cursor: pointer; 
            margin-right: 10px;
            margin-bottom: 10px;
        }
        button:hover { 
            background: #0056b3; 
        }
        .result-container { 
            margin-top: 20px; 
            border: 1px solid #ddd; 
            padding: 20px; 
            border-radius: 4px;
            background: #f8f9fa;
        }
        .result-content {
            background: white;
            padding: 15px;
            border-radius: 4px;
            white-space: pre-wrap;
            font-family: 'Courier New', monospace;
            max-height: 400px;
            overflow-y: auto;
        }
        .error { 
            color: #dc3545; 
            margin-top: 10px; 
            padding: 10px;
            background: #f8d7da;
            border: 1px solid #f5c6cb;
            border-radius: 4px;
        }
        .success { 
            color: #155724; 
            margin-top: 10px; 
            padding: 10px;
            background: #d4edda;
            border: 1px solid #c3e6cb;
            border-radius: 4px;
        }
        .search-section {
            margin-bottom: 20px;
        }
        .search-results {
            margin-top: 15px;
        }
        .search-result {
            padding: 10px;
            border: 1px solid #ddd;
            margin-bottom: 10px;
            border-radius: 4px;
            cursor: pointer;
        }
        .search-result:hover {
            background: #f8f9fa;
        }
        .mcp-section {
            background: #e3f2fd;
            padding: 15px;
            border-radius: 4px;
            margin: 15px 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Prompt Template Renderer</h1>
            <p>Render and manage prompt templates with variable substitution</p>
        </div>
        
        <div class="tabs">
            <button class="tab active" onclick="showTab('render')">Render Prompt</button>
            <button class="tab" onclick="showTab('search')">Search Templates</button>
            <button class="tab" onclick="showTab('mcp')">MCP Database</button>
        </div>
        
        <!-- Render Tab -->
        <div id="render" class="tab-content active">
            <div class="form-group">
                <label for="template">Template:</label>
                <select id="template">
                    <option value="">Select a template...</option>
                    {% for name, metadata in templates.items() %}
                    <option value="{{ name }}">{{ name }} - {{ metadata.description }}</option>
                    {% endfor %}
                    {% for name, prompt in mcp_prompts.items() %}
                    <option value="{{ name }}">{{ name }} (MCP) - {{ prompt.metadata.description }}</option>
                    {% endfor %}
                </select>
            </div>
            
            <div class="variables-section">
                <h3>Variables</h3>
                <button class="add-variable" onclick="addVariable()">Add Variable</button>
                <div id="variables-container"></div>
            </div>
            
            <div class="form-group">
                <label for="format">Output Format:</label>
                <select id="format">
                    <option value="txt">Plain Text</option>
                    <option value="md">Markdown</option>
                    <option value="json">JSON</option>
                </select>
            </div>
            
            <button onclick="renderPrompt()">Render Prompt</button>
            <button onclick="exportPrompt()">Export Prompt</button>
            <button onclick="loadTemplateDefaults()">Load Defaults</button>
            
            <div id="result" class="result-container" style="display: none;">
                <h3>Rendered Prompt:</h3>
                <div id="rendered-content" class="result-content"></div>
            </div>
        </div>
        
        <!-- Search Tab -->
        <div id="search" class="tab-content">
            <div class="search-section">
                <input type="text" id="search-query" placeholder="Search prompts..." style="width: 70%;">
                <select id="search-category" style="width: 25%;">
                    <option value="">All Categories</option>
                    {% for category in categories %}
                    <option value="{{ category }}">{{ category }}</option>
                    {% endfor %}
                </select>
                <button onclick="searchPrompts()">Search</button>
            </div>
            
            <div id="search-results" class="search-results"></div>
        </div>
        
        <!-- MCP Tab -->
        <div id="mcp" class="tab-content">
            <div class="mcp-section">
                <h3>MCP Database Management</h3>
                <button onclick="showAddMCPForm()">Add New Prompt</button>
                <button onclick="loadMCPPrompts()">Refresh List</button>
            </div>
            
            <div id="mcp-form" style="display: none;">
                <h4>Add/Edit MCP Prompt</h4>
                <div class="form-group">
                    <label for="mcp-name">Name:</label>
                    <input type="text" id="mcp-name" placeholder="prompt-name">
                </div>
                <div class="form-group">
                    <label for="mcp-content">Content:</label>
                    <textarea id="mcp-content" placeholder="Prompt content with {{ variables }}"></textarea>
                </div>
                <div class="form-group">
                    <label for="mcp-description">Description:</label>
                    <input type="text" id="mcp-description" placeholder="Prompt description">
                </div>
                <div class="form-group">
                    <label for="mcp-category">Category:</label>
                    <input type="text" id="mcp-category" placeholder="category">
                </div>
                <button onclick="saveMCPPrompt()">Save Prompt</button>
                <button onclick="hideMCPForm()">Cancel</button>
            </div>
            
            <div id="mcp-list"></div>
        </div>
        
        <div id="message"></div>
    </div>

    <script>
        let variables = {};
        
        function showTab(tabName) {
            // Hide all tabs
            document.querySelectorAll('.tab-content').forEach(tab => {
                tab.classList.remove('active');
            });
            document.querySelectorAll('.tab').forEach(tab => {
                tab.classList.remove('active');
            });
            
            // Show selected tab
            document.getElementById(tabName).classList.add('active');
            event.target.classList.add('active');
        }
        
        function addVariable() {
            const container = document.getElementById('variables-container');
            const div = document.createElement('div');
            div.className = 'variable-input';
            div.innerHTML = `
                <input type="text" placeholder="Variable name" class="var-name">
                <input type="text" placeholder="Variable value" class="var-value">
                <button onclick="removeVariable(this)">Remove</button>
            `;
            container.appendChild(div);
        }
        
        function removeVariable(button) {
            button.parentElement.remove();
        }
        
        function collectVariables() {
            const container = document.getElementById('variables-container');
            const inputs = container.querySelectorAll('.variable-input');
            variables = {};
            
            inputs.forEach(input => {
                const name = input.querySelector('.var-name').value;
                const value = input.querySelector('.var-value').value;
                if (name && value) {
                    variables[name] = value;
                }
            });
        }
        
        async function renderPrompt() {
            const template = document.getElementById('template').value;
            if (!template) {
                showMessage('Please select a template', 'error');
                return;
            }
            
            collectVariables();
            
            try {
                const response = await fetch('/api/render', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        template_name: template,
                        variables: variables
                    })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    document.getElementById('rendered-content').textContent = data.rendered_prompt;
                    document.getElementById('result').style.display = 'block';
                    showMessage('Prompt rendered successfully!', 'success');
                } else {
                    showMessage('Error: ' + data.error, 'error');
                }
            } catch (error) {
                showMessage('Error: ' + error.message, 'error');
            }
        }
        
        async function exportPrompt() {
            const template = document.getElementById('template').value;
            const format = document.getElementById('format').value;
            
            if (!template) {
                showMessage('Please select a template', 'error');
                return;
            }
            
            collectVariables();
            
            try {
                const response = await fetch('/api/export', {
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
                
                if (response.ok) {
                    const blob = await response.blob();
                    const url = window.URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = `${template}_prompt.${format}`;
                    a.click();
                    showMessage('Prompt exported successfully!', 'success');
                } else {
                    const error = await response.json();
                    showMessage('Error: ' + error.error, 'error');
                }
            } catch (error) {
                showMessage('Error: ' + error.message, 'error');
            }
        }
        
        async function loadTemplateDefaults() {
            const template = document.getElementById('template').value;
            if (!template) {
                showMessage('Please select a template first', 'error');
                return;
            }
            
            try {
                const response = await fetch('/api/templates');
                const templates = await response.json();
                
                if (templates[template] && templates[template].variables) {
                    const container = document.getElementById('variables-container');
                    container.innerHTML = '';
                    
                    Object.entries(templates[template].variables).forEach(([key, value]) => {
                        addVariable();
                        const inputs = container.lastElementChild.querySelectorAll('input');
                        inputs[0].value = key;
                        inputs[1].value = value;
                    });
                    
                    showMessage('Default variables loaded!', 'success');
                }
            } catch (error) {
                showMessage('Error loading defaults: ' + error.message, 'error');
            }
        }
        
        async function searchPrompts() {
            const query = document.getElementById('search-query').value;
            const category = document.getElementById('search-category').value;
            
            if (!query) {
                showMessage('Please enter a search query', 'error');
                return;
            }
            
            try {
                const response = await fetch(`/api/search?q=${encodeURIComponent(query)}&category=${encodeURIComponent(category)}`);
                const results = await response.json();
                
                const container = document.getElementById('search-results');
                container.innerHTML = '';
                
                if (results.length === 0) {
                    container.innerHTML = '<p>No results found</p>';
                    return;
                }
                
                results.forEach(result => {
                    const div = document.createElement('div');
                    div.className = 'search-result';
                    div.innerHTML = `
                        <h4>${result.name} (${result.type})</h4>
                        <p><strong>Description:</strong> ${result.metadata.description || 'No description'}</p>
                        <p><strong>Category:</strong> ${result.metadata.category || 'No category'}</p>
                        <p><strong>Content Preview:</strong> ${result.content}</p>
                    `;
                    div.onclick = () => {
                        document.getElementById('template').value = result.name;
                        showTab('render');
                    };
                    container.appendChild(div);
                });
                
            } catch (error) {
                showMessage('Error searching: ' + error.message, 'error');
            }
        }
        
        function showAddMCPForm() {
            document.getElementById('mcp-form').style.display = 'block';
        }
        
        function hideMCPForm() {
            document.getElementById('mcp-form').style.display = 'none';
        }
        
        async function saveMCPPrompt() {
            const name = document.getElementById('mcp-name').value;
            const content = document.getElementById('mcp-content').value;
            const description = document.getElementById('mcp-description').value;
            const category = document.getElementById('mcp-category').value;
            
            if (!name || !content) {
                showMessage('Name and content are required', 'error');
                return;
            }
            
            try {
                const response = await fetch('/api/mcp/add', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        name: name,
                        content: content,
                        metadata: {
                            description: description,
                            category: category
                        }
                    })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    showMessage(data.message, 'success');
                    hideMCPForm();
                    loadMCPPrompts();
                } else {
                    showMessage('Error: ' + data.error, 'error');
                }
            } catch (error) {
                showMessage('Error: ' + error.message, 'error');
            }
        }
        
        async function loadMCPPrompts() {
            try {
                const response = await fetch('/api/mcp-prompts');
                const prompts = await response.json();
                
                const container = document.getElementById('mcp-list');
                container.innerHTML = '<h3>MCP Database Prompts</h3>';
                
                Object.entries(prompts).forEach(([name, prompt]) => {
                    const div = document.createElement('div');
                    div.className = 'search-result';
                    div.innerHTML = `
                        <h4>${name}</h4>
                        <p><strong>Description:</strong> ${prompt.metadata.description || 'No description'}</p>
                        <p><strong>Category:</strong> ${prompt.metadata.category || 'No category'}</p>
                        <button onclick="deleteMCPPrompt('${name}')">Delete</button>
                    `;
                    container.appendChild(div);
                });
                
            } catch (error) {
                showMessage('Error loading MCP prompts: ' + error.message, 'error');
            }
        }
        
        async function deleteMCPPrompt(name) {
            if (!confirm(`Are you sure you want to delete "${name}"?`)) {
                return;
            }
            
            try {
                const response = await fetch('/api/mcp/delete', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        name: name
                    })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    showMessage(data.message, 'success');
                    loadMCPPrompts();
                } else {
                    showMessage('Error: ' + data.error, 'error');
                }
            } catch (error) {
                showMessage('Error: ' + error.message, 'error');
            }
        }
        
        function showMessage(text, type) {
            const messageDiv = document.getElementById('message');
            messageDiv.textContent = text;
            messageDiv.className = type;
            setTimeout(() => {
                messageDiv.textContent = '';
                messageDiv.className = '';
            }, 5000);
        }
        
        // Load MCP prompts on page load
        window.onload = function() {
            loadMCPPrompts();
        };
    </script>
</body>
</html>
    '''
    
    with open('templates/prompt_index.html', 'w') as f:
        f.write(html_template)
    
    print("Starting prompt renderer web interface...")
    print("Open http://localhost:5001 in your browser")
    app.run(debug=True, host='0.0.0.0', port=5001)