# sparetools-openssl-cmake

Experimental OpenSSL recipe that prototypes a CMake-first build flow. The
package exists for R&D and comparison against the Perl Configure baseline.
Expect in-flight changes while the team evaluates upstream parity for newer
OpenSSL releases.

## Status

- **Lifecycle:** Experimental / proof-of-concept
- **Intended usage:** Matrix experimentation, CI smoke testing
- **Production builds:** Use `sparetools-openssl` with CMake profiles instead

## Local Testing

```bash
cd packages/sparetools-openssl-cmake
conan create . --version=3.3.2 --build=missing
```

## Related References

- `packages/sparetools-openssl` – canonical OpenSSL package
- `packages/sparetools-openssl-tools/openssl_tools/profiles/` – CMake profile
  definitions leveraged by the unified recipe

