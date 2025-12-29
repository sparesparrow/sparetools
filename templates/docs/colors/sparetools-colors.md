# SpareTools Mermaid Color Scheme

## Color Palette

| Component Type | Fill Color | Stroke Color | Text Color | Usage |
|---------------|------------|--------------|------------|-------|
| Schema Layer | #2196F3 | #1565C0 | #fff | BPM schemas, protocol definitions |
| Provider Layer | #FF9800 | #E65100 | #fff | ESP32 firmware, hardware providers |
| Consumer Layer | #9C27B0 | #6A1B9A | #fff | Android apps, consumers |
| Tooling Layer | #FFC107 | #F57C00 | #000 | sparetools, shared utilities |
| Success/Production | #4CAF50 | #2E7D32 | #fff | Final states, production deployments |
| Utilities/Bootstrap | #607D8B | #37474F | #fff | Bootstrap, utilities |
| Security/Errors | #E91E63 / #F44336 | #880E4F / #B71C1C | #fff | Security scanning, blocking states |

## Usage Example

```mermaid
graph TB
    SCHEMA[Schema Package]
    PROVIDER[Provider Package]
    CONSUMER[Consumer Package]
    
    style SCHEMA fill:#2196F3,stroke:#1565C0,color:#fff
    style PROVIDER fill:#FF9800,stroke:#E65100,color:#fff
    style CONSUMER fill:#9C27B0,stroke:#6A1B9A,color:#fff
```

## Python Helper Function

```python
def get_sparetools_color(layer_type: str) -> dict:
    """Get SpareTools color scheme for a layer type.
    
    Args:
        layer_type: One of 'schema', 'provider', 'consumer', 'tooling', 
                   'success', 'utilities', 'security', 'error'
    
    Returns:
        Dict with 'fill', 'stroke', and 'color' keys
    """
    colors = {
        'schema': {'fill': '#2196F3', 'stroke': '#1565C0', 'color': '#fff'},
        'provider': {'fill': '#FF9800', 'stroke': '#E65100', 'color': '#fff'},
        'consumer': {'fill': '#9C27B0', 'stroke': '#6A1B9A', 'color': '#fff'},
        'tooling': {'fill': '#FFC107', 'stroke': '#F57C00', 'color': '#000'},
        'success': {'fill': '#4CAF50', 'stroke': '#2E7D32', 'color': '#fff'},
        'utilities': {'fill': '#607D8B', 'stroke': '#37474F', 'color': '#fff'},
        'security': {'fill': '#E91E63', 'stroke': '#880E4F', 'color': '#fff'},
        'error': {'fill': '#F44336', 'stroke': '#B71C1C', 'color': '#fff'},
    }
    return colors.get(layer_type.lower(), colors['utilities'])
```

## Mermaid Style Syntax

To apply SpareTools colors in Mermaid diagrams:

```mermaid
graph TD
    A[Schema Component]
    B[Provider Component]
    C[Consumer Component]
    
    style A fill:#2196F3,stroke:#1565C0,color:#fff
    style B fill:#FF9800,stroke:#E65100,color:#fff
    style C fill:#9C27B0,stroke:#6A1B9A,color:#fff
```

## Integration with Mermaid Generator

The `MermaidGenerator` class includes an `apply_sparetools_colors()` method that automatically applies these colors based on component types detected in your diagram.
