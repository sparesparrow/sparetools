# OpenSSL Profile Axes

This directory defines the canonical build matrix for OpenSSL within the SpareTools
ecosystem. The intent is to consolidate all historical "variant" packages into a
single Conan recipe (`sparetools-openssl`) while expressing behavioural
differences through structured build profiles.

## Terminology

* **Variant** – which build recipe or flow to exercise (Perl Configure,
  CMake, Autotools, Hybrid).
* **OpenSSL Release** – upstream version under test (e.g. 3.3.2 for
  shipping, 3.6.0 for forward-looking coverage).
* **Operating System / Architecture** – execution environment for the build.
* **Compiler** – primary toolchain (family and major version bucket).
* **Linkage** – shared vs. static libraries.
* **Optimization Tier** – bundle of optimisation / diagnostics flags tuned
  for release, balanced CI, or debug scenarios.
* **FIPS Mode** – whether FIPS support is enabled.

Refer to `axes.yaml` for the machine-readable definition used by tooling and CI
generators. Each axis value carries metadata (e.g. GitHub Actions runner) so that
automation can derive the correct environment without duplicating logic.

## Naming Convention

Profiles use the template declared in `axes.yaml` and collapse to a
dash-delimited identifier, for example:

```
perl-lin-x86_64-gcc-shared-fips
cmake-win-x86_64-msvc-static-std
hybrid-mac-arm64-clang-shared-std
```

Metadata-only axes (OpenSSL release, optimisation tier) remain attached to
the profile definition and are surfaced to orchestration tooling without
lengthening the human-readable identifier. This keeps file names stable while
still enabling matrix expansion for new releases.

## Next Steps

1. Generate Conan 2 profile files for each supported combination under this
   directory (see `profiles-implement` task).
2. Update automation (`build_matrix.py`, GitHub Actions) to consume the new
   matrix data instead of ad-hoc lists.
3. Remove legacy duplicate packages once the unified recipe + profiles cover
   all required scenarios.
