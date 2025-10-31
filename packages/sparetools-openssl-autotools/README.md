# sparetools-openssl-autotools

Experimental OpenSSL recipe showcasing the Autotools toolchain integration in
Conan 2.x. Retained for comparison and migration testing; production builds
should prefer the unified `sparetools-openssl` package plus the
`autotools-*` profiles published in `sparetools-openssl-tools`.

## Status

- **Lifecycle:** Experimental / reference implementation
- **Use cases:** Regression testing, documentation of Autotools integration
- **Production builds:** Use `sparetools-openssl` instead

## Local Testing

```bash
cd packages/sparetools-openssl-autotools
conan create . --version=3.3.2 --build=missing
```

## Related References

- `packages/sparetools-openssl` – unified package for daily use
- `packages/sparetools-openssl-tools/openssl_tools/profiles/` – Autotools
  profiles aligning with the unified recipe

