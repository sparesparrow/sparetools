# sparetools-cpython

Prebuilt CPython 3.12.7 for OpenSSL DevOps ecosystem.

## Features

- Optimized build (LTO, PGO)
- OpenSSL support
- Zero dependencies
- Works with sparetools-base utilities

## Build
From source (already built)cd ~/.openssl-bootstrap/Python-3.12.7
make install DESTDIR=/tmp/cpython-3.12.7-stagingPackagecd packages/sparetools-cpython
conan create . --version=3.12.7
## Install
conan install --requires=sparetools-cpython/3.12.7 --deployer=full_deploy
source full_deploy/host/sparetools-cpython/3.12.7/*/activate.sh
