# mcp-architecture-prompt

Generate architecture design prompts for system design and planning using MCP prompts

## Usage

```bash
mcp-prompts apply_prompt mcp-architecture-prompt \
  --system_type "web application" \
  --requirements "Basic CRUD operations" \
  --scale "medium" \
  --technology_stack "Python, React, PostgreSQL" \
  --constraints "Budget and time limitations" \
  --include_diagrams true \
  --include_security true
```

## Description

Uses the MCP prompts system to generate comprehensive architecture design prompts for system design and planning. The template covers scalability, performance, reliability, security, and maintainability considerations with visual documentation support.

## Parameters

- **system_type**: Type of system (web application, microservices, mobile app, etc.)
- **requirements**: System requirements and specifications
- **scale**: Scale (small, medium, large, enterprise)
- **technology_stack**: Technology stack (Python, React, PostgreSQL, etc.)
- **constraints**: Constraints (budget, time, resources, etc.)
- **include_diagrams**: Whether to include visual documentation (true/false)
- **include_security**: Whether to include security considerations (true/false)

## Examples

### Web Application
```bash
mcp-prompts apply_prompt mcp-architecture-prompt \
  --system_type "web application" \
  --requirements "E-commerce platform with user management and payment processing" \
  --scale "large" \
  --technology_stack "Python, React, PostgreSQL, Redis, Docker" \
  --constraints "High availability and scalability requirements" \
  --include_diagrams true \
  --include_security true
```

### Microservices Architecture
```bash
mcp-prompts apply_prompt mcp-architecture-prompt \
  --system_type "microservices" \
  --requirements "Distributed system with API gateway and service mesh" \
  --scale "enterprise" \
  --technology_stack "Kubernetes, Docker, gRPC, PostgreSQL, Redis" \
  --constraints "Multi-cloud deployment and compliance requirements" \
  --include_diagrams true \
  --include_security true
```

### Mobile Application
```bash
mcp-prompts apply_prompt mcp-architecture-prompt \
  --system_type "mobile application" \
  --requirements "Cross-platform app with offline capabilities" \
  --scale "medium" \
  --technology_stack "React Native, Node.js, MongoDB, AWS" \
  --constraints "Limited development resources and tight timeline" \
  --include_diagrams true \
  --include_security true
```

## Related Commands

- `mcp-code-generator`: Code generation
- `mcp-analysis-prompt`: System analysis
- `mcp-documentation-prompt`: Architecture documentation