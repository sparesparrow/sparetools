# Package README Template

Use this template when authoring or updating package-level README files in the
`packages/` directory.

```markdown
# <package-name>

<One or two sentences explaining the role of the package.>

## Key Capabilities

- <Capability 1>
- <Capability 2>
- <Capability 3>

## Conan Usage

```bash
# Optional: build locally
cd packages/<package-name>
conan create . --version=<version> [--build=missing]

# Consume from Cloudsmith
conan install --requires=<package-name>/<version>@ [additional flags]
```

## Development Notes

- <Prerequisites or environment notes>
- <Links to important scripts or modules>

## Related References

- <Docs or companion packages>
```

