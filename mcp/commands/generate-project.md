# generateProject

Generate a complete project structure from a template

## Usage

```json
{
  "template_name": "fastapi-project",
  "variables": {
    "project_name": "my-api",
    "author": "John Doe",
    "description": "REST API for user management"
  },
  "output_dir": "./generated-projects/my-api"
}
```

## Description

Creates complete project structures with all necessary files, directories, configuration files, and boilerplate code based on predefined templates.

## Parameters

- `template_name` (string, required): Name of the project template
- `variables` (object, optional): Variables for project generation (project name, author, etc.)
- `output_dir` (string, required): Directory where the project will be created

## Examples

```json
{
  "template_name": "react-typescript-app",
  "variables": {
    "project_name": "task-manager",
    "author": "Jane Smith",
    "description": "A modern task management application"
  },
  "output_dir": "./projects/task-manager"
}
```

## Available Project Templates

- `fastapi-project`: Python FastAPI backend
- `react-typescript-app`: React with TypeScript frontend
- `django-project`: Django web application
- `node-express-api`: Node.js Express API
- `flutter-mobile-app`: Flutter mobile application
- `docker-microservice`: Containerized microservice

## Generated Structure

Projects include:
- Source code with proper structure
- Configuration files (package.json, requirements.txt, etc.)
- Docker files and docker-compose.yml
- Documentation (README.md)
- Testing setup
- CI/CD configuration

## Related Commands

- `generateComponent`: Generate individual components
- `generateDiagram`: Create project architecture diagrams
- `renderPrompt`: Generate documentation templates