# mcp-analysis-prompt

Generate analysis prompts for code review, debugging, or system analysis using MCP prompts

## Usage

```bash
mcp-prompts apply_prompt mcp-analysis-prompt \
  --analysis_type "code_review" \
  --target_code "Code to analyze" \
  --focus_areas "performance,security,maintainability" \
  --context "Production system" \
  --urgency "medium" \
  --include_recommendations true
```

## Description

Uses the MCP prompts system to generate comprehensive analysis prompts for code review, debugging, or system analysis. The template focuses on specific areas and provides structured analysis requirements.

## Parameters

- **analysis_type**: Type of analysis (code_review, debugging, system_analysis)
- **target_code**: Code or system to analyze
- **focus_areas**: Comma-separated list of focus areas (performance, security, maintainability, etc.)
- **context**: System context (Production, Development, Testing)
- **urgency**: Urgency level (low, medium, high, critical)
- **include_recommendations**: Whether to include improvement recommendations (true/false)

## Examples

### Code Review Analysis
```bash
mcp-prompts apply_prompt mcp-analysis-prompt \
  --analysis_type "code_review" \
  --target_code "Python API endpoint" \
  --focus_areas "security,performance,maintainability" \
  --context "Production system" \
  --urgency "high" \
  --include_recommendations true
```

### System Analysis
```bash
mcp-prompts apply_prompt mcp-analysis-prompt \
  --analysis_type "system_analysis" \
  --target_code "Microservices architecture" \
  --focus_areas "scalability,reliability,monitoring" \
  --context "Production system" \
  --urgency "medium" \
  --include_recommendations true
```

### Debugging Analysis
```bash
mcp-prompts apply_prompt mcp-analysis-prompt \
  --analysis_type "debugging" \
  --target_code "Failing authentication service" \
  --focus_areas "error_handling,logging,performance" \
  --context "Production system" \
  --urgency "critical" \
  --include_recommendations true
```

## Related Commands

- `mcp-code-generator`: Code generation
- `mcp-debugging-prompt`: Debugging assistance
- `mcp-architecture-prompt`: Architecture design