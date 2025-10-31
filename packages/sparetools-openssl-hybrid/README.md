# sparetools-openssl-hybrid

Legacy package used to prototype the hybrid Perl + Python configuration flow
for OpenSSL. The functionality has since been folded into
`sparetools-openssl-tools` and the unified `sparetools-openssl` recipe, but the
package remains available for reproducibility and historical reference.

## Status

- **Lifecycle:** Legacy / compatibility
- **Primary purpose:** Validate the hybrid `configure.py` implementation during
  the migration from Perl Configure
- **Current recommendation:** Use `sparetools-openssl` with the `hybrid-*`
  profiles provided by `sparetools-openssl-tools`

## Local Testing

```bash
cd packages/sparetools-openssl-hybrid
conan create . --version=3.3.2 --build=missing
```

## Related References

- `packages/sparetools-openssl-tools/openssl_tools/openssl/hybrid_builder.py`
- `packages/sparetools-openssl` – active recipe consuming the hybrid builder

