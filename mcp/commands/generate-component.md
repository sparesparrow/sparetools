# generateComponent

Generate individual components from templates

## Usage

```json
{
  "template_name": "react-component",
  "variables": {
    "component_name": "UserProfile",
    "props": ["userId", "onEdit"],
    "hooks": ["useState", "useEffect"]
  },
  "output_dir": "./components"
}
```

## Description

Creates individual components, modules, or code snippets based on specific templates. Useful for adding functionality to existing projects.

## Parameters

- `template_name` (string, required): Name of the component template
- `variables` (object, optional): Variables for component generation
- `output_dir` (string, required): Directory where the component will be created

## Examples

```json
{
  "template_name": "database-model",
  "variables": {
    "model_name": "User",
    "fields": [
      {"name": "id", "type": "UUID", "primary": true},
      {"name": "email", "type": "String", "unique": true},
      {"name": "created_at", "type": "DateTime"}
    ]
  },
  "output_dir": "./models"
}
```

## Available Component Templates

### Frontend Components
- `react-component`: React functional component
- `vue-component`: Vue.js component
- `angular-component`: Angular component
- `svelte-component`: Svelte component

### Backend Components
- `express-route`: Express.js route handler
- `django-view`: Django view function
- `fastapi-router`: FastAPI router
- `graphql-resolver`: GraphQL resolver

### Database Components
- `sql-table`: SQL table creation script
- `mongoose-model`: MongoDB Mongoose model
- `django-model`: Django database model
- `typeorm-entity`: TypeORM entity

### Infrastructure Components
- `docker-service`: Docker service configuration
- `kubernetes-deployment`: K8s deployment YAML
- `terraform-module`: Terraform infrastructure module
- `github-action`: GitHub Actions workflow

## Generated Files

Components include:
- Main implementation file
- Type definitions (if applicable)
- Unit tests
- Documentation
- Example usage

## Related Commands

- `generateProject`: Generate complete project structures
- `generateDiagram`: Create component architecture diagrams
- `renderPrompt`: Generate component documentation